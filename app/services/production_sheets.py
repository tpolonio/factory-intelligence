from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.base_models import ProductionLine, ResinType, Shift
from app.models.production import ProductionSheet
from app.schemas.production import ProductionSheetCreate


def create_production_sheet(
    production_sheet_input: ProductionSheetCreate, db: Session
) -> ProductionSheet:

    ensure_unique_production_ref(production_sheet_input.production_ref, db)
    ensure_production_line_exists(production_sheet_input.production_line_id, db)
    ensure_shift_exists(production_sheet_input.shift_id, db)
    ensure_resin_type_exists(production_sheet_input.resin_type_id, db)

    new_production_sheet = ProductionSheet(**production_sheet_input.model_dump())

    try:
        db.add(new_production_sheet)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Production sheet with that production reference already exists.",
        )
    db.refresh(new_production_sheet)

    return new_production_sheet


def ensure_unique_production_ref(production_ref: int, db: Session):

    statement = select(ProductionSheet).where(
        production_ref == ProductionSheet.production_ref
    )
    existing_production_ref = db.scalars(statement).first()
    if existing_production_ref:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Production Reference already exists.",
        )


def ensure_production_line_exists(production_line_id: int, db: Session):

    statement = select(ProductionLine).where(production_line_id == ProductionLine.id)
    existing_production_line = db.scalars(statement).first()
    if not existing_production_line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production line with that id does not exist.",
        )


def ensure_shift_exists(shift_id: int, db: Session):

    statement = select(Shift).where(shift_id == Shift.id)
    existing_shift = db.scalars(statement).first()
    if not existing_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift with that id does not exist.",
        )


def ensure_resin_type_exists(resin_type_id: int, db: Session):
    statement = select(ResinType).where(resin_type_id == ResinType.id)

    existing_resin_type = db.scalars(statement).first()

    if not existing_resin_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resin Type with that id does not exist.",
        )
