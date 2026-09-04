from datetime import datetime, timezone

from app.schemas.base_models import ProductionLineCreate, ResinTypeCreate, ShiftCreate
from app.schemas.lab import LabTestCreate
from app.schemas.production import ProductionSheetCreate
from app.services import production_lines, production_sheets, resin_types, shifts


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
        "production_duration": 150.0,
        "total_downtime": 20.4,
        "resin_dosed": 10,
        "paraffin_dosed": 4,
        "urea_dosed": 1,
        "percentage_recycled_material": 10,
        "panels_produced": 100,
        "panels_rejected": 5,
    }
    data.update(overrides)
    return ProductionSheetCreate(**data)


def build_lab_test_payload(**overrides):
    data = {
        "lab_ref": 1,
        "lab_test_date": datetime.now(timezone.utc),
        "production_ref": 1,
        "production_line_id": 1,
        "batch_id": 1,
        "shift_id": 1,
        "panel_type": "MDF",
        "panel_thickness": 18,
        "actual_thickness": 18.5,
        "calculated_density": 650.0,
        "moisture_content": 7.0,
        "internal_bond": 1.0,
        "bending_strength": 18.0,
        "elastic_modulus": 2000.0,
        "thickness_swelling": 5,
        "water_absorption": 5,
        "formaldehyde_emission": 0.1,
        "formaldehyde_content": 1.0,
    }
    data.update(overrides)
    return LabTestCreate(**data)


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


def create_production_sheet_services(db):
    create_production_line(db)
    create_resin_type(db)
    create_shift(db)


def create_lab_test_services(db):
    create_production_line(db)
    create_resin_type(db)
    create_shift(db)

    new_production_sheet = production_sheets.create_production_sheet(
        build_production_sheet_payload(),
        db,
    )

    return new_production_sheet
