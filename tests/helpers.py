from datetime import datetime, timezone

from app.schemas.production import ProductionSheetCreate


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
