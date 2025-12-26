from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    customers,
    packages,
    invoices,
    payments,
    dashboard
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    customers.router,
    prefix="/customers",
    tags=["Customers"]
)

api_router.include_router(
    packages.router,
    prefix="/packages",
    tags=["Packages"]
)

api_router.include_router(
    invoices.router,
    prefix="/invoices",
    tags=["Invoices"]
)

api_router.include_router(
    payments.router,
    prefix="/payments",
    tags=["Payments"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)
