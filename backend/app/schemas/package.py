from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


# Base Schema
class PackageBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    download_speed: int = Field(..., gt=0)
    upload_speed: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    installation_fee: Decimal = Field(default=Decimal('0'), ge=0)
    quota_gb: int = Field(default=0, ge=0)
    is_active: bool = True
    is_featured: bool = False
    sort_order: int = Field(default=0, ge=0)
    package_type: str = Field(default="residential", pattern="^(residential|business|corporate)$")
    features: Optional[str] = None


# Schema for creating new package
class PackageCreate(PackageBase):
    pass


# Schema for updating package
class PackageUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    download_speed: Optional[int] = Field(None, gt=0)
    upload_speed: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    installation_fee: Optional[Decimal] = Field(None, ge=0)
    quota_gb: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)
    package_type: Optional[str] = Field(None, pattern="^(residential|business|corporate)$")
    features: Optional[str] = None


# Schema for package in database (response)
class Package(PackageBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Schema for package in list (compact)
class PackageInList(BaseModel):
    id: int
    name: str
    code: str
    download_speed: int
    upload_speed: int
    price: Decimal
    package_type: str
    is_active: bool
    is_featured: bool
    
    model_config = ConfigDict(from_attributes=True)


# Schema with customer count
class PackageWithStats(Package):
    customer_count: int = 0
