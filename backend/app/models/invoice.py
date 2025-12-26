from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Invoice(Base):
    """
    Invoice model - Tagihan pelanggan
    """
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Invoice Info
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "INV-2024-12-001"
    
    # Customer Reference
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer", back_populates="invoices")
    
    # Billing Period
    billing_period = Column(String(20), nullable=False)  # e.g., "2024-12" or "December 2024"
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Invoice Date
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    # Amounts
    subtotal = Column(Numeric(15, 2), nullable=False)  # Total sebelum diskon/denda
    discount = Column(Numeric(15, 2), default=0)  # Diskon
    late_fee = Column(Numeric(15, 2), default=0)  # Denda keterlambatan
    tax = Column(Numeric(15, 2), default=0)  # Pajak (jika ada)
    total_amount = Column(Numeric(15, 2), nullable=False)  # Total yang harus dibayar
    paid_amount = Column(Numeric(15, 2), default=0)  # Total yang sudah dibayar
    
    # Status
    status = Column(String(20), default="pending")  # pending, paid, partial, overdue, cancelled
    
    # Payment Date
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Description/Items
    description = Column(Text, nullable=True)
    items = Column(Text, nullable=True)  # JSON string untuk line items
    
    # Notes
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)  # Internal notes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.status}>"
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        from datetime import date
        return self.status != "paid" and self.due_date < date.today()
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.paid_amount
