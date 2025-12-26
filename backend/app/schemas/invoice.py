from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


# Base Schema
class InvoiceBase(BaseModel):
    customer_id: int
    billing_period: str = Field(..., min_length=1, max_length=20)
    period_start: date
    period_end: date
    invoice_date: date
    due_date: date
    subtotal: Decimal = Field(..., ge=0)
    discount: Decimal = Field(default=Decimal('0'), ge=0)
    late_fee: Decimal = Field(default=Decimal('0'), ge=0)
    tax: Decimal = Field(default=Decimal('0'), ge=0)
    total_amount: Decimal = Field(..., ge=0)
    description: Optional[str] = None
    items: Optional[str] = None
    notes: Optional[str] = None
    admin_notes: Optional[str] = None


# Schema for creating new invoice
class InvoiceCreate(InvoiceBase):
    pass


# Schema for updating invoice
class InvoiceUpdate(BaseModel):
    billing_period: Optional[str] = Field(None, min_length=1, max_length=20)
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    subtotal: Optional[Decimal] = Field(None, ge=0)
    discount: Optional[Decimal] = Field(None, ge=0)
    late_fee: Optional[Decimal] = Field(None, ge=0)
    tax: Optional[Decimal] = Field(None, ge=0)
    total_amount: Optional[Decimal] = Field(None, ge=0)
    paid_amount: Optional[Decimal] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(pending|paid|partial|overdue|cancelled)$")
    description: Optional[str] = None
    items: Optional[str] = None
    notes: Optional[str] = None
    admin_notes: Optional[str] = None


# Schema for invoice in database (response)
class Invoice(InvoiceBase):
    id: int
    invoice_number: str
    paid_amount: Decimal
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Schema for invoice in list (compact)
class InvoiceInList(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    billing_period: str
    invoice_date: date
    due_date: date
    total_amount: Decimal
    paid_amount: Decimal
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Schema with customer details
class InvoiceWithCustomer(Invoice):
    customer: Optional["CustomerInInvoice"] = None


# For circular import prevention
class CustomerInInvoice(BaseModel):
    id: int
    customer_code: str
    full_name: str
    email: Optional[str] = None
    phone: str
    
    model_config = ConfigDict(from_attributes=True)


# Schema for generating invoice
class InvoiceGenerate(BaseModel):
    customer_id: int
    billing_month: date  # First day of the month
