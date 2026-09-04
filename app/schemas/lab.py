from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.base_models import PanelType


class LabTestCreate(BaseModel):
    lab_ref: int = Field(gt=0)
    lab_test_date: datetime
    production_line_id: int = Field(gt=0)
    production_ref: int = Field(gt=0)
    batch_id: int = Field(gt=0)
    shift_id: int = Field(gt=0)
    panel_type: PanelType
    panel_thickness: Decimal = Field(max_digits=6, decimal_places=2, gt=0)
    actual_thickness: Decimal = Field(max_digits=6, decimal_places=2, gt=0)
    calculated_density: Decimal = Field(max_digits=6, decimal_places=0, ge=0)
    moisture_content: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    internal_bond: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    bending_strength: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    elastic_modulus: Decimal = Field(max_digits=6, decimal_places=0, ge=0)
    thickness_swelling: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    water_absorption: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    formaldehyde_emission: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    formaldehyde_content: Decimal = Field(max_digits=6, decimal_places=2, ge=0)


class LabTestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lab_ref: int = Field(gt=0)
    lab_test_date: datetime
    production_line_id: int = Field(gt=0)
    production_sheet_id: int | None = Field(default=None, gt=0)
    batch_id: int = Field(gt=0)
    shift_id: int = Field(gt=0)
    panel_type: PanelType
    panel_thickness: Decimal = Field(max_digits=6, decimal_places=2, gt=0)
    actual_thickness: Decimal = Field(max_digits=6, decimal_places=2, gt=0)
    calculated_density: Decimal = Field(max_digits=6, decimal_places=0, ge=0)
    moisture_content: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    internal_bond: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    bending_strength: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    elastic_modulus: Decimal = Field(max_digits=6, decimal_places=0, ge=0)
    thickness_swelling: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    water_absorption: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    formaldehyde_emission: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    formaldehyde_content: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    created_at: datetime
    updated_at: datetime
