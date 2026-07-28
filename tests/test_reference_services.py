import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.schemas.base_models import ProductionLineCreate, ResinTypeCreate, ShiftCreate
from app.services import production_lines, resin_types, shifts

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


# Production Line tests


def test_create_production_line_normalizes_name():
    db = TestingSessionLocal()
    try:
        line = production_lines.create_production_line(
            ProductionLineCreate(name=" Line 1 "),
            db,
        )

        assert line.name == "line 1"
    finally:
        db.close()


def test_duplicate_production_line_returns_conflict():
    db = TestingSessionLocal()
    try:
        production_lines.create_production_line(ProductionLineCreate(name="Line 1"), db)

        with pytest.raises(HTTPException) as exc_info:
            production_lines.create_production_line(
                ProductionLineCreate(name=" line 1 "),
                db,
            )

        assert exc_info.value.status_code == 409
    finally:
        db.close()


def test_list_production_lines_can_filter_by_name():
    db = TestingSessionLocal()
    try:
        production_lines.create_production_line(ProductionLineCreate(name="Line 1"), db)
        production_lines.create_production_line(ProductionLineCreate(name="Line 2"), db)

        results = production_lines.list_production_lines(
            name="line 1",
            db=db,
            limit=20,
            offset=0,
        )

        assert [line.name for line in results] == ["line 1"]
    finally:
        db.close()


def test_missing_production_line_returns_not_found():
    db = TestingSessionLocal()
    try:
        with pytest.raises(HTTPException) as exc_info:
            production_lines.get_production_line(line_id=999, db=db)

        assert exc_info.value.status_code == 404
    finally:
        db.close()


# Resin Type tests


def test_create_resin_type_preserves_capitalization():
    db = TestingSessionLocal()
    try:
        resin_type = resin_types.create_resin_type(ResinTypeCreate(name=" pMDI "), db)

        assert resin_type.name == "pMDI"
    finally:
        db.close()


def test_duplicate_resin_type_is_case_insensitive():
    db = TestingSessionLocal()
    try:
        resin_types.create_resin_type(ResinTypeCreate(name="UF"), db)

        with pytest.raises(HTTPException) as exc_info:
            resin_types.create_resin_type(ResinTypeCreate(name="uf"), db)

        assert exc_info.value.status_code == 409
    finally:
        db.close()


# Resin Type tests


def test_create_shift_normalizes_letter_and_operator_names():
    db = TestingSessionLocal()
    try:
        shift = shifts.create_shift(
            ShiftCreate(
                shift_letter=" a ",
                press_operator=" Jane Smith ",
                line_operator=" Luis Costa ",
            ),
            db,
        )

        assert shift.shift_letter == "A"
        assert shift.press_operator == "Jane Smith"
        assert shift.line_operator == "Luis Costa"
    finally:
        db.close()


def test_invalid_shift_letter_returns_bad_request():
    db = TestingSessionLocal()
    try:
        with pytest.raises(HTTPException) as exc_info:
            shifts.create_shift(
                ShiftCreate(
                    shift_letter="AB",
                    press_operator="Jane Smith",
                    line_operator="Luis Costa",
                ),
                db,
            )

        assert exc_info.value.status_code == 400
    finally:
        db.close()


def test_missing_shift_returns_not_found():
    db = TestingSessionLocal()
    try:
        with pytest.raises(HTTPException) as exc_info:
            shifts.get_shift(shift_id=999, db=db)

        assert exc_info.value.status_code == 404
    finally:
        db.close()
