from fastapi import APIRouter

router = APIRouter()

# Placeholder - akan diisi nanti
@router.get("/")
async def get_invoices():
    return {"message": "Invoices endpoint - coming soon"}
