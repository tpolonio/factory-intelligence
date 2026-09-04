from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.models.base_models import PanelType
from app.schemas.base_models import ProductionLineCreate
from app.services import lab_tests, production_lines
from tests.helpers import (
    build_lab_test_payload,
    create_lab_test_services,
)


def test_create_lab_test_with_valid_reference_ids(db_session):
    new_production_sheet = create_lab_test_services(db_session)

    new_lab_test = lab_tests.create_lab_test(
        build_lab_test_payload(production_ref=new_production_sheet.production_ref),
        db_session,
    )

    assert new_lab_test.lab_ref == 1
    assert new_lab_test.production_line_id == 1
    assert new_lab_test.batch_id == 1
    assert new_lab_test.shift_id == 1
    assert new_lab_test.panel_type == PanelType.MDF
    assert new_lab_test.panel_thickness == Decimal("18.00")
    assert new_lab_test.actual_thickness == Decimal("18.50")
    assert new_lab_test.calculated_density == Decimal("650.00")
    assert new_lab_test.moisture_content == Decimal("7.00")
    assert new_lab_test.internal_bond == Decimal("1.00")
    assert new_lab_test.bending_strength == Decimal("18.00")
    assert new_lab_test.elastic_modulus == Decimal("2000.00")
    assert new_lab_test.thickness_swelling == Decimal("5.00")
    assert new_lab_test.water_absorption == Decimal("5.00")
    assert new_lab_test.formaldehyde_emission == Decimal("0.10")
    assert new_lab_test.formaldehyde_content == Decimal("1.00")
    assert new_lab_test.created_at is not None


def test_duplicate_lab_test_returns_conflict(db_session):
    create_lab_test_services(db_session)
    lab_tests.create_lab_test(build_lab_test_payload(), db_session)

    with pytest.raises(HTTPException) as exc_info:
        lab_tests.create_lab_test(build_lab_test_payload(), db_session)

    assert exc_info.value.status_code == 409


def test_lab_test_returns_not_found(db_session):
    create_lab_test_services(db_session)

    with pytest.raises(HTTPException) as exc_info:
        lab_tests.create_lab_test(
            build_lab_test_payload(production_line_id=999), db_session
        )

    assert exc_info.value.status_code == 404


def test_list_lab_tests_returns_created_tests(db_session):
    create_lab_test_services(db_session)

    new_lab_test = lab_tests.create_lab_test(
        build_lab_test_payload(),
        db_session,
    )

    lab_tests_list = lab_tests.list_lab_tests(db_session)
    assert len(lab_tests_list) == 1
    assert lab_tests_list[0].lab_ref == new_lab_test.lab_ref


def test_list_lab_tests_can_filter_by_panel_type(db_session):
    create_lab_test_services(db_session)

    new_lab_test_1 = lab_tests.create_lab_test(
        build_lab_test_payload(),
        db_session,
    )

    new_lab_test_2 = lab_tests.create_lab_test(
        build_lab_test_payload(lab_ref=2, panel_type=PanelType.OSB),
        db_session,
    )

    lab_tests_list = lab_tests.list_lab_tests(panel_type=PanelType.MDF, db=db_session)
    assert len(lab_tests_list) == 1
    assert new_lab_test_1.panel_type == "MDF"
    assert new_lab_test_2.panel_type == "OSB"
    assert lab_tests_list[0].panel_type == "MDF"


def test_list_lab_tests_can_filter_by_production_line_id(db_session):
    create_lab_test_services(db_session)

    production_lines.create_production_line(
        ProductionLineCreate(name="OSB Line"),
        db_session,
    )

    new_lab_test_1 = lab_tests.create_lab_test(
        build_lab_test_payload(),
        db_session,
    )

    new_lab_test_2 = lab_tests.create_lab_test(
        build_lab_test_payload(lab_ref=2, production_line_id=2),
        db_session,
    )

    lab_tests_list = lab_tests.list_lab_tests(
        production_line_id=1,
        db=db_session,
    )
    assert len(lab_tests_list) == 1
    assert new_lab_test_1.production_line_id == 1
    assert new_lab_test_2.production_line_id == 2
    assert lab_tests_list[0].production_line_id == 1


def test_list_lab_tests_applies_limit(db_session):
    create_lab_test_services(db_session)
    lab_tests.create_lab_test(
        build_lab_test_payload(),
        db_session,
    )

    lab_tests.create_lab_test(
        build_lab_test_payload(lab_ref=2),
        db_session,
    )

    lab_tests_list = lab_tests.list_lab_tests(limit=1, db=db_session)
    assert len(lab_tests_list) == 1


def test_get_lab_test_returns_existing_test(db_session):
    create_lab_test_services(db_session)

    new_lab_test = lab_tests.create_lab_test(
        build_lab_test_payload(),
        db_session,
    )

    lab_test = lab_tests.get_lab_test(
        lab_test_id=new_lab_test.id,
        db=db_session,
    )

    assert lab_test.id == new_lab_test.id
    assert lab_test.lab_ref == new_lab_test.lab_ref


def test_missing_lab_test_returns_not_found(db_session):
    create_lab_test_services(db_session)
    lab_tests.create_lab_test(
        build_lab_test_payload(),
        db_session,
    )

    with pytest.raises(HTTPException) as exc_info:
        lab_tests.get_lab_test(lab_test_id=999, db=db_session)

    assert exc_info.value.status_code == 404


def test_list_lab_tests_can_filter_by_date_range(db_session):
    create_lab_test_services(db_session)
    sheet_1_date = datetime(2026, 8, 1, tzinfo=timezone.utc)
    sheet_2_date = datetime(2026, 8, 10, tzinfo=timezone.utc)

    date_from = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc)
    date_to = datetime(2026, 8, 5, 23, 59, tzinfo=timezone.utc)

    new_lab_test_1 = lab_tests.create_lab_test(
        build_lab_test_payload(lab_test_date=sheet_1_date, lab_ref=1),
        db_session,
    )

    new_lab_test_2 = lab_tests.create_lab_test(
        build_lab_test_payload(lab_test_date=sheet_2_date, lab_ref=2),
        db_session,
    )

    lab_tests_list = lab_tests.list_lab_tests(
        lab_test_date_from=date_from,
        lab_test_date_to=date_to,
        db=db_session,
    )
    assert len(lab_tests_list) == 1
    assert lab_tests_list[0].id == new_lab_test_1.id
    assert lab_tests_list[0].id != new_lab_test_2.id
