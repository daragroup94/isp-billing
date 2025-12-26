from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, date


# Base Schema
class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: str = Field(..., min_length=10, max_length=20)
    id_card_number: Optional[str] = Field(None, max_length=50)
    address: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2, max_length=100)
    province: str = Field(..., min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    installation_address: Optional[str] = None
    installation_notes: Optional[str] = None
    package_id: Optional[int] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    router_username: Optional[str] = Field(None, max_length=100)
    router_password: Optional[str] = Field(None, max_length=100)
    billing_day: int = Field(default=1, ge=1, le=28)
    auto_payment: bool = False
    notes: Optional[str] = None


# Schema for creating new customer
class CustomerCreate(CustomerBase):
    pass


# Schema for updating customer
class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    id_card_number: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, min_length=5)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    province: Optional[str] = Field(None, min_length=2, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    installation_address: Optional[str] = None
    installation_notes: Optional[str] = None
    package_id: Optional[int] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    router_username: Optional[str] = Field(None, max_length=100)
    router_password: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(active|suspended|inactive|terminated)$")
    is_active: Optional[bool] = None
    billing_day: Optional[int] = Field(None, ge=1, le=28)
    auto_payment: Optional[bool] = None
    notes: Optional[str] = None


# Schema for customer in database (response)
class Customer(CustomerBase):
    id: int
    customer_code: str
    status: str
    is_active: bool
    installation_date: Optional[datetime] = None
    activation_date: Optional[datetime] = None
    termination_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Schema with package details
class CustomerWithPackage(Customer):
    package: Optional["PackageInCustomer"] = None


# Schema for customer list (compact)
class CustomerInList(BaseModel):
    id: int
    customer_code: str
    full_name: str
    phone: str
    email: Optional[EmailStr] = None
    city: str
    status: str
    is_active: bool
    package_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# For circular import prevention
class PackageInCustomer(BaseModel):
    id: int
    name: str
    code: str
    download_speed: int
    upload_speed: int
    price: float
    
    model_config = ConfigDict(from_attributes=True)
