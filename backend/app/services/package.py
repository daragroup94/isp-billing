from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException, status

from app.models.package import Package
from app.schemas.package import PackageCreate, PackageUpdate


class PackageService:
    """
    Package service for business logic
    """
    
    @staticmethod
    def get_packages(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        package_type: Optional[str] = None
    ) -> List[Package]:
        """Get packages list with filters"""
        query = db.query(Package)
        
        if is_active is not None:
            query = query.filter(Package.is_active == is_active)
        
        if package_type:
            query = query.filter(Package.package_type == package_type)
        
        query = query.order_by(Package.sort_order.asc(), Package.created_at.asc())
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_package_by_id(db: Session, package_id: int) -> Package:
        """Get package by ID"""
        package = db.query(Package).filter(Package.id == package_id).first()
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found"
            )
        return package
    
    @staticmethod
    def get_package_by_code(db: Session, code: str) -> Package:
        """Get package by code"""
        package = db.query(Package).filter(Package.code == code).first()
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found"
            )
        return package
    
    @staticmethod
    def create_package(db: Session, package_in: PackageCreate) -> Package:
        """Create new package"""
        # Check if name exists
        existing = db.query(Package).filter(Package.name == package_in.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A package with this name already exists"
            )
        
        # Check if code exists
        existing = db.query(Package).filter(Package.code == package_in.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A package with this code already exists"
            )
        
        # Create package
        package = Package(**package_in.model_dump())
        db.add(package)
        db.commit()
        db.refresh(package)
        
        return package
    
    @staticmethod
    def update_package(
        db: Session,
        package_id: int,
        package_in: PackageUpdate
    ) -> Package:
        """Update package"""
        package = PackageService.get_package_by_id(db, package_id)
        
        # Check if name is being changed and already exists
        if package_in.name and package_in.name != package.name:
            existing = db.query(Package).filter(Package.name == package_in.name).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A package with this name already exists"
                )
        
        # Check if code is being changed and already exists
        if package_in.code and package_in.code != package.code:
            existing = db.query(Package).filter(Package.code == package_in.code).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A package with this code already exists"
                )
        
        # Update fields
        update_data = package_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(package, field, value)
        
        db.commit()
        db.refresh(package)
        
        return package
    
    @staticmethod
    def delete_package(db: Session, package_id: int) -> None:
        """Delete package"""
        package = PackageService.get_package_by_id(db, package_id)
        
        # Check if package has customers
        if package.customers.count() > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete package. {package.customers.count()} customers are using this package"
            )
        
        db.delete(package)
        db.commit()
    
    @staticmethod
    def toggle_package_status(db: Session, package_id: int) -> Package:
        """Toggle package active status"""
        package = PackageService.get_package_by_id(db, package_id)
        
        package.is_active = not package.is_active
        
        db.commit()
        db.refresh(package)
        
        return package
