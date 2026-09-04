from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models.base_models import PanelType
from app.schemas.base_models import ProductionLineCreate
from app.services import production_lines, production_sheets
from tests.helpers import (
    build_production_sheet_payload,
    create_production_line,
    create_production_sheet_services,
    create_resin_type,
    create_shift,
)


def test_create_production_sheet_with_valid_reference_ids(db_session):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
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
    assert new_production_sheet.production_duration == 150.0
    assert new_production_sheet.total_downtime == 20.4
    assert new_production_sheet.resin_dosed == 10
    assert new_production_sheet.paraffin_dosed == 4
    assert new_production_sheet.urea_dosed == 1
    assert new_production_sheet.percentage_recycled_material == 10
    assert new_production_sheet.panels_produced == 100
    assert new_production_sheet.panels_rejected == 5
    assert new_production_sheet.rejection_rate == 5.0


def test_duplicate_production_ref_returns_conflict(db_session):
    create_production_sheet_services(db_session)
    production_sheets.create_production_sheet(
        build_production_sheet_payload(), db_session
    )

    with pytest.raises(HTTPException) as exc_info:
        production_sheets.create_production_sheet(
            build_production_sheet_payload(), db_session
        )

    assert exc_info.value.status_code == 409


def test_missing_production_line_returns_not_found(db_session):
    create_resin_type(db_session)
    create_shift(db_session)

    with pytest.raises(HTTPException) as exc_info:
        production_sheets.create_production_sheet(
            build_production_sheet_payload(production_line_id=999), db_session
        )

    assert exc_info.value.status_code == 404


def test_missing_shift_returns_not_found(db_session):
    create_production_line(db_session)
    create_resin_type(db_session)

    with pytest.raises(HTTPException) as exc_info:
        production_sheets.create_production_sheet(
            build_production_sheet_payload(shift_id=999), db_session
        )

    assert exc_info.value.status_code == 404


def test_missing_resin_type_returns_not_found(db_session):
    create_production_line(db_session)
    create_shift(db_session)

    with pytest.raises(HTTPException) as exc_info:
        production_sheets.create_production_sheet(
            build_production_sheet_payload(resin_type_id=999), db_session
        )

    assert exc_info.value.status_code == 404


def test_list_production_sheets_returns_created_sheets(db_session):
    create_production_sheet_services(db_session)

    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
    )

    production_sheets_list = production_sheets.list_production_sheets(db_session)
    assert len(production_sheets_list) == 1
    assert (
        production_sheets_list[0].production_ref == new_production_sheet.production_ref
    )


def test_list_production_sheets_can_filter_by_panel_type(db_session):
    create_production_sheet_services(db_session)

    new_production_sheet_1 = production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
    )

    new_production_sheet_2 = production_sheets.create_production_sheet(
        build_production_sheet_payload(production_ref=2, panel_type=PanelType.OSB),
        db_session,
    )

    production_sheets_list = production_sheets.list_production_sheets(
        panel_type=PanelType.MDF, db=db_session
    )
    assert len(production_sheets_list) == 1
    assert new_production_sheet_1.panel_type == "MDF"
    assert new_production_sheet_2.panel_type == "OSB"
    assert production_sheets_list[0].panel_type == "MDF"


def test_list_production_sheets_can_filter_by_production_ref(db_session):
    create_production_sheet_services(db_session)

    new_production_sheet_1 = production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
    )

    new_production_sheet_2 = production_sheets.create_production_sheet(
        build_production_sheet_payload(production_ref=2),
        db_session,
    )

    production_sheets_list = production_sheets.list_production_sheets(
        production_ref=1, db=db_session
    )
    assert len(production_sheets_list) == 1
    assert new_production_sheet_1.production_ref == 1
    assert new_production_sheet_2.production_ref == 2
    assert production_sheets_list[0].production_ref == 1


def test_list_production_sheets_can_filter_by_production_line_id(db_session):
    create_production_sheet_services(db_session)

    production_lines.create_production_line(
        ProductionLineCreate(name="OSB Line"),
        db_session,
    )

    new_production_sheet_1 = production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
    )

    new_production_sheet_2 = production_sheets.create_production_sheet(
        build_production_sheet_payload(production_ref=2, production_line_id=2),
        db_session,
    )

    production_sheets_list = production_sheets.list_production_sheets(
        production_line_id=1,
        db=db_session,
    )
    assert len(production_sheets_list) == 1
    assert new_production_sheet_1.production_line_id == 1
    assert new_production_sheet_2.production_line_id == 2
    assert production_sheets_list[0].production_line_id == 1


def test_list_production_sheets_applies_limit(db_session):
    create_production_sheet_services(db_session)
    production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
    )

    production_sheets.create_production_sheet(
        build_production_sheet_payload(production_ref=2),
        db_session,
    )

    production_sheets_list = production_sheets.list_production_sheets(
        limit=1, db=db_session
    )
    assert len(production_sheets_list) == 1


def test_get_production_sheet_returns_existing_sheet(db_session):
    create_production_sheet_services(db_session)

    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
    )

    production_sheet = production_sheets.get_production_sheet(
        production_sheet_id=new_production_sheet.id,
        db=db_session,
    )

    assert production_sheet.id == new_production_sheet.id
    assert production_sheet.production_ref == new_production_sheet.production_ref


def test_missing_production_sheet_returns_not_found(db_session):
    create_production_sheet_services(db_session)
    production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
    )

    with pytest.raises(HTTPException) as exc_info:
        production_sheets.get_production_sheet(production_sheet_id=999, db=db_session)

    assert exc_info.value.status_code == 404


def test_list_production_sheets_can_filter_by_date_range(db_session):
    create_production_sheet_services(db_session)
    sheet_1_date = datetime(2026, 8, 1, tzinfo=timezone.utc)
    sheet_2_date = datetime(2026, 8, 10, tzinfo=timezone.utc)

    date_from = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc)
    date_to = datetime(2026, 8, 5, 23, 59, tzinfo=timezone.utc)

    new_production_sheet_1 = production_sheets.create_production_sheet(
        build_production_sheet_payload(production_date=sheet_1_date, production_ref=1),
        db_session,
    )

    new_production_sheet_2 = production_sheets.create_production_sheet(
        build_production_sheet_payload(production_date=sheet_2_date, production_ref=2),
        db_session,
    )

    production_sheets_list = production_sheets.list_production_sheets(
        production_date_from=date_from,
        production_date_to=date_to,
        db=db_session,
    )
    assert len(production_sheets_list) == 1
    assert production_sheets_list[0].id == new_production_sheet_1.id
    assert production_sheets_list[0].id != new_production_sheet_2.id


def test_get_production_sheet_operational_assessment_returns_ok(db_session):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            production_duration=100,
            total_downtime=5,
            panels_produced=100,
            panels_rejected=2,
            percentage_recycled_material=25,
        ),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["production_metrics"]["accepted_panels"] == 98
    assert operational_assessment["quality"]["rejection_rate"] == 2.0
    assert operational_assessment["production_metrics"]["net_production_time"] == 95
    assert operational_assessment["downtime"]["downtime_rate"] == 5.0
    assert operational_assessment["quality"]["status"] == "good"
    assert operational_assessment["downtime"]["status"] == "good"
    assert operational_assessment["sustainability"]["status"] == "target_met"
    assert operational_assessment["overall_status"] == "good"
    assert operational_assessment["sustainability"]["recycled_material_percentage"] > 10
    assert operational_assessment["flags"] == []
    assert operational_assessment["main_issue"] is None


def test_get_production_sheet_operational_assessment_returns_critical_downtime(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            production_duration=100,
            total_downtime=30,
            panels_produced=100,
            panels_rejected=2,
            percentage_recycled_material=25,
        ),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["production_metrics"]["accepted_panels"] == 98
    assert operational_assessment["quality"]["rejection_rate"] == 2.0
    assert operational_assessment["production_metrics"]["net_production_time"] == 70.0
    assert operational_assessment["downtime"]["downtime_rate"] == 30.0
    assert operational_assessment["quality"]["status"] == "good"
    assert operational_assessment["downtime"]["status"] == "critical"
    assert operational_assessment["sustainability"]["status"] == "target_met"
    assert operational_assessment["overall_status"] == "critical"
    assert operational_assessment["flags"] == ["critical_downtime"]
    assert operational_assessment["main_issue"] == "critical_downtime"


def test_get_production_sheet_operational_assessment_returns_critical_rejection(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            total_downtime=0,
            panels_produced=100,
            panels_rejected=40,
            percentage_recycled_material=25,
        ),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
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


def test_get_production_sheet_operational_assessment_returns_critical_rejection_and_downtime(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            total_downtime=50,
            panels_produced=100,
            panels_rejected=40,
            percentage_recycled_material=25,
        ),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["production_metrics"]["accepted_panels"] == 60
    assert operational_assessment["quality"]["rejection_rate"] == 40
    assert operational_assessment["production_metrics"]["net_production_time"] == 100
    assert operational_assessment["quality"]["status"] == "critical"
    assert operational_assessment["downtime"]["status"] == "critical"
    assert operational_assessment["flags"] == [
        "critical_rejection_rate",
        "critical_downtime",
    ]
    assert operational_assessment["main_issue"] == "critical_rejection_rate"
    assert operational_assessment["overall_status"] == "critical"


def test_get_production_sheet_operational_assessment_returns_warning_rejection_and_low_sustainability(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            production_duration=100,
            total_downtime=5,
            panels_produced=100,
            panels_rejected=4,
            percentage_recycled_material=5,
        ),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["production_metrics"]["accepted_panels"] == 96
    assert operational_assessment["quality"]["rejection_rate"] == 4.0
    assert operational_assessment["production_metrics"]["net_production_time"] == 95.0
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


def test_get_production_sheet_operational_assessment_missing_sheet_returns_not_found(
    db_session,
):
    with pytest.raises(HTTPException) as exc_info:
        production_sheets.get_production_sheet_operational_assessment(
            production_sheet_id=999,
            db=db_session,
        )

    assert exc_info.value.status_code == 404


def test_list_production_sheets_orders_newest_production_date_first(db_session):
    create_production_sheet_services(db_session)

    newest_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            production_date=datetime(2026, 8, 10, tzinfo=timezone.utc),
            production_ref=1,
        ),
        db_session,
    )
    oldest_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            production_date=datetime(2026, 8, 1, tzinfo=timezone.utc),
            production_ref=2,
        ),
        db_session,
    )
    middle_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            production_date=datetime(2026, 8, 5, tzinfo=timezone.utc),
            production_ref=3,
        ),
        db_session,
    )

    production_sheets_list = production_sheets.list_production_sheets(db=db_session)

    ordered_ids = [sheet.id for sheet in production_sheets_list]
    assert ordered_ids == [
        newest_sheet.id,
        middle_sheet.id,
        oldest_sheet.id,
    ]


def test_list_production_sheets_orders_newer_insertion_first_when_dates_match(
    db_session,
):
    create_production_sheet_services(db_session)
    same_production_date = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)

    first_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            production_date=same_production_date,
            production_ref=1,
        ),
        db_session,
    )
    second_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            production_date=same_production_date,
            production_ref=2,
        ),
        db_session,
    )

    production_sheets_list = production_sheets.list_production_sheets(db=db_session)

    ordered_ids = [sheet.id for sheet in production_sheets_list]
    assert ordered_ids == [second_sheet.id, first_sheet.id]


def test_get_production_sheet_operational_assessment_process_params_within_target(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
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


def test_get_production_sheet_operational_assessment_press_temperature_above_target(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(press_temperature=200),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
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


def test_get_production_sheet_operational_assessment_press_temperature_below_target(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(press_temperature=100),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
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


def test_get_production_sheet_operational_assessment_press_temperature_at_target_limit(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(press_temperature=170),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
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


def test_get_production_sheet_operational_assessment_quality_status_warning(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(panels_rejected=4),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["quality"]["status"] == "warning"


def test_get_production_sheet_operational_assessment_quality_status_critical(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(panels_rejected=8),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["quality"]["status"] == "critical"


def test_get_production_sheet_operational_assessment_downtime_status_warning(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(production_duration=100, total_downtime=10.1),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["downtime"]["status"] == "warning"


def test_get_production_sheet_operational_assessment_downtime_status_critical(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(production_duration=100, total_downtime=21),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["downtime"]["status"] == "critical"


def test_get_production_sheet_operational_assessment_sustainability_target_met(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(percentage_recycled_material=20),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert operational_assessment["sustainability"]["status"] == "target_met"


def test_get_production_sheet_operational_assessment_material_efficiency_all_panels_accepted(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            panels_produced=100,
            panels_rejected=0,
            resin_dosed=10,
            urea_dosed=3,
            paraffin_dosed=2,
        ),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
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


def test_get_production_sheet_operational_assessment_material_efficiency_all_panels_rejected(
    db_session,
):
    create_production_sheet_services(db_session)
    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(
            panels_produced=100,
            panels_rejected=100,
            resin_dosed=10,
            urea_dosed=3,
            paraffin_dosed=2,
        ),
        db_session,
    )

    operational_assessment = (
        production_sheets.get_production_sheet_operational_assessment(
            new_production_sheet.id, db_session
        )
    )

    assert (
        operational_assessment["material_efficiency"]["chemical_total_dosed"]
        == new_production_sheet.resin_dosed
        + new_production_sheet.paraffin_dosed
        + new_production_sheet.urea_dosed
    )

    assert (
        operational_assessment["material_efficiency"]["resin_per_accepted_panel"] == 0
    )
    assert (
        operational_assessment["material_efficiency"]["paraffin_per_accepted_panel"]
        == 0
    )
    assert operational_assessment["material_efficiency"]["urea_per_accepted_panel"] == 0
