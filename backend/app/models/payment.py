from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Payment(Base):
    """
    Payment model - Pembayaran dari pelanggan
    """
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Payment Info
    payment_number = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "PAY-2024-12-001"
    
    # Customer Reference
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer", back_populates="payments")
    
    # Invoice Reference
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    invoice = relationship("Invoice", back_populates="payments")
    
    # Payment Details
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    
    # Payment Method
    payment_method = Column(String(50), nullable=False)  # cash, bank_transfer, e-wallet, credit_card
    
    # Bank Transfer Details
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    account_name = Column(String(255), nullable=True)
    
    # Reference/Receipt Number
    reference_number = Column(String(100), nullable=True)  # No. referensi bank/receipt
    receipt_image = Column(String(500), nullable=True)  # Path/URL to receipt image
    
    # Status
    status = Column(String(20), default="pending")  # pending, verified, rejected, cancelled
    
    # Verification
    verified_by = Column(Integer, nullable=True)  # User ID yang verifikasi
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)  # Internal notes
    rejection_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Payment {self.payment_number} - {self.amount}>"
