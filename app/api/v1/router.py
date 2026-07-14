from fastapi import APIRouter
from app.api.v1 import lab, production


router = APIRouter()

router.include_router(lab.router, prefix="/lab", tags=["Lab"])
router.include_router(production.router, prefix="/production", tags=["Production"])