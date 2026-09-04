from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.base_models import PanelType, ProductionLine, Shift
from app.models.lab import LabTest
from app.models.production import ProductionSheet
from app.schemas.lab import LabTestCreate

TWO_DECIMAL_PLACES = Decimal("0.01")

STATUS_GOOD = "good"
STATUS_WARNING = "warning"
STATUS_CRITICAL = "critical"


def create_lab_test(lab_test_input: LabTestCreate, db: Session) -> LabTest:

    production_sheet = ensure_production_ref_exists(lab_test_input.production_ref, db)

    ensure_production_line_exists(lab_test_input.production_line_id, db)
    ensure_shift_exists(lab_test_input.shift_id, db)

    new_lab_test = LabTest(
        **lab_test_input.model_dump(exclude={"production_ref"}),
        production_sheet_id=production_sheet.id,
    )

    try:
        db.add(new_lab_test)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Lab test with that lab reference already exists.",
        )
    db.refresh(new_lab_test)

    return new_lab_test


def list_lab_tests(
    db: Session,
    limit: int | None = None,
    offset: int | None = None,
    production_line_id: int | None = None,
    batch_id: int | None = None,
    shift_id: int | None = None,
    panel_type: PanelType | None = None,
    panel_thickness: Decimal | None = None,
    lab_test_date_from: datetime | None = None,
    lab_test_date_to: datetime | None = None,
):
    statement = select(LabTest)
    if production_line_id is not None:
        statement = statement.where(LabTest.production_line_id == production_line_id)

    if batch_id is not None:
        statement = statement.where(LabTest.batch_id == batch_id)

    if shift_id is not None:
        statement = statement.where(LabTest.shift_id == shift_id)

    if panel_type is not None:
        statement = statement.where(LabTest.panel_type == panel_type)

    if panel_thickness is not None:
        statement = statement.where(LabTest.panel_thickness == panel_thickness)

    if lab_test_date_from is not None:
        statement = statement.where(LabTest.lab_test_date >= lab_test_date_from)

    if lab_test_date_to is not None:
        statement = statement.where(LabTest.lab_test_date <= lab_test_date_to)

    statement = statement.order_by(LabTest.lab_test_date.desc(), LabTest.id.desc())

    if offset is not None:
        statement = statement.offset(offset)

    if limit is not None:
        statement = statement.limit(limit)

    return db.scalars(statement).all()


def get_lab_test(lab_test_id: int, db: Session) -> LabTest:

    lab_test = db.get(LabTest, lab_test_id)
    if not lab_test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lab test not found."
        )

    return lab_test


def ensure_production_ref_exists(production_ref: int, db: Session) -> ProductionSheet:

    statement = select(ProductionSheet).where(
        ProductionSheet.production_ref == production_ref
    )
    existing_production_ref = db.scalars(statement).first()

    if not existing_production_ref:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production Reference for this lab test does not exist.",
        )

    return existing_production_ref


def ensure_production_line_exists(production_line_id: int, db: Session):

    statement = select(ProductionLine).where(ProductionLine.id == production_line_id)
    existing_production_line = db.scalars(statement).first()
    if not existing_production_line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Production line with that id does not exist.",
        )


def ensure_shift_exists(shift_id: int, db: Session):

    statement = select(Shift).where(Shift.id == shift_id)
    existing_shift = db.scalars(statement).first()
    if not existing_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift with that id does not exist.",
        )
