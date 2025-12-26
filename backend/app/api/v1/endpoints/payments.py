from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas import payment as payment_schema
from app.services.payment import PaymentService

router = APIRouter()


@router.get("/", response_model=List[payment_schema.PaymentInList])
def get_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    invoice_id: Optional[int] = Query(None, description="Filter by invoice ID"),
    status: Optional[str] = Query(None, description="Filter by status: pending, verified, rejected, cancelled"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method")
) -> Any:
    """
    Get payments list with filters
    """
    payments = PaymentService.get_payments(
        db=db,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        invoice_id=invoice_id,
        status=status,
        payment_method=payment_method
    )
    return payments


@router.get("/count", response_model=dict)
def get_payments_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get payments count by status
    """
    from app.models.payment import Payment
    
    total = db.query(Payment).count()
    pending = db.query(Payment).filter(Payment.status == "pending").count()
    verified = db.query(Payment).filter(Payment.status == "verified").count()
    rejected = db.query(Payment).filter(Payment.status == "rejected").count()
    cancelled = db.query(Payment).filter(Payment.status == "cancelled").count()
    
    # Calculate total amounts
    from sqlalchemy import func
    total_amount = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "verified"
    ).scalar() or 0
    
    pending_amount = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "pending"
    ).scalar() or 0
    
    return {
        "total": total,
        "pending": pending,
        "verified": verified,
        "rejected": rejected,
        "cancelled": cancelled,
        "total_verified_amount": float(total_amount),
        "pending_amount": float(pending_amount)
    }


@router.get("/pending", response_model=List[payment_schema.PaymentInList])
def get_pending_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    """
    Get pending payments that need verification
    """
    from app.models.payment import Payment
    
    payments = db.query(Payment).filter(
        Payment.status == "pending"
    ).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    return payments


@router.post("/", response_model=payment_schema.Payment, status_code=status.HTTP_201_CREATED)
def create_payment(
    *,
    db: Session = Depends(get_db),
    payment_in: payment_schema.PaymentCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new payment
    """
    payment = PaymentService.create_payment(db, payment_in)
    return payment


@router.get("/{payment_id}", response_model=payment_schema.Payment)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get payment by ID
    """
    payment = PaymentService.get_payment_by_id(db, payment_id)
    return payment


@router.get("/number/{payment_number}", response_model=payment_schema.Payment)
def get_payment_by_number(
    payment_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get payment by payment number
    """
    payment = PaymentService.get_payment_by_number(db, payment_number)
    return payment


@router.put("/{payment_id}", response_model=payment_schema.Payment)
def update_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    payment_in: payment_schema.PaymentUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update payment
    """
    payment = PaymentService.update_payment(db, payment_id, payment_in)
    return payment


@router.post("/{payment_id}/verify", response_model=payment_schema.Payment)
def verify_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    verify_data: payment_schema.PaymentVerify,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Verify payment (approve)
    """
    payment = PaymentService.verify_payment(
        db=db,
        payment_id=payment_id,
        verified_by=current_user.id
    )
    
    # Update admin notes if provided
    if verify_data.admin_notes:
        payment.admin_notes = verify_data.admin_notes
        db.commit()
        db.refresh(payment)
    
    return payment


@router.post("/{payment_id}/reject", response_model=payment_schema.Payment)
def reject_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    reject_data: payment_schema.PaymentReject,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Reject payment
    """
    payment = PaymentService.reject_payment(
        db=db,
        payment_id=payment_id,
        verified_by=current_user.id,
        rejection_reason=reject_data.rejection_reason
    )
    
    # Update admin notes if provided
    if reject_data.admin_notes:
        payment.admin_notes = reject_data.admin_notes
        db.commit()
        db.refresh(payment)
    
    return payment


@router.post("/{payment_id}/cancel", response_model=payment_schema.Payment)
def cancel_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Cancel payment
    """
    payment = PaymentService.cancel_payment(db, payment_id)
    return payment


@router.get("/methods/stats", response_model=dict)
def get_payment_methods_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get payment statistics by payment method
    """
    from app.models.payment import Payment
    from sqlalchemy import func
    
    stats = db.query(
        Payment.payment_method,
        func.count(Payment.id).label('count'),
        func.sum(Payment.amount).label('total_amount')
    ).filter(
        Payment.status == "verified"
    ).group_by(Payment.payment_method).all()
    
    result = {}
    for stat in stats:
        result[stat.payment_method] = {
            "count": stat.count,
            "total_amount": float(stat.total_amount or 0)
        }
    
    return result
