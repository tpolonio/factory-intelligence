from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def production_health_check():
    return {"domain": "production","status": "healthy"}