import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.base_models import PanelType
from app.schemas.base_models import ProductionLineCreate, ResinTypeCreate, ShiftCreate
from app.schemas.production import ProductionSheetCreate
from app.services import production_lines, production_sheets, resin_types, shifts

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def create_production_line(db):
    return production_lines.create_production_line(
        ProductionLineCreate(name="MDF Line"),
        db,
    )


def create_resin_type(db):
    return resin_types.create_resin_type(ResinTypeCreate(name="UF"), db)


def create_shift(db):
    return shifts.create_shift(
        ShiftCreate(
            shift_letter="A",
            press_operator="Joao Fernandes",
            line_operator="Luis Costa",
        ),
        db,
    )


def build_production_sheet_payload(**overrides):
    data = {
        "production_ref": 1,
        "production_line_id": 1,
        "shift_id": 1,
        "resin_type_id": 1,
        "batch_id": 1,
        "production_date": datetime.now(timezone.utc),
        "panel_type": "MDF",
        "panel_length": 4880,
        "panel_width": 1200,
        "panel_thickness": 18,
        "forming_line_speed": 10.5,
        "press_temperature": 180.0,
        "press_pressure": 150.0,
        "press_factor": 0.8,
        "production_duration": 150.5,
        "total_downtime": 20.4,
        "resin_dosed": 12,
        "paraffin_dosed": 4,
        "urea_dosed": 0.5,
        "percentage_recycled_material": 12,
        "panels_produced": 123,
        "panels_rejected": 8,
    }
    data.update(overrides)
    return ProductionSheetCreate(**data)


def create_services(db):
    create_production_line(db)
    create_resin_type(db)
    create_shift(db)


def test_create_production_sheet_with_valid_reference_ids():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        assert new_production_sheet.production_ref == 1
        assert new_production_sheet.production_line_id == 1
        assert new_production_sheet.shift_id == 1
        assert new_production_sheet.resin_type_id == 1
        assert new_production_sheet.panel_type == "MDF"
        assert new_production_sheet.panel_length == 4880
        assert new_production_sheet.panel_width == 1200
        assert new_production_sheet.panel_thickness == 18
        assert new_production_sheet.forming_line_speed == 10.5
        assert new_production_sheet.press_temperature == 180.0
        assert new_production_sheet.press_pressure == 150.0
        assert new_production_sheet.press_factor == 0.8
        assert new_production_sheet.production_duration == 150.5
        assert new_production_sheet.total_downtime == 20.4
        assert new_production_sheet.resin_dosed == 12
        assert new_production_sheet.paraffin_dosed == 4
        assert new_production_sheet.urea_dosed == 0.5
        assert new_production_sheet.percentage_recycled_material == 12
        assert new_production_sheet.panels_produced == 123
        assert new_production_sheet.panels_rejected == 8
        assert new_production_sheet.rejection_rate == pytest.approx(
            6.504065040650406, rel=1e-9
        )

    finally:
        db.close()


def test_duplicate_production_ref_returns_conflict():
    db = TestingSessionLocal()
    try:
        create_services(db)
        production_sheets.create_production_sheet(build_production_sheet_payload(), db)

        with pytest.raises(HTTPException) as exc_info:
            production_sheets.create_production_sheet(
                build_production_sheet_payload(), db
            )

        assert exc_info.value.status_code == 409
    finally:
        db.close()


def test_missing_production_line_returns_not_found():
    db = TestingSessionLocal()

    try:
        create_resin_type(db)
        create_shift(db)

        with pytest.raises(HTTPException) as exc_info:
            production_sheets.create_production_sheet(
                build_production_sheet_payload(production_line_id=999), db
            )

        assert exc_info.value.status_code == 404
    finally:
        db.close()


def test_missing_shift_returns_not_found():
    db = TestingSessionLocal()

    try:
        create_production_line(db)
        create_resin_type(db)

        with pytest.raises(HTTPException) as exc_info:
            production_sheets.create_production_sheet(
                build_production_sheet_payload(shift_id=999), db
            )

        assert exc_info.value.status_code == 404
    finally:
        db.close()


def test_missing_resin_type_returns_not_found():
    db = TestingSessionLocal()

    try:
        create_production_line(db)
        create_shift(db)

        with pytest.raises(HTTPException) as exc_info:
            production_sheets.create_production_sheet(
                build_production_sheet_payload(resin_type_id=999), db
            )

        assert exc_info.value.status_code == 404
    finally:
        db.close()


def test_list_production_sheets_returns_created_sheets():
    db = TestingSessionLocal()

    try:
        create_services(db)

        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        production_sheets_list = production_sheets.list_production_sheets(db)
        assert len(production_sheets_list) == 1
        assert (
            production_sheets_list[0].production_ref
            == new_production_sheet.production_ref
        )

    finally:
        db.close()


def test_list_production_sheets_can_filter_by_panel_type():
    db = TestingSessionLocal()

    try:
        create_services(db)

        new_production_sheet_1 = production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        new_production_sheet_2 = production_sheets.create_production_sheet(
            build_production_sheet_payload(production_ref=2, panel_type=PanelType.OSB),
            db,
        )

        production_sheets_list = production_sheets.list_production_sheets(
            panel_type=PanelType.MDF, db=db
        )
        assert len(production_sheets_list) == 1
        assert new_production_sheet_1.panel_type == "MDF"
        assert new_production_sheet_2.panel_type == "OSB"
        assert production_sheets_list[0].panel_type == "MDF"

    finally:
        db.close()


def test_list_production_sheets_can_filter_by_production_ref():
    db = TestingSessionLocal()

    try:
        create_services(db)

        new_production_sheet_1 = production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        new_production_sheet_2 = production_sheets.create_production_sheet(
            build_production_sheet_payload(production_ref=2),
            db,
        )

        production_sheets_list = production_sheets.list_production_sheets(
            production_ref=1, db=db
        )
        assert len(production_sheets_list) == 1
        assert new_production_sheet_1.production_ref == 1
        assert new_production_sheet_2.production_ref == 2
        assert production_sheets_list[0].production_ref == 1

    finally:
        db.close()


def test_list_production_sheets_can_filter_by_production_line_id():

    db = TestingSessionLocal()

    try:
        create_services(db)

        production_lines.create_production_line(
            ProductionLineCreate(name="OSB Line"),
            db,
        )

        new_production_sheet_1 = production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        new_production_sheet_2 = production_sheets.create_production_sheet(
            build_production_sheet_payload(production_ref=2, production_line_id=2),
            db,
        )

        production_sheets_list = production_sheets.list_production_sheets(
            production_line_id=1,
            db=db,
        )
        assert len(production_sheets_list) == 1
        assert new_production_sheet_1.production_line_id == 1
        assert new_production_sheet_2.production_line_id == 2
        assert production_sheets_list[0].production_line_id == 1

    finally:
        db.close()


def test_list_production_sheets_applies_limit():
    db = TestingSessionLocal()

    try:
        create_services(db)
        production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        production_sheets.create_production_sheet(
            build_production_sheet_payload(production_ref=2),
            db,
        )

        production_sheets_list = production_sheets.list_production_sheets(
            limit=1, db=db
        )
        assert len(production_sheets_list) == 1

    finally:
        db.close()


def test_get_production_sheet_returns_existing_sheet():
    db = TestingSessionLocal()

    try:
        create_services(db)

        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        production_sheet = production_sheets.get_production_sheet(
            production_sheet_id=new_production_sheet.id,
            db=db,
        )

        assert production_sheet.id == new_production_sheet.id
        assert production_sheet.production_ref == new_production_sheet.production_ref
    finally:
        db.close()


def test_missing_production_sheet_returns_not_found():
    db = TestingSessionLocal()

    try:
        create_services(db)
        production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        with pytest.raises(HTTPException) as exc_info:
            production_sheets.get_production_sheet(production_sheet_id=999, db=db)

        assert exc_info.value.status_code == 404
    finally:
        db.close()
