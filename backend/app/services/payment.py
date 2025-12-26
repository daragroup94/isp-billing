from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, date
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.schemas.payment import PaymentCreate, PaymentUpdate
from app.services.invoice import InvoiceService


class PaymentService:
    """
    Payment service for business logic
    """
    
    @staticmethod
    def generate_payment_number(db: Session, payment_date: date) -> str:
        """Generate unique payment number"""
        # Format: PAY-YYYY-MM-XXX
        year_month = payment_date.strftime("%Y-%m")
        prefix = f"PAY-{year_month}"
        
        # Get last payment for this month
        last_payment = db.query(Payment).filter(
            Payment.payment_number.like(f"{prefix}%")
        ).order_by(Payment.id.desc()).first()
        
        if last_payment:
            try:
                last_number = int(last_payment.payment_number.split('-')[-1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:03d}"
    
    @staticmethod
    def get_payments(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        customer_id: Optional[int] = None,
        invoice_id: Optional[int] = None,
        status: Optional[str] = None,
        payment_method: Optional[str] = None
    ) -> List[Payment]:
        """Get payments list with filters"""
        query = db.query(Payment)
        
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        
        if invoice_id:
            query = query.filter(Payment.invoice_id == invoice_id)
        
        if status:
            query = query.filter(Payment.status == status)
        
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        
        query = query.order_by(Payment.created_at.desc())
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_payment_by_id(db: Session, payment_id: int) -> Payment:
        """Get payment by ID"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment
    
    @staticmethod
    def get_payment_by_number(db: Session, payment_number: str) -> Payment:
        """Get payment by number"""
        payment = db.query(Payment).filter(Payment.payment_number == payment_number).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment
    
    @staticmethod
    def create_payment(db: Session, payment_in: PaymentCreate) -> Payment:
        """Create new payment"""
        # Check if customer exists
        customer = db.query(Customer).filter(Customer.id == payment_in.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Check if invoice exists (optional)
        if payment_in.invoice_id:
            invoice = db.query(Invoice).filter(Invoice.id == payment_in.invoice_id).first()
            if not invoice:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invoice not found"
                )
            
            # Check if invoice belongs to customer
            if invoice.customer_id != payment_in.customer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invoice does not belong to this customer"
                )
        
        # Generate payment number
        payment_number = PaymentService.generate_payment_number(db, payment_in.payment_date)
        
        # Create payment
        payment = Payment(
            payment_number=payment_number,
            **payment_in.model_dump(),
            status="pending"
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def update_payment(
        db: Session,
        payment_id: int,
        payment_in: PaymentUpdate
    ) -> Payment:
        """Update payment"""
        payment = PaymentService.get_payment_by_id(db, payment_id)
        
        # Don't allow updating verified payments
        if payment.status == "verified":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update verified payment"
            )
        
        # Update fields
        update_data = payment_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(payment, field, value)
        
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def verify_payment(
        db: Session,
        payment_id: int,
        verified_by: int
    ) -> Payment:
        """Verify payment"""
        payment = PaymentService.get_payment_by_id(db, payment_id)
        
        if payment.status == "verified":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already verified"
            )
        
        if payment.status == "rejected":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot verify rejected payment"
            )
        
        # Update payment status
        payment.status = "verified"
        payment.verified_by = verified_by
        payment.verified_at = datetime.utcnow()
        
        # Update invoice if exists
        if payment.invoice_id:
            invoice = db.query(Invoice).filter(Invoice.id == payment.invoice_id).first()
            if invoice:
                # Update paid amount
                invoice.paid_amount += payment.amount
                
                # Update invoice status
                if invoice.paid_amount >= invoice.total_amount:
                    invoice.status = "paid"
                    invoice.paid_at = datetime.utcnow()
                elif invoice.paid_amount > 0:
                    invoice.status = "partial"
        
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def reject_payment(
        db: Session,
        payment_id: int,
        verified_by: int,
        rejection_reason: str
    ) -> Payment:
        """Reject payment"""
        payment = PaymentService.get_payment_by_id(db, payment_id)
        
        if payment.status == "verified":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot reject verified payment"
            )
        
        # Update payment status
        payment.status = "rejected"
        payment.verified_by = verified_by
        payment.verified_at = datetime.utcnow()
        payment.rejection_reason = rejection_reason
        
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def cancel_payment(db: Session, payment_id: int) -> Payment:
        """Cancel payment"""
        payment = PaymentService.get_payment_by_id(db, payment_id)
        
        if payment.status == "verified":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel verified payment"
            )
        
        payment.status = "cancelled"
        
        db.commit()
        db.refresh(payment)
        
        return payment
