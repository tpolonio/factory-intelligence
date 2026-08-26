import pytest
from fastapi import HTTPException

from app.schemas.base_models import ProductionLineCreate, ResinTypeCreate, ShiftCreate
from app.services import production_lines, resin_types, shifts

# Production Line tests


def test_create_production_line_normalizes_name(db_session):
    line = production_lines.create_production_line(
        ProductionLineCreate(name=" Line 1 "),
        db_session,
    )

    assert line.name == "line 1"


def test_duplicate_production_line_returns_conflict(db_session):
    production_lines.create_production_line(
        ProductionLineCreate(name="Line 1"), db_session
    )

    with pytest.raises(HTTPException) as exc_info:
        production_lines.create_production_line(
            ProductionLineCreate(name=" line 1 "),
            db_session,
        )

    assert exc_info.value.status_code == 409


def test_list_production_lines_can_filter_by_name(db_session):
    production_lines.create_production_line(
        ProductionLineCreate(name="Line 1"), db_session
    )
    production_lines.create_production_line(
        ProductionLineCreate(name="Line 2"), db_session
    )

    results = production_lines.list_production_lines(
        name="line 1",
        db=db_session,
        limit=20,
        offset=0,
    )

    assert [line.name for line in results] == ["line 1"]


def test_missing_production_line_returns_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        production_lines.get_production_line(line_id=999, db=db_session)

    assert exc_info.value.status_code == 404


# Resin Type tests


def test_create_resin_type_preserves_capitalization(db_session):
    resin_type = resin_types.create_resin_type(
        ResinTypeCreate(name=" pMDI "), db_session
    )

    assert resin_type.name == "pMDI"


def test_duplicate_resin_type_is_case_insensitive(db_session):
    resin_types.create_resin_type(ResinTypeCreate(name="UF"), db_session)

    with pytest.raises(HTTPException) as exc_info:
        resin_types.create_resin_type(ResinTypeCreate(name="uf"), db_session)

    assert exc_info.value.status_code == 409


# Resin Type tests


def test_create_shift_normalizes_letter_and_operator_names(db_session):
    shift = shifts.create_shift(
        ShiftCreate(
            shift_letter=" a ",
            press_operator=" Joao Fernandes ",
            line_operator=" Luis Costa ",
        ),
        db_session,
    )

    assert shift.shift_letter == "A"
    assert shift.press_operator == "Joao Fernandes"
    assert shift.line_operator == "Luis Costa"


def test_invalid_shift_letter_returns_bad_request(db_session):
    with pytest.raises(HTTPException) as exc_info:
        shifts.create_shift(
            ShiftCreate(
                shift_letter="AB",
                press_operator="Jane Smith",
                line_operator="Luis Costa",
            ),
            db_session,
        )

    assert exc_info.value.status_code == 400


def test_missing_shift_returns_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        shifts.get_shift(shift_id=999, db=db_session)

    assert exc_info.value.status_code == 404
