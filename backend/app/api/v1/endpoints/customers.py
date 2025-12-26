from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.customer import Customer
from app.models.package import Package
from app.schemas import customer as customer_schema

router = APIRouter()


def generate_customer_code(db: Session) -> str:
    """
    Generate unique customer code
    Format: CUST-XXXX (auto increment)
    """
    last_customer = db.query(Customer).order_by(Customer.id.desc()).first()
    
    if last_customer and last_customer.customer_code:
        try:
            last_number = int(last_customer.customer_code.split('-')[1])
            new_number = last_number + 1
        except (IndexError, ValueError):
            new_number = 1
    else:
        new_number = 1
    
    return f"CUST-{new_number:04d}"


@router.get("/", response_model=List[customer_schema.CustomerInList])
def get_customers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by name, code, phone, or email"),
    status: Optional[str] = Query(None, description="Filter by status: active, suspended, inactive, terminated"),
    package_id: Optional[int] = Query(None, description="Filter by package ID"),
    city: Optional[str] = Query(None, description="Filter by city")
) -> Any:
    """
    Get customers list with pagination and filters
    """
    query = db.query(Customer)
    
    # Search filter
    if search:
        search_filter = or_(
            Customer.full_name.ilike(f"%{search}%"),
            Customer.customer_code.ilike(f"%{search}%"),
            Customer.phone.ilike(f"%{search}%"),
            Customer.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Status filter
    if status:
        query = query.filter(Customer.status == status)
    
    # Package filter
    if package_id:
        query = query.filter(Customer.package_id == package_id)
    
    # City filter
    if city:
        query = query.filter(Customer.city.ilike(f"%{city}%"))
    
    # Order by created date descending
    query = query.order_by(Customer.created_at.desc())
    
    # Pagination
    customers = query.offset(skip).limit(limit).all()
    
    return customers


@router.get("/count", response_model=dict)
def get_customers_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    status: Optional[str] = Query(None)
) -> Any:
    """
    Get total customers count with optional status filter
    """
    query = db.query(Customer)
    
    if status:
        query = query.filter(Customer.status == status)
    
    total = query.count()
    
    # Count by status
    active_count = db.query(Customer).filter(Customer.status == "active").count()
    suspended_count = db.query(Customer).filter(Customer.status == "suspended").count()
    inactive_count = db.query(Customer).filter(Customer.status == "inactive").count()
    terminated_count = db.query(Customer).filter(Customer.status == "terminated").count()
    
    return {
        "total": total,
        "active": active_count,
        "suspended": suspended_count,
        "inactive": inactive_count,
        "terminated": terminated_count
    }


@router.post("/", response_model=customer_schema.Customer, status_code=status.HTTP_201_CREATED)
def create_customer(
    *,
    db: Session = Depends(get_db),
    customer_in: customer_schema.CustomerCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new customer
    """
    # Check if email already exists
    if customer_in.email:
        existing_customer = db.query(Customer).filter(Customer.email == customer_in.email).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A customer with this email already exists"
            )
    
    # Check if package exists
    if customer_in.package_id:
        package = db.query(Package).filter(Package.id == customer_in.package_id).first()
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found"
            )
    
    # Generate customer code
    customer_code = generate_customer_code(db)
    
    # Create customer
    customer = Customer(
        customer_code=customer_code,
        **customer_in.model_dump(),
        status="active",
        is_active=True,
        activation_date=datetime.utcnow()
    )
    
    db.add(customer)
    db.commit()
    db.refresh(customer)
    
    return customer


@router.get("/{customer_id}", response_model=customer_schema.CustomerWithPackage)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get customer by ID with package details
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return customer


@router.put("/{customer_id}", response_model=customer_schema.Customer)
def update_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    customer_in: customer_schema.CustomerUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update customer
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Check if email is being changed and already exists
    if customer_in.email and customer_in.email != customer.email:
        existing_customer = db.query(Customer).filter(Customer.email == customer_in.email).first()
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A customer with this email already exists"
            )
    
    # Check if package exists
    if customer_in.package_id:
        package = db.query(Package).filter(Package.id == customer_in.package_id).first()
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found"
            )
    
    # Update customer fields
    update_data = customer_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    current_user: User = Depends(get_current_active_user)
) -> None:
    """
    Delete customer (soft delete - set to terminated)
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Soft delete - set status to terminated
    customer.status = "terminated"
    customer.is_active = False
    customer.termination_date = datetime.utcnow()
    
    db.commit()
    
    return None


@router.post("/{customer_id}/suspend", response_model=customer_schema.Customer)
def suspend_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Suspend customer (temporary block)
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    customer.status = "suspended"
    customer.is_active = False
    
    db.commit()
    db.refresh(customer)
    
    return customer


@router.post("/{customer_id}/activate", response_model=customer_schema.Customer)
def activate_customer(
    *,
    db: Session = Depends(get_db),
    customer_id: int,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Activate customer
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    customer.status = "active"
    customer.is_active = True
    
    if not customer.activation_date:
        customer.activation_date = datetime.utcnow()
    
    db.commit()
    db.refresh(customer)
    
    return customer
