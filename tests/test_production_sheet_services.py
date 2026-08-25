import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

from datetime import datetime, timezone
from decimal import Decimal

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


def test_list_production_sheets_can_filter_by_date_range():
    db = TestingSessionLocal()

    try:
        create_services(db)
        sheet_1_date = datetime(2026, 8, 1, tzinfo=timezone.utc)
        sheet_2_date = datetime(2026, 8, 10, tzinfo=timezone.utc)

        date_from = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc)
        date_to = datetime(2026, 8, 5, 23, 59, tzinfo=timezone.utc)

        new_production_sheet_1 = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_date=sheet_1_date, production_ref=1
            ),
            db,
        )

        new_production_sheet_2 = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_date=sheet_2_date, production_ref=2
            ),
            db,
        )

        production_sheets_list = production_sheets.list_production_sheets(
            production_date_from=date_from,
            production_date_to=date_to,
            db=db,
        )
        assert len(production_sheets_list) == 1
        assert production_sheets_list[0].id == new_production_sheet_1.id
        assert production_sheets_list[0].id != new_production_sheet_2.id

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_returns_ok():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_duration=100,
                total_downtime=5,
                panels_produced=100,
                panels_rejected=2,
                percentage_recycled_material=25,
            ),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        print(f"operational_assessment: {operational_assessment}")

        assert operational_assessment["production_metrics"]["accepted_panels"] == 98
        assert operational_assessment["quality"]["rejection_rate"] == 2.0
        assert operational_assessment["production_metrics"]["net_production_time"] == 95
        assert operational_assessment["downtime"]["downtime_rate"] == 5.0
        assert operational_assessment["quality"]["status"] == "good"
        assert operational_assessment["downtime"]["status"] == "good"
        assert operational_assessment["sustainability"]["status"] == "target_met"
        assert operational_assessment["overall_status"] == "good"
        assert (
            operational_assessment["sustainability"]["recycled_material_percentage"]
            > 10
        )
        assert operational_assessment["flags"] == []
        assert operational_assessment["main_issue"] is None

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_returns_critical_downtime():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_duration=100,
                total_downtime=30,
                panels_produced=100,
                panels_rejected=2,
                percentage_recycled_material=25,
            ),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert operational_assessment["production_metrics"]["accepted_panels"] == 98
        assert operational_assessment["quality"]["rejection_rate"] == 2.0
        assert (
            operational_assessment["production_metrics"]["net_production_time"] == 70.0
        )
        assert operational_assessment["downtime"]["downtime_rate"] == 30.0
        assert operational_assessment["quality"]["status"] == "good"
        assert operational_assessment["downtime"]["status"] == "critical"
        assert operational_assessment["sustainability"]["status"] == "target_met"
        assert operational_assessment["overall_status"] == "critical"
        assert operational_assessment["flags"] == ["critical_downtime"]
        assert operational_assessment["main_issue"] == "critical_downtime"

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_returns_critical_rejection():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                total_downtime=0,
                panels_produced=100,
                panels_rejected=40,
                percentage_recycled_material=25,
            ),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert operational_assessment["production_metrics"]["accepted_panels"] == 60
        assert operational_assessment["quality"]["rejection_rate"] == 40
        assert operational_assessment["quality"]["status"] == "critical"
        assert operational_assessment["flags"] == [
            "critical_rejection_rate",
        ]
        assert operational_assessment["main_issue"] == "critical_rejection_rate"
        assert operational_assessment["overall_status"] == "critical"

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_returns_critical_rejection_and_downtime():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                total_downtime=50,
                panels_produced=100,
                panels_rejected=40,
                percentage_recycled_material=25,
            ),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert operational_assessment["production_metrics"]["accepted_panels"] == 60
        assert operational_assessment["quality"]["rejection_rate"] == 40
        assert (
            operational_assessment["production_metrics"]["net_production_time"] == 100.5
        )
        assert operational_assessment["quality"]["status"] == "critical"
        assert operational_assessment["downtime"]["status"] == "critical"
        assert operational_assessment["flags"] == [
            "critical_rejection_rate",
            "critical_downtime",
        ]
        assert operational_assessment["main_issue"] == "critical_rejection_rate"
        assert operational_assessment["overall_status"] == "critical"

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_returns_warning_rejection_and_low_sustainability():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_duration=100,
                total_downtime=5,
                panels_produced=100,
                panels_rejected=4,
                percentage_recycled_material=5,
            ),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert operational_assessment["production_metrics"]["accepted_panels"] == 96
        assert operational_assessment["quality"]["rejection_rate"] == 4.0
        assert (
            operational_assessment["production_metrics"]["net_production_time"] == 95.0
        )
        assert operational_assessment["downtime"]["downtime_rate"] == 5.0
        assert operational_assessment["quality"]["status"] == "warning"
        assert operational_assessment["downtime"]["status"] == "good"
        assert operational_assessment["sustainability"]["status"] == "below_target"
        assert operational_assessment["overall_status"] == "warning"
        assert operational_assessment["flags"] == [
            "high_rejection_rate",
            "recycled_material_below_target",
        ]
        assert operational_assessment["main_issue"] == "high_rejection_rate"

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_missing_sheet_returns_not_found():
    db = TestingSessionLocal()

    try:
        with pytest.raises(HTTPException) as exc_info:
            production_sheets.get_production_sheet_operational_assessment(
                production_sheet_id=999,
                db=db,
            )

        assert exc_info.value.status_code == 404

    finally:
        db.close()


def test_list_production_sheets_orders_newest_production_date_first():
    db = TestingSessionLocal()

    try:
        create_services(db)

        newest_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_date=datetime(2026, 8, 10, tzinfo=timezone.utc),
                production_ref=1,
            ),
            db,
        )
        oldest_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_date=datetime(2026, 8, 1, tzinfo=timezone.utc),
                production_ref=2,
            ),
            db,
        )
        middle_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_date=datetime(2026, 8, 5, tzinfo=timezone.utc),
                production_ref=3,
            ),
            db,
        )

        production_sheets_list = production_sheets.list_production_sheets(db=db)

        ordered_ids = [sheet.id for sheet in production_sheets_list]
        assert ordered_ids == [
            newest_sheet.id,
            middle_sheet.id,
            oldest_sheet.id,
        ]

    finally:
        db.close()


def test_list_production_sheets_orders_newer_insertion_first_when_dates_match():
    db = TestingSessionLocal()

    try:
        create_services(db)
        same_production_date = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

        first_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_date=same_production_date,
                production_ref=1,
            ),
            db,
        )
        second_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                production_date=same_production_date,
                production_ref=2,
            ),
            db,
        )

        production_sheets_list = production_sheets.list_production_sheets(db=db)

        ordered_ids = [sheet.id for sheet in production_sheets_list]
        assert ordered_ids == [second_sheet.id, first_sheet.id]

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_process_params_within_target():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert (
            operational_assessment["process_parameters"]["press_temperature"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["press_pressure"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["press_factor"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["forming_line_speed"]["status"]
            == "within_target"
        )

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_press_temperature_above_target():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(press_temperature=200),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert (
            operational_assessment["process_parameters"]["press_temperature"]["status"]
            == "above_target"
        )

        assert (
            operational_assessment["process_parameters"]["press_pressure"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["press_factor"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["forming_line_speed"]["status"]
            == "within_target"
        )

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_press_temperature_below_target():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(press_temperature=100),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert (
            operational_assessment["process_parameters"]["press_temperature"]["status"]
            == "below_target"
        )

        assert (
            operational_assessment["process_parameters"]["press_pressure"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["press_factor"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["forming_line_speed"]["status"]
            == "within_target"
        )

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_press_temperature_at_target_limit():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(press_temperature=170),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert (
            operational_assessment["process_parameters"]["press_temperature"]["status"]
            == "within_target"
        )

        assert (
            operational_assessment["process_parameters"]["press_pressure"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["press_factor"]["status"]
            == "within_target"
        )
        assert (
            operational_assessment["process_parameters"]["forming_line_speed"]["status"]
            == "within_target"
        )

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_material_efficiency_all_panels_accepted():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                panels_produced=100,
                panels_rejected=0,
                resin_dosed=10,
                urea_dosed=3,
                paraffin_dosed=2,
            ),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert (
            operational_assessment["material_efficiency"]["chemical_total_dosed"]
            == new_production_sheet.resin_dosed
            + new_production_sheet.paraffin_dosed
            + new_production_sheet.urea_dosed
        )

        assert operational_assessment["material_efficiency"][
            "resin_per_accepted_panel"
        ] == pytest.approx(Decimal(10 / 100))
        assert operational_assessment["material_efficiency"][
            "paraffin_per_accepted_panel"
        ] == pytest.approx(Decimal(2 / 100))
        assert operational_assessment["material_efficiency"][
            "urea_per_accepted_panel"
        ] == pytest.approx(Decimal(3 / 100))

    finally:
        db.close()


def test_get_production_sheet_operational_assessment_material_efficiency_all_panels_rejected():
    db = TestingSessionLocal()

    try:
        create_services(db)
        new_production_sheet = production_sheets.create_production_sheet(
            build_production_sheet_payload(
                panels_produced=100,
                panels_rejected=100,
                resin_dosed=10,
                urea_dosed=3,
                paraffin_dosed=2,
            ),
            db,
        )

        operational_assessment = (
            production_sheets.get_production_sheet_operational_assessment(
                new_production_sheet.id, db
            )
        )

        assert (
            operational_assessment["material_efficiency"]["chemical_total_dosed"]
            == new_production_sheet.resin_dosed
            + new_production_sheet.paraffin_dosed
            + new_production_sheet.urea_dosed
        )

        assert (
            operational_assessment["material_efficiency"]["resin_per_accepted_panel"]
            == 0
        )
        assert (
            operational_assessment["material_efficiency"]["paraffin_per_accepted_panel"]
            == 0
        )
        assert (
            operational_assessment["material_efficiency"]["urea_per_accepted_panel"]
            == 0
        )

    finally:
        db.close()
