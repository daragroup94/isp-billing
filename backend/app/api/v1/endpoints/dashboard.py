from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.customer import Customer
from app.models.package import Package
from app.models.invoice import Invoice
from app.models.payment import Payment

router = APIRouter()


@router.get("/stats", response_model=dict)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get overall dashboard statistics
    """
    # Customer stats
    total_customers = db.query(Customer).count()
    active_customers = db.query(Customer).filter(Customer.status == "active").count()
    suspended_customers = db.query(Customer).filter(Customer.status == "suspended").count()
    
    # Invoice stats
    total_invoices = db.query(Invoice).count()
    pending_invoices = db.query(Invoice).filter(Invoice.status == "pending").count()
    paid_invoices = db.query(Invoice).filter(Invoice.status == "paid").count()
    overdue_invoices = db.query(Invoice).filter(Invoice.status == "overdue").count()
    
    # Payment stats
    total_payments = db.query(Payment).count()
    pending_payments = db.query(Payment).filter(Payment.status == "pending").count()
    verified_payments = db.query(Payment).filter(Payment.status == "verified").count()
    
    # Revenue stats
    total_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status == "paid"
    ).scalar() or 0
    
    pending_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status.in_(["pending", "partial", "overdue"])
    ).scalar() or 0
    
    # This month revenue
    first_day_of_month = date.today().replace(day=1)
    this_month_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status == "paid",
        Invoice.paid_at >= first_day_of_month
    ).scalar() or 0
    
    # Last month revenue
    last_month_first_day = (first_day_of_month - timedelta(days=1)).replace(day=1)
    last_month_revenue = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status == "paid",
        Invoice.paid_at >= last_month_first_day,
        Invoice.paid_at < first_day_of_month
    ).scalar() or 0
    
    return {
        "customers": {
            "total": total_customers,
            "active": active_customers,
            "suspended": suspended_customers,
            "growth_rate": 0  # TODO: Calculate growth rate
        },
        "invoices": {
            "total": total_invoices,
            "pending": pending_invoices,
            "paid": paid_invoices,
            "overdue": overdue_invoices
        },
        "payments": {
            "total": total_payments,
            "pending": pending_payments,
            "verified": verified_payments
        },
        "revenue": {
            "total": float(total_revenue),
            "pending": float(pending_revenue),
            "this_month": float(this_month_revenue),
            "last_month": float(last_month_revenue),
            "growth_percentage": round(
                ((this_month_revenue - last_month_revenue) / last_month_revenue * 100) 
                if last_month_revenue > 0 else 0, 2
            )
        }
    }


@router.get("/revenue-chart", response_model=dict)
def get_revenue_chart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    months: int = 12
) -> Any:
    """
    Get revenue chart data for last N months
    """
    today = date.today()
    chart_data = []
    
    for i in range(months - 1, -1, -1):
        month_date = today - relativedelta(months=i)
        first_day = month_date.replace(day=1)
        last_day = (first_day + relativedelta(months=1)) - timedelta(days=1)
        
        # Get revenue for this month
        revenue = db.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status == "paid",
            Invoice.paid_at >= first_day,
            Invoice.paid_at <= last_day
        ).scalar() or 0
        
        # Get invoice count for this month
        invoice_count = db.query(func.count(Invoice.id)).filter(
            Invoice.status == "paid",
            Invoice.paid_at >= first_day,
            Invoice.paid_at <= last_day
        ).scalar() or 0
        
        chart_data.append({
            "month": first_day.strftime("%Y-%m"),
            "month_name": first_day.strftime("%B %Y"),
            "revenue": float(revenue),
            "invoice_count": invoice_count
        })
    
    return {
        "data": chart_data,
        "total_revenue": sum(item["revenue"] for item in chart_data),
        "average_revenue": sum(item["revenue"] for item in chart_data) / months if months > 0 else 0
    }


@router.get("/customer-growth", response_model=dict)
def get_customer_growth(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    months: int = 12
) -> Any:
    """
    Get customer growth chart data for last N months
    """
    today = date.today()
    chart_data = []
    
    for i in range(months - 1, -1, -1):
        month_date = today - relativedelta(months=i)
        first_day = month_date.replace(day=1)
        last_day = (first_day + relativedelta(months=1)) - timedelta(days=1)
        
        # Get new customers this month
        new_customers = db.query(func.count(Customer.id)).filter(
            Customer.created_at >= first_day,
            Customer.created_at <= last_day
        ).scalar() or 0
        
        # Get total customers up to end of this month
        total_customers = db.query(func.count(Customer.id)).filter(
            Customer.created_at <= last_day
        ).scalar() or 0
        
        chart_data.append({
            "month": first_day.strftime("%Y-%m"),
            "month_name": first_day.strftime("%B %Y"),
            "new_customers": new_customers,
            "total_customers": total_customers
        })
    
    return {
        "data": chart_data
    }


@router.get("/package-distribution", response_model=dict)
def get_package_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get customer distribution by package
    """
    # Get packages with customer count
    packages = db.query(
        Package.id,
        Package.name,
        Package.code,
        func.count(Customer.id).label('customer_count')
    ).outerjoin(
        Customer, Package.id == Customer.package_id
    ).filter(
        Customer.status == "active"
    ).group_by(Package.id).all()
    
    total_customers = sum(p.customer_count for p in packages)
    
    distribution = []
    for package in packages:
        distribution.append({
            "package_id": package.id,
            "package_name": package.name,
            "package_code": package.code,
            "customer_count": package.customer_count,
            "percentage": round((package.customer_count / total_customers * 100) if total_customers > 0 else 0, 2)
        })
    
    return {
        "total_customers": total_customers,
        "distribution": distribution
    }


@router.get("/recent-activities", response_model=dict)
def get_recent_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 10
) -> Any:
    """
    Get recent activities (customers, invoices, payments)
    """
    # Recent customers
    recent_customers = db.query(Customer).order_by(
        Customer.created_at.desc()
    ).limit(limit).all()
    
    # Recent invoices
    recent_invoices = db.query(Invoice).order_by(
        Invoice.created_at.desc()
    ).limit(limit).all()
    
    # Recent payments
    recent_payments = db.query(Payment).order_by(
        Payment.created_at.desc()
    ).limit(limit).all()
    
    return {
        "recent_customers": [
            {
                "id": c.id,
                "customer_code": c.customer_code,
                "full_name": c.full_name,
                "status": c.status,
                "created_at": c.created_at.isoformat()
            } for c in recent_customers
        ],
        "recent_invoices": [
            {
                "id": i.id,
                "invoice_number": i.invoice_number,
                "customer_id": i.customer_id,
                "total_amount": float(i.total_amount),
                "status": i.status,
                "created_at": i.created_at.isoformat()
            } for i in recent_invoices
        ],
        "recent_payments": [
            {
                "id": p.id,
                "payment_number": p.payment_number,
                "customer_id": p.customer_id,
                "amount": float(p.amount),
                "status": p.status,
                "created_at": p.created_at.isoformat()
            } for p in recent_payments
        ]
    }


@router.get("/overdue-summary", response_model=dict)
def get_overdue_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get summary of overdue invoices
    """
    today = date.today()
    
    # Get overdue invoices grouped by age
    overdue_1_7 = db.query(func.count(Invoice.id), func.sum(Invoice.total_amount)).filter(
        Invoice.status.in_(["pending", "partial", "overdue"]),
        Invoice.due_date < today,
        Invoice.due_date >= today - timedelta(days=7)
    ).first()
    
    overdue_8_30 = db.query(func.count(Invoice.id), func.sum(Invoice.total_amount)).filter(
        Invoice.status.in_(["pending", "partial", "overdue"]),
        Invoice.due_date < today - timedelta(days=7),
        Invoice.due_date >= today - timedelta(days=30)
    ).first()
    
    overdue_30_plus = db.query(func.count(Invoice.id), func.sum(Invoice.total_amount)).filter(
        Invoice.status.in_(["pending", "partial", "overdue"]),
        Invoice.due_date < today - timedelta(days=30)
    ).first()
    
    return {
        "overdue_1_7_days": {
            "count": overdue_1_7[0] or 0,
            "total_amount": float(overdue_1_7[1] or 0)
        },
        "overdue_8_30_days": {
            "count": overdue_8_30[0] or 0,
            "total_amount": float(overdue_8_30[1] or 0)
        },
        "overdue_30_plus_days": {
            "count": overdue_30_plus[0] or 0,
            "total_amount": float(overdue_30_plus[1] or 0)
        },
        "total_overdue": {
            "count": (overdue_1_7[0] or 0) + (overdue_8_30[0] or 0) + (overdue_30_plus[0] or 0),
            "total_amount": float((overdue_1_7[1] or 0) + (overdue_8_30[1] or 0) + (overdue_30_plus[1] or 0))
        }
    }
