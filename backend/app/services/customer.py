from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from fastapi import HTTPException, status

from app.models.customer import Customer
from app.models.package import Package
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """
    Customer service for business logic
    """
    
    @staticmethod
    def generate_customer_code(db: Session) -> str:
        """Generate unique customer code"""
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
    
    @staticmethod
    def get_customers(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
        package_id: Optional[int] = None,
        city: Optional[str] = None
    ) -> List[Customer]:
        """Get customers list with filters"""
        query = db.query(Customer)
        
        if search:
            search_filter = or_(
                Customer.full_name.ilike(f"%{search}%"),
                Customer.customer_code.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if status:
            query = query.filter(Customer.status == status)
        
        if package_id:
            query = query.filter(Customer.package_id == package_id)
        
        if city:
            query = query.filter(Customer.city.ilike(f"%{city}%"))
        
        query = query.order_by(Customer.created_at.desc())
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_customers_count(db: Session, status: Optional[str] = None) -> dict:
        """Get customers count by status"""
        query = db.query(Customer)
        
        if status:
            query = query.filter(Customer.status == status)
        
        total = query.count()
        
        return {
            "total": total,
            "active": db.query(Customer).filter(Customer.status == "active").count(),
            "suspended": db.query(Customer).filter(Customer.status == "suspended").count(),
            "inactive": db.query(Customer).filter(Customer.status == "inactive").count(),
            "terminated": db.query(Customer).filter(Customer.status == "terminated").count()
        }
    
    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Customer:
        """Get customer by ID"""
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return customer
    
    @staticmethod
    def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
        """Create new customer"""
        # Check if email exists
        if customer_in.email:
            existing = db.query(Customer).filter(Customer.email == customer_in.email).first()
            if existing:
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
        customer_code = CustomerService.generate_customer_code(db)
        
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
    
    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        customer_in: CustomerUpdate
    ) -> Customer:
        """Update customer"""
        customer = CustomerService.get_customer_by_id(db, customer_id)
        
        # Check if email is being changed and already exists
        if customer_in.email and customer_in.email != customer.email:
            existing = db.query(Customer).filter(Customer.email == customer_in.email).first()
            if existing:
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
        
        # Update fields
        update_data = customer_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        
        return customer
    
    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> None:
        """Soft delete customer"""
        customer = CustomerService.get_customer_by_id(db, customer_id)
        
        customer.status = "terminated"
        customer.is_active = False
        customer.termination_date = datetime.utcnow()
        
        db.commit()
    
    @staticmethod
    def suspend_customer(db: Session, customer_id: int) -> Customer:
        """Suspend customer"""
        customer = CustomerService.get_customer_by_id(db, customer_id)
        
        customer.status = "suspended"
        customer.is_active = False
        
        db.commit()
        db.refresh(customer)
        
        return customer
    
    @staticmethod
    def activate_customer(db: Session, customer_id: int) -> Customer:
        """Activate customer"""
        customer = CustomerService.get_customer_by_id(db, customer_id)
        
        customer.status = "active"
        customer.is_active = True
        
        if not customer.activation_date:
            customer.activation_date = datetime.utcnow()
        
        db.commit()
        db.refresh(customer)
        
        return customer
