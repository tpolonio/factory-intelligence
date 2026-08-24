from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self

from app.models.base_models import PanelType


class ProductionSheetCreate(BaseModel):
    production_ref: int = Field(gt=0)
    production_date: datetime
    production_line_id: int = Field(gt=0)
    batch_id: int = Field(gt=0)
    shift_id: int = Field(gt=0)
    panel_type: PanelType
    panel_length: Decimal = Field(max_digits=6, decimal_places=2, gt=0)
    panel_width: Decimal = Field(max_digits=6, decimal_places=2, gt=0)
    panel_thickness: Decimal = Field(max_digits=6, decimal_places=2, gt=0)
    forming_line_speed: float = Field(gt=0)
    press_temperature: float = Field(gt=0)
    press_pressure: float = Field(gt=0)
    press_factor: float = Field(gt=0)
    resin_type_id: int = Field(gt=0)
    production_duration: float = Field(gt=0)
    total_downtime: float = Field(ge=0)
    resin_dosed: Decimal = Field(max_digits=6, decimal_places=2, gt=0)
    paraffin_dosed: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    urea_dosed: Decimal = Field(max_digits=6, decimal_places=2, ge=0)
    percentage_recycled_material: float = Field(ge=0, le=100)
    panels_produced: int = Field(gt=0)
    panels_rejected: int = Field(ge=0)

    @model_validator(mode="after")
    def check_panels_rejected_less_than_produced(self) -> Self:
        if self.panels_rejected > self.panels_produced:
            raise ValueError("Rejected panels cannot be bigger than produced panels")
        return self

    @model_validator(mode="after")
    def check_downtime_less_than_production_duration(self) -> Self:
        if self.total_downtime > self.production_duration:
            raise ValueError("Total downtime cannot be bigger than production duration")
        return self


class ProductionSheetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    production_ref: int
    production_date: datetime
    production_line_id: int
    batch_id: int
    shift_id: int
    panel_type: PanelType
    panel_length: Decimal = Field(max_digits=6, decimal_places=2)
    panel_width: Decimal = Field(max_digits=6, decimal_places=2)
    panel_thickness: Decimal = Field(max_digits=6, decimal_places=2)
    forming_line_speed: float
    press_temperature: float
    press_pressure: float
    press_factor: float
    resin_type_id: int
    production_duration: float
    total_downtime: float
    resin_dosed: Decimal = Field(max_digits=6, decimal_places=2)
    paraffin_dosed: Decimal = Field(max_digits=6, decimal_places=2)
    urea_dosed: Decimal = Field(max_digits=6, decimal_places=2)
    percentage_recycled_material: float
    panels_produced: int
    panels_rejected: int
    rejection_rate: float
    created_at: datetime
    updated_at: datetime


class ProcessParameterAssessmentRead(BaseModel):
    value: float
    status: str


class MaterialEfficiencyRead(BaseModel):
    chemical_total_dosed: Decimal = Field(max_digits=6, decimal_places=2)
    resin_per_accepted_panel: Decimal = Field(max_digits=6, decimal_places=2)
    paraffin_per_accepted_panel: Decimal = Field(max_digits=6, decimal_places=2)
    urea_per_accepted_panel: Decimal = Field(max_digits=6, decimal_places=2)
    chemical_dose_per_accepted_panel: Decimal = Field(max_digits=6, decimal_places=2)


class ProductionSheetOperationalAssessmentRead(BaseModel):
    production_sheet_id: int
    production_ref: int
    accepted_panels: int
    rejection_rate: float
    net_production_time: float
    downtime_rate: float
    quality_status: str
    downtime_status: str
    sustainability_status: str
    process_parameters: dict[str, ProcessParameterAssessmentRead]
    material_efficiency: MaterialEfficiencyRead
    overall_status: str
    flags: list[str]
    main_issue: str | None
