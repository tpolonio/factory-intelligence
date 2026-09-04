from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

import app.services.lab_tests as lab_test_service
from app.core.database import get_db
from app.models.base_models import PanelType
from app.schemas.lab import (
    LabTestCreate,
    LabTestRead,
)

router = APIRouter()


@router.get("/health")
async def lab_health_check():
    return {"domain": "lab", "status": "healthy"}


# ---------------------------------Lab Tests--------------------------------------#


@router.post(
    "/lab-tests",
    response_model=LabTestRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_new_lab_test(
    lab_test_input: LabTestCreate,
    db: Annotated[Session, Depends(get_db)],
):

    new_lab_test = lab_test_service.create_lab_test(lab_test_input, db)

    return new_lab_test


@router.get(
    "/lab-tests",
    response_model=list[LabTestRead],
    status_code=status.HTTP_200_OK,
)
async def list_lab_tests(
    db: Annotated[Session, Depends(get_db)],
    production_line_id: int | None = Query(default=None, gt=0),
    batch_id: int | None = Query(default=None, gt=0),
    shift_id: int | None = Query(default=None, gt=0),
    panel_type: PanelType | None = None,
    panel_thickness: Decimal | None = None,
    lab_test_date_from: datetime | None = None,
    lab_test_date_to: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    lab_test_retrieved = lab_test_service.list_lab_tests(
        production_line_id=production_line_id,
        shift_id=shift_id,
        batch_id=batch_id,
        panel_type=panel_type,
        panel_thickness=panel_thickness,
        lab_test_date_from=lab_test_date_from,
        lab_test_date_to=lab_test_date_to,
        db=db,
        limit=limit,
        offset=offset,
    )
    return lab_test_retrieved


@router.get(
    "/lab-tests/{lab_test_id}",
    response_model=LabTestRead,
    status_code=status.HTTP_200_OK,
)
async def show_lab_test(
    db: Annotated[Session, Depends(get_db)],
    lab_test_id: int,
):
    lab_test_retrieved = lab_test_service.get_lab_test(
        lab_test_id=lab_test_id,
        db=db,
    )
    return lab_test_retrieved
