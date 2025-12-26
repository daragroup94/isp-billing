from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    """
    Customer model - Pelanggan ISP
    """
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Customer Identity
    customer_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "CUST-001"
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(20), nullable=False)
    id_card_number = Column(String(50), nullable=True)  # NIK/KTP
    
    # Address
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    province = Column(String(100), nullable=False)
    postal_code = Column(String(10), nullable=True)
    
    # Installation Address (if different)
    installation_address = Column(Text, nullable=True)
    installation_notes = Column(Text, nullable=True)  # Catatan lokasi
    
    # Package Subscription
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=True)
    package = relationship("Package", back_populates="customers")
    
    # Connection Details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    router_username = Column(String(100), nullable=True)
    router_password = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(20), default="active")  # active, suspended, inactive, terminated
    is_active = Column(Boolean, default=True)
    
    # Payment Info
    billing_day = Column(Integer, default=1)  # Tanggal tagihan (1-28)
    auto_payment = Column(Boolean, default=False)
    
    # Installation Date
    installation_date = Column(DateTime(timezone=True), nullable=True)
    activation_date = Column(DateTime(timezone=True), nullable=True)
    termination_date = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="customer", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Customer {self.customer_code} - {self.full_name}>"
