from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas import invoice as invoice_schema
from app.services.invoice import InvoiceService

router = APIRouter()


@router.get("/", response_model=List[invoice_schema.InvoiceInList])
def get_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by status: pending, paid, partial, overdue, cancelled"),
    month: Optional[str] = Query(None, description="Filter by billing month (YYYY-MM)")
) -> Any:
    """
    Get invoices list with filters
    """
    invoices = InvoiceService.get_invoices(
        db=db,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        status=status,
        month=month
    )
    return invoices


@router.get("/count", response_model=dict)
def get_invoices_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get invoices count by status
    """
    from app.models.invoice import Invoice
    
    total = db.query(Invoice).count()
    pending = db.query(Invoice).filter(Invoice.status == "pending").count()
    paid = db.query(Invoice).filter(Invoice.status == "paid").count()
    partial = db.query(Invoice).filter(Invoice.status == "partial").count()
    overdue = db.query(Invoice).filter(Invoice.status == "overdue").count()
    cancelled = db.query(Invoice).filter(Invoice.status == "cancelled").count()
    
    # Calculate total amounts
    from sqlalchemy import func
    total_amount = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status.in_(["pending", "partial", "overdue"])
    ).scalar() or 0
    
    paid_amount = db.query(func.sum(Invoice.total_amount)).filter(
        Invoice.status == "paid"
    ).scalar() or 0
    
    return {
        "total": total,
        "pending": pending,
        "paid": paid,
        "partial": partial,
        "overdue": overdue,
        "cancelled": cancelled,
        "total_outstanding": float(total_amount),
        "total_paid": float(paid_amount)
    }


@router.get("/overdue", response_model=List[invoice_schema.InvoiceInList])
def get_overdue_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """
    Get overdue invoices
    """
    from app.models.invoice import Invoice
    
    invoices = db.query(Invoice).filter(
        Invoice.status.in_(["pending", "partial"]),
        Invoice.due_date < date.today()
    ).order_by(Invoice.due_date.asc()).offset(skip).limit(limit).all()
    
    return invoices


@router.post("/", response_model=invoice_schema.Invoice, status_code=status.HTTP_201_CREATED)
def create_invoice(
    *,
    db: Session = Depends(get_db),
    invoice_in: invoice_schema.InvoiceCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new invoice manually
    """
    invoice = InvoiceService.create_invoice(db, invoice_in)
    return invoice


@router.post("/generate", response_model=invoice_schema.Invoice, status_code=status.HTTP_201_CREATED)
def generate_invoice(
    *,
    db: Session = Depends(get_db),
    invoice_gen: invoice_schema.InvoiceGenerate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Generate monthly invoice for a customer
    """
    invoice = InvoiceService.generate_monthly_invoice(
        db=db,
        customer_id=invoice_gen.customer_id,
        billing_month=invoice_gen.billing_month
    )
    return invoice


@router.post("/generate-batch", response_model=dict)
def generate_batch_invoices(
    *,
    db: Session = Depends(get_db),
    billing_month: date,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Generate invoices for all active customers for a specific month
    """
    from app.models.customer import Customer
    
    # Get all active customers
    customers = db.query(Customer).filter(
        Customer.status == "active",
        Customer.package_id.isnot(None)
    ).all()
    
    success_count = 0
    error_count = 0
    errors = []
    
    for customer in customers:
        try:
            InvoiceService.generate_monthly_invoice(
                db=db,
                customer_id=customer.id,
                billing_month=billing_month
            )
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append({
                "customer_id": customer.id,
                "customer_name": customer.full_name,
                "error": str(e)
            })
    
    return {
        "total_customers": len(customers),
        "success": success_count,
        "errors": error_count,
        "error_details": errors
    }


@router.get("/{invoice_id}", response_model=invoice_schema.Invoice)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get invoice by ID
    """
    invoice = InvoiceService.get_invoice_by_id(db, invoice_id)
    return invoice


@router.get("/number/{invoice_number}", response_model=invoice_schema.Invoice)
def get_invoice_by_number(
    invoice_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get invoice by invoice number
    """
    invoice = InvoiceService.get_invoice_by_number(db, invoice_number)
    return invoice


@router.put("/{invoice_id}", response_model=invoice_schema.Invoice)
def update_invoice(
    *,
    db: Session = Depends(get_db),
    invoice_id: int,
    invoice_in: invoice_schema.InvoiceUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update invoice
    """
    invoice = InvoiceService.update_invoice(db, invoice_id, invoice_in)
    return invoice


@router.post("/{invoice_id}/cancel", response_model=invoice_schema.Invoice)
def cancel_invoice(
    *,
    db: Session = Depends(get_db),
    invoice_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Cancel invoice
    """
    invoice = InvoiceService.cancel_invoice(db, invoice_id)
    return invoice


@router.post("/{invoice_id}/mark-paid", response_model=invoice_schema.Invoice)
def mark_invoice_as_paid(
    *,
    db: Session = Depends(get_db),
    invoice_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Mark invoice as paid
    """
    invoice = InvoiceService.mark_as_paid(db, invoice_id)
    return invoice


@router.post("/check-overdue", response_model=dict)
def check_overdue_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Check and update overdue invoices
    """
    overdue_invoices = InvoiceService.check_overdue_invoices(db)
    
    return {
        "message": "Overdue invoices checked and updated",
        "overdue_count": len(overdue_invoices),
        "invoice_ids": [inv.id for inv in overdue_invoices]
    }
