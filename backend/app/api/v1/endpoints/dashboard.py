from fastapi import APIRouter

router = APIRouter()

# Placeholder - akan diisi nanti
@router.get("/")
async def get_dashboard():
    return {"message": "Dashboard endpoint - coming soon"}
