from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.payment import Payment
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.core.config import settings


class InvoiceService:
    """
    Invoice service for business logic
    """
    
    @staticmethod
    def generate_invoice_number(db: Session, invoice_date: date) -> str:
        """Generate unique invoice number"""
        # Format: INV-YYYY-MM-XXX
        year_month = invoice_date.strftime("%Y-%m")
        prefix = f"INV-{year_month}"
        
        # Get last invoice for this month
        last_invoice = db.query(Invoice).filter(
            Invoice.invoice_number.like(f"{prefix}%")
        ).order_by(Invoice.id.desc()).first()
        
        if last_invoice:
            try:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:03d}"
    
    @staticmethod
    def get_invoices(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        month: Optional[str] = None
    ) -> List[Invoice]:
        """Get invoices list with filters"""
        query = db.query(Invoice)
        
        if customer_id:
            query = query.filter(Invoice.customer_id == customer_id)
        
        if status:
            query = query.filter(Invoice.status == status)
        
        if month:
            query = query.filter(Invoice.billing_period == month)
        
        query = query.order_by(Invoice.created_at.desc())
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_invoice_by_id(db: Session, invoice_id: int) -> Invoice:
        """Get invoice by ID"""
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return invoice
    
    @staticmethod
    def get_invoice_by_number(db: Session, invoice_number: str) -> Invoice:
        """Get invoice by number"""
        invoice = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return invoice
    
    @staticmethod
    def create_invoice(db: Session, invoice_in: InvoiceCreate) -> Invoice:
        """Create new invoice manually"""
        # Check if customer exists
        customer = db.query(Customer).filter(Customer.id == invoice_in.customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Generate invoice number
        invoice_number = InvoiceService.generate_invoice_number(db, invoice_in.invoice_date)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            **invoice_in.model_dump()
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        return invoice
    
    @staticmethod
    def generate_monthly_invoice(db: Session, customer_id: int, billing_month: date) -> Invoice:
        """Generate monthly invoice for a customer"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        if not customer.package:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer has no package assigned"
            )
        
        # Check if invoice already exists for this month
        billing_period = billing_month.strftime("%Y-%m")
        existing = db.query(Invoice).filter(
            Invoice.customer_id == customer_id,
            Invoice.billing_period == billing_period
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invoice for {billing_period} already exists"
            )
        
        # Calculate dates
        invoice_date = date(billing_month.year, billing_month.month, customer.billing_day)
        period_start = date(billing_month.year, billing_month.month, 1)
        period_end = period_start + relativedelta(months=1) - timedelta(days=1)
        due_date = invoice_date + timedelta(days=settings.LATE_PAYMENT_DAYS)
        
        # Calculate amounts
        subtotal = Decimal(str(customer.package.price))
        discount = Decimal('0')
        late_fee = Decimal('0')
        tax = Decimal('0')
        total_amount = subtotal - discount + late_fee + tax
        
        # Generate invoice number
        invoice_number = InvoiceService.generate_invoice_number(db, invoice_date)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=customer_id,
            billing_period=billing_period,
            period_start=period_start,
            period_end=period_end,
            invoice_date=invoice_date,
            due_date=due_date,
            subtotal=subtotal,
            discount=discount,
            late_fee=late_fee,
            tax=tax,
            total_amount=total_amount,
            paid_amount=Decimal('0'),
            status="pending",
            description=f"Internet Service - {customer.package.name}",
            items=f'{{"package": "{customer.package.name}", "price": {customer.package.price}}}'
        )
        
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        
        return invoice
    
    @staticmethod
    def update_invoice(
        db: Session,
        invoice_id: int,
        invoice_in: InvoiceUpdate
    ) -> Invoice:
        """Update invoice"""
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id)
        
        # Don't allow updating paid invoices
        if invoice.status == "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update paid invoice"
            )
        
        # Update fields
        update_data = invoice_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(invoice, field, value)
        
        db.commit()
        db.refresh(invoice)
        
        return invoice
    
    @staticmethod
    def cancel_invoice(db: Session, invoice_id: int) -> Invoice:
        """Cancel invoice"""
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id)
        
        if invoice.status == "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel paid invoice"
            )
        
        if invoice.paid_amount > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel invoice with partial payment"
            )
        
        invoice.status = "cancelled"
        
        db.commit()
        db.refresh(invoice)
        
        return invoice
    
    @staticmethod
    def mark_as_paid(db: Session, invoice_id: int, paid_amount: Optional[Decimal] = None) -> Invoice:
        """Mark invoice as paid"""
        invoice = InvoiceService.get_invoice_by_id(db, invoice_id)
        
        if paid_amount:
            invoice.paid_amount = paid_amount
        else:
            invoice.paid_amount = invoice.total_amount
        
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = "paid"
            invoice.paid_at = datetime.utcnow()
        elif invoice.paid_amount > 0:
            invoice.status = "partial"
        
        db.commit()
        db.refresh(invoice)
        
        return invoice
    
    @staticmethod
    def check_overdue_invoices(db: Session) -> List[Invoice]:
        """Check and update overdue invoices"""
        today = date.today()
        
        overdue_invoices = db.query(Invoice).filter(
            Invoice.status.in_(["pending", "partial"]),
            Invoice.due_date < today
        ).all()
        
        for invoice in overdue_invoices:
            invoice.status = "overdue"
            
            # Add late fee if not already added
            if invoice.late_fee == 0:
                invoice.late_fee = Decimal(str(settings.LATE_PAYMENT_FEE))
                invoice.total_amount = invoice.subtotal - invoice.discount + invoice.late_fee + invoice.tax
        
        db.commit()
        
        return overdue_invoices
