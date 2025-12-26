from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


# Base Schema
class PaymentBase(BaseModel):
    customer_id: int
    invoice_id: Optional[int] = None
    payment_date: date
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., pattern="^(cash|bank_transfer|e_wallet|credit_card)$")
    bank_name: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    account_name: Optional[str] = Field(None, max_length=255)
    reference_number: Optional[str] = Field(None, max_length=100)
    receipt_image: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None


# Schema for creating new payment
class PaymentCreate(PaymentBase):
    pass


# Schema for updating payment
class PaymentUpdate(BaseModel):
    payment_date: Optional[date] = None
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_method: Optional[str] = Field(None, pattern="^(cash|bank_transfer|e_wallet|credit_card)$")
    bank_name: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    account_name: Optional[str] = Field(None, max_length=255)
    reference_number: Optional[str] = Field(None, max_length=100)
    receipt_image: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    admin_notes: Optional[str] = None


# Schema for payment in database (response)
class Payment(PaymentBase):
    id: int
    payment_number: str
    status: str
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Schema for payment in list (compact)
class PaymentInList(BaseModel):
    id: int
    payment_number: str
    customer_id: int
    invoice_id: Optional[int] = None
    payment_date: date
    amount: Decimal
    payment_method: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema with customer and invoice details
class PaymentWithDetails(Payment):
    customer: Optional["CustomerInPayment"] = None
    invoice: Optional["InvoiceInPayment"] = None


# For circular import prevention
class CustomerInPayment(BaseModel):
    id: int
    customer_code: str
    full_name: str
    email: Optional[str] = None
    phone: str
    
    model_config = ConfigDict(from_attributes=True)


class InvoiceInPayment(BaseModel):
    id: int
    invoice_number: str
    billing_period: str
    total_amount: Decimal
    status: str
    
    model_config = ConfigDict(from_attributes=True)


# Schema for payment verification
class PaymentVerify(BaseModel):
    admin_notes: Optional[str] = None


# Schema for payment rejection
class PaymentReject(BaseModel):
    rejection_reason: str = Field(..., min_length=1)
    admin_notes: Optional[str] = None
