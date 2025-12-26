from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_superuser
from app.models.user import User
from app.schemas import package as package_schema
from app.services.package import PackageService

router = APIRouter()


@router.get("/", response_model=List[package_schema.PackageInList])
def get_packages(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    package_type: Optional[str] = Query(None, description="Filter by package type: residential, business, corporate")
) -> Any:
    """
    Get packages list with filters (Public - no auth required)
    """
    packages = PackageService.get_packages(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        package_type=package_type
    )
    return packages


@router.get("/count", response_model=dict)
def get_packages_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get packages count by type and status
    """
    from app.models.package import Package
    
    total = db.query(Package).count()
    active = db.query(Package).filter(Package.is_active == True).count()
    inactive = db.query(Package).filter(Package.is_active == False).count()
    residential = db.query(Package).filter(Package.package_type == "residential").count()
    business = db.query(Package).filter(Package.package_type == "business").count()
    corporate = db.query(Package).filter(Package.package_type == "corporate").count()
    
    return {
        "total": total,
        "active": active,
        "inactive": inactive,
        "residential": residential,
        "business": business,
        "corporate": corporate
    }


@router.get("/{package_id}", response_model=package_schema.Package)
def get_package(
    package_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get package by ID (Public - no auth required)
    """
    package = PackageService.get_package_by_id(db, package_id)
    return package


@router.get("/code/{code}", response_model=package_schema.Package)
def get_package_by_code(
    code: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Get package by code (Public - no auth required)
    """
    package = PackageService.get_package_by_code(db, code)
    return package


@router.post("/", response_model=package_schema.Package, status_code=status.HTTP_201_CREATED)
def create_package(
    *,
    db: Session = Depends(get_db),
    package_in: package_schema.PackageCreate,
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Create new package (Admin only)
    """
    package = PackageService.create_package(db, package_in)
    return package


@router.put("/{package_id}", response_model=package_schema.Package)
def update_package(
    *,
    db: Session = Depends(get_db),
    package_id: int,
    package_in: package_schema.PackageUpdate,
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Update package (Admin only)
    """
    package = PackageService.update_package(db, package_id, package_in)
    return package


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_package(
    *,
    db: Session = Depends(get_db),
    package_id: int,
    current_user: User = Depends(get_current_superuser)
) -> None:
    """
    Delete package (Admin only)
    Cannot delete if package has customers
    """
    PackageService.delete_package(db, package_id)
    return None


@router.post("/{package_id}/toggle", response_model=package_schema.Package)
def toggle_package_status(
    *,
    db: Session = Depends(get_db),
    package_id: int,
    current_user: User = Depends(get_current_superuser)
) -> Any:
    """
    Toggle package active status (Admin only)
    """
    package = PackageService.toggle_package_status(db, package_id)
    return package


@router.get("/{package_id}/customers", response_model=dict)
def get_package_customers(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get customers count for a package
    """
    from app.models.customer import Customer
    
    package = PackageService.get_package_by_id(db, package_id)
    
    total = db.query(Customer).filter(Customer.package_id == package_id).count()
    active = db.query(Customer).filter(
        Customer.package_id == package_id,
        Customer.status == "active"
    ).count()
    
    return {
        "package_id": package_id,
        "package_name": package.name,
        "total_customers": total,
        "active_customers": active
    }
