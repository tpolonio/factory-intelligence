from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

import app.services.production_lines as production_line_service
import app.services.production_sheets as production_sheet_service
import app.services.resin_types as resin_type_service
import app.services.shifts as shift_service
from app.core.database import get_db
from app.models.base_models import PanelType
from app.schemas.base_models import (
    ProductionLineCreate,
    ProductionLineRead,
    ResinTypeCreate,
    ResinTypeRead,
    ShiftCreate,
    ShiftRead,
)
from app.schemas.production import ProductionSheetCreate, ProductionSheetRead

router = APIRouter()


@router.get("/health")
def production_health_check():
    return {"domain": "production", "status": "healthy"}


# ---------------------------------Production Sheets--------------------------------------#


@router.post(
    "/production-sheets",
    response_model=ProductionSheetRead,
    status_code=status.HTTP_201_CREATED,
)
def add_new_production_sheet(
    production_sheet_input: ProductionSheetCreate,
    db: Annotated[Session, Depends(get_db)],
):

    new_production_sheet = production_sheet_service.create_production_sheet(
        production_sheet_input, db
    )

    return new_production_sheet


@router.get(
    "/production-sheets",
    response_model=list[ProductionSheetRead],
    status_code=status.HTTP_200_OK,
)
def list_production_sheets(
    db: Annotated[Session, Depends(get_db)],
    production_line_id: int | None = Query(default=None, gt=0),
    shift_id: int | None = Query(default=None, gt=0),
    resin_type_id: int | None = Query(default=None, gt=0),
    production_ref: int | None = Query(default=None, gt=0),
    batch_id: int | None = Query(default=None, gt=0),
    panel_type: PanelType | None = None,
    production_date_from: datetime | None = None,
    production_date_to: datetime | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    production_sheet_retrieved = production_sheet_service.list_production_sheets(
        production_line_id=production_line_id,
        shift_id=shift_id,
        resin_type_id=resin_type_id,
        production_ref=production_ref,
        batch_id=batch_id,
        panel_type=panel_type,
        production_date_from=production_date_from,
        production_date_to=production_date_to,
        db=db,
        limit=limit,
        offset=offset,
    )
    return production_sheet_retrieved


@router.get(
    "/production-sheets/{production_sheet_id}",
    response_model=ProductionSheetRead,
    status_code=status.HTTP_200_OK,
)
def show_production_sheet(
    db: Annotated[Session, Depends(get_db)],
    production_sheet_id: int,
):
    production_sheet_retrieved = production_sheet_service.get_production_sheet(
        production_sheet_id=production_sheet_id,
        db=db,
    )
    return production_sheet_retrieved


# ---------------------------------Production Lines--------------------------------------#


@router.post(
    "/lines", response_model=ProductionLineRead, status_code=status.HTTP_201_CREATED
)
def add_new_production_line(
    production_line_input: ProductionLineCreate,
    db: Annotated[Session, Depends(get_db)],
):

    new_production_line = production_line_service.create_production_line(
        production_line_input, db
    )

    return new_production_line


@router.get("/lines", response_model=list[ProductionLineRead])
def list_production_lines(
    db: Annotated[Session, Depends(get_db)],
    name: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):

    production_lines_retrieved = production_line_service.list_production_lines(
        name=name, db=db, limit=limit, offset=offset
    )
    return production_lines_retrieved


@router.get("/lines/{line_id}", response_model=ProductionLineRead)
def show_production_line(line_id: int, db: Annotated[Session, Depends(get_db)]):

    production_line = production_line_service.get_production_line(
        line_id=line_id, db=db
    )
    return production_line


# ---------------------------------Resin Types--------------------------------------#


@router.post(
    "/resin-types", response_model=ResinTypeRead, status_code=status.HTTP_201_CREATED
)
def add_new_resin_type(
    resin_type_input: ResinTypeCreate,
    db: Annotated[Session, Depends(get_db)],
):

    new_resin_type = resin_type_service.create_resin_type(resin_type_input, db)

    return new_resin_type


@router.get("/resin-types", response_model=list[ResinTypeRead])
def list_resin_types(
    db: Annotated[Session, Depends(get_db)],
    name: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):

    resin_type_retrieved = resin_type_service.list_resin_types(
        name=name, db=db, limit=limit, offset=offset
    )
    return resin_type_retrieved


@router.get("/resin-types/{resin_type_id}", response_model=ResinTypeRead)
def show_resin_type(resin_type_id: int, db: Annotated[Session, Depends(get_db)]):

    resin_type = resin_type_service.get_resin_type(resin_type_id=resin_type_id, db=db)
    return resin_type


# ---------------------------------Shifts--------------------------------------#


@router.post("/shifts", response_model=ShiftRead, status_code=status.HTTP_201_CREATED)
def add_new_shift(shift_input: ShiftCreate, db: Annotated[Session, Depends(get_db)]):

    new_shift = shift_service.create_shift(shift_input, db)

    return new_shift


@router.get("/shifts", response_model=list[ShiftRead])
def list_shifts(
    db: Annotated[Session, Depends(get_db)],
    shift_letter: str | None = None,
    press_operator: str | None = None,
    line_operator: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):

    shifts_retrieved = shift_service.list_shifts(
        shift_letter=shift_letter,
        press_operator=press_operator,
        line_operator=line_operator,
        db=db,
        limit=limit,
        offset=offset,
    )
    return shifts_retrieved


@router.get("/shifts/{shift_id}", response_model=ShiftRead)
def show_shift(shift_id: int, db: Annotated[Session, Depends(get_db)]):

    shift = shift_service.get_shift(shift_id=shift_id, db=db)
    return shift
