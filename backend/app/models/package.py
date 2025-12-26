from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.customer import Customer


class Package(Base):
    """
    Package model - Paket Internet ISP
    """
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Package Info
    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "PKG-10M"
    description = Column(Text, nullable=True)
    
    # Speed (in Mbps)
    download_speed = Column(Integer, nullable=False)  # Mbps
    upload_speed = Column(Integer, nullable=False)  # Mbps
    
    # Pricing
    price = Column(Numeric(15, 2), nullable=False)  # Harga per bulan
    installation_fee = Column(Numeric(15, 2), default=0)  # Biaya pemasangan
    
    # Quota (optional, 0 = unlimited)
    quota_gb = Column(Integer, default=0)  # 0 = unlimited
    
    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # Paket unggulan
    
    # Display Order
    sort_order = Column(Integer, default=0)
    
    # Package Type
    package_type = Column(String(50), default="residential")  # residential, business, corporate
    
    # Benefits/Features (JSON atau Text)
    features = Column(Text, nullable=True)  # Bisa simpan JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customers = relationship("Customer", back_populates="package", lazy="dynamic")
    
    def __repr__(self):
        return f"<Package {self.code} - {self.name}>"
