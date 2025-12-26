from fastapi import APIRouter

router = APIRouter()

# Placeholder - akan diisi nanti
@router.get("/")
async def get_packages():
    return {"message": "Packages endpoint - coming soon"}
