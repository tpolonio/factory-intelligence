from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def lab_health_check():
    return {"domain": "lab","status": "healthy"}