from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.production import ProductionSheet
from app.schemas.production import ProductionSheetCreate


def create_production_sheet(
    production_sheet_input: ProductionSheetCreate, db: Session
) -> ProductionSheet:

    new_production_sheet = ProductionSheet

    try:
        db.add(new_production_sheet)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Production sheet with that name already exists.",
        )
    db.refresh(new_production_sheet)

    return new_production_sheet
