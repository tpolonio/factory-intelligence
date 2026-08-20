from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.base_models import PanelType, ProductionLine, ResinType, Shift
from app.models.production import ProductionSheet
from app.schemas.production import ProductionSheetCreate

REJECTION_RATE_WARNING_THRESHOLD = 3.0
REJECTION_RATE_CRITICAL_THRESHOLD = 7.0

DOWNTIME_RATE_WARNING_THRESHOLD = 10.0
DOWNTIME_RATE_CRITICAL_THRESHOLD = 20.0

RECYCLED_MATERIAL_TARGET_PERCENTAGE = 20.0

STATUS_GOOD = "good"
STATUS_WARNING = "warning"
STATUS_CRITICAL = "critical"

SUSTAINABILITY_TARGET_MET = "target_met"
SUSTAINABILITY_BELOW_TARGET = "below_target"

FLAG_HIGH_REJECTION_RATE = "high_rejection_rate"
FLAG_CRITICAL_REJECTION_RATE = "critical_rejection_rate"
FLAG_DOWNTIME_ABOVE_TARGET = "downtime_above_target"
FLAG_CRITICAL_DOWNTIME = "critical_downtime"
FLAG_RECYCLED_MATERIAL_BELOW_TARGET = "recycled_material_below_target"

MAIN_ISSUE_PRIORITY = [
    FLAG_CRITICAL_REJECTION_RATE,
    FLAG_CRITICAL_DOWNTIME,
    FLAG_HIGH_REJECTION_RATE,
    FLAG_DOWNTIME_ABOVE_TARGET,
    FLAG_RECYCLED_MATERIAL_BELOW_TARGET,
]


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


def list_production_sheets(
    db: Session,
    limit: int | None = None,
    offset: int | None = None,
    production_line_id: int | None = None,
    shift_id: int | None = None,
    resin_type_id: int | None = None,
    production_ref: int | None = None,
    batch_id: int | None = None,
    panel_type: PanelType | None = None,
    production_date_from: datetime | None = None,
    production_date_to: datetime | None = None,
):
    statement = select(ProductionSheet)
    if production_line_id is not None:
        statement = statement.where(
            ProductionSheet.production_line_id == production_line_id
        )

    if shift_id is not None:
        statement = statement.where(ProductionSheet.shift_id == shift_id)

    if resin_type_id is not None:
        statement = statement.where(ProductionSheet.resin_type_id == resin_type_id)

    if production_ref is not None:
        statement = statement.where(ProductionSheet.production_ref == production_ref)

    if batch_id is not None:
        statement = statement.where(ProductionSheet.batch_id == batch_id)

    if panel_type is not None:
        statement = statement.where(ProductionSheet.panel_type == panel_type)

    if production_date_from is not None:
        statement = statement.where(
            ProductionSheet.production_date >= production_date_from
        )

    if production_date_to is not None:
        statement = statement.where(
            ProductionSheet.production_date <= production_date_to
        )

    statement = statement.order_by(
        ProductionSheet.production_date.desc(), ProductionSheet.id.desc()
    )

    if offset is not None:
        statement = statement.offset(offset)

    if limit is not None:
        statement = statement.limit(limit)

    return db.scalars(statement).all()


def get_production_sheet(production_sheet_id: int, db: Session) -> ProductionSheet:

    production_sheet = db.get(ProductionSheet, production_sheet_id)
    if not production_sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Production sheet not found."
        )

    return production_sheet


def get_production_sheet_operational_assessment(
    production_sheet_id: int,
    db: Session,
):
    production_sheet = get_production_sheet(
        production_sheet_id=production_sheet_id,
        db=db,
    )

    accepted_panels = (
        production_sheet.panels_produced - production_sheet.panels_rejected
    )
    rejection_rate = production_sheet.rejection_rate

    net_production_time = (
        production_sheet.production_duration - production_sheet.total_downtime
    )

    downtime_rate = (
        production_sheet.total_downtime / production_sheet.production_duration * 100
    )

    quality_status = classify_quality_status(rejection_rate)
    downtime_status = classify_downtime_status(downtime_rate)
    sustainability_status = classify_sustainability_status(
        production_sheet.percentage_recycled_material
    )

    overall_status = classify_overall_status(
        quality_status=quality_status,
        downtime_status=downtime_status,
    )

    flags = build_operational_flags(
        quality_status=quality_status,
        downtime_status=downtime_status,
        sustainability_status=sustainability_status,
    )

    main_issue = choose_main_issue(flags)

    return {
        "production_sheet_id": production_sheet.id,
        "production_ref": production_sheet.production_ref,
        "accepted_panels": accepted_panels,
        "rejection_rate": rejection_rate,
        "net_production_time": net_production_time,
        "downtime_rate": downtime_rate,
        "quality_status": quality_status,
        "downtime_status": downtime_status,
        "sustainability_status": sustainability_status,
        "overall_status": overall_status,
        "flags": flags,
        "main_issue": main_issue,
    }


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


def classify_quality_status(rejection_rate: float) -> str:
    if rejection_rate > REJECTION_RATE_CRITICAL_THRESHOLD:
        return STATUS_CRITICAL

    if rejection_rate > REJECTION_RATE_WARNING_THRESHOLD:
        return STATUS_WARNING

    return STATUS_GOOD


def classify_downtime_status(downtime_rate: float) -> str:
    if downtime_rate > DOWNTIME_RATE_CRITICAL_THRESHOLD:
        return STATUS_CRITICAL

    if downtime_rate > DOWNTIME_RATE_WARNING_THRESHOLD:
        return STATUS_WARNING

    return STATUS_GOOD


def classify_sustainability_status(recycled_material_percentage: float) -> str:
    if recycled_material_percentage >= RECYCLED_MATERIAL_TARGET_PERCENTAGE:
        return SUSTAINABILITY_TARGET_MET

    return SUSTAINABILITY_BELOW_TARGET


def classify_overall_status(quality_status: str, downtime_status: str) -> str:
    if STATUS_CRITICAL in (quality_status, downtime_status):
        return STATUS_CRITICAL

    if STATUS_WARNING in (quality_status, downtime_status):
        return STATUS_WARNING

    return STATUS_GOOD


def build_operational_flags(
    quality_status: str,
    downtime_status: str,
    sustainability_status: str,
) -> list[str]:
    flags = []

    if quality_status == STATUS_CRITICAL:
        flags.append(FLAG_CRITICAL_REJECTION_RATE)
    elif quality_status == STATUS_WARNING:
        flags.append(FLAG_HIGH_REJECTION_RATE)

    if downtime_status == STATUS_CRITICAL:
        flags.append(FLAG_CRITICAL_DOWNTIME)
    elif downtime_status == STATUS_WARNING:
        flags.append(FLAG_DOWNTIME_ABOVE_TARGET)

    if sustainability_status == SUSTAINABILITY_BELOW_TARGET:
        flags.append(FLAG_RECYCLED_MATERIAL_BELOW_TARGET)

    return flags


def choose_main_issue(flags: list[str]) -> str | None:
    for issue in MAIN_ISSUE_PRIORITY:
        if issue in flags:
            return issue

    return None
