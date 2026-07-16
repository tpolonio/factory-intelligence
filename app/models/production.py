from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, ForeignKey, DateTime, Numeric, Enum, Float as SaFloat, func, case, cast
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.database import Base
from app.models.base_models import PanelType

if TYPE_CHECKING:
    from app.models.base_models import ProductionLine, ResinType, Shift

class ProductionSheet(Base):
    __tablename__ = "production_sheets"
    __table_args__ = (
        CheckConstraint("panel_length > 0", name="ck_production_sheets_panel_length_positive"),
        CheckConstraint("panel_width > 0", name="ck_production_sheets_panel_width_positive"),
        CheckConstraint("panel_thickness > 0", name="ck_production_sheets_panel_thickness_positive"),
        CheckConstraint("forming_line_speed >= 0", name="ck_production_sheets_forming_line_speed_nonnegative"),
        CheckConstraint("press_temperature >= 0", name="ck_production_sheets_press_temperature_nonnegative"),
        CheckConstraint("press_pressure >= 0", name="ck_production_sheets_press_pressure_nonnegative"),
        CheckConstraint("press_factor >= 0", name="ck_production_sheets_press_factor_nonnegative"),
        CheckConstraint("production_duration >= 0", name="ck_production_sheets_production_duration_nonnegative"),
        CheckConstraint("total_downtime >= 0", name="ck_production_sheets_total_downtime_nonnegative"),
        CheckConstraint("resin_dosed >= 0", name="ck_production_sheets_resin_dosed_nonnegative"),
        CheckConstraint("paraffin_dosed >= 0", name="ck_production_sheets_paraffin_dosed_nonnegative"),
        CheckConstraint("urea_dosed >= 0", name="ck_production_sheets_urea_dosed_nonnegative"),
        CheckConstraint(
            "percentage_recycled_material >= 0 AND percentage_recycled_material <= 100",
            name="ck_production_sheets_percentage_recycled_material_range",
        ),
        CheckConstraint("panels_produced >= 0", name="ck_production_sheets_panels_produced_nonnegative"),
        CheckConstraint("panels_rejected >= 0", name="ck_production_sheets_panels_rejected_nonnegative"),
        CheckConstraint(
            "panels_rejected <= panels_produced",
            name="ck_production_sheets_panels_rejected_lte_produced",
        ),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    production_ref: Mapped[int] = mapped_column(unique=True, index=True)
    production_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    production_line_id: Mapped[int] = mapped_column(ForeignKey("production_lines.id"))
    batch_id: Mapped[int] = mapped_column()
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"))
    
    panel_type: Mapped[PanelType] = mapped_column(Enum(PanelType))
    panel_length: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    panel_width: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    panel_thickness: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))

    forming_line_speed: Mapped[float] = mapped_column()
    press_temperature: Mapped[float] = mapped_column()
    press_pressure: Mapped[float] = mapped_column()
    press_factor: Mapped[float] = mapped_column()

    resin_type_id: Mapped[int] = mapped_column(ForeignKey("resin_types.id"))
    production_duration: Mapped[float] = mapped_column()
    total_downtime: Mapped[float] = mapped_column()

    resin_dosed: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    paraffin_dosed: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    urea_dosed: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    percentage_recycled_material: Mapped[float] = mapped_column()

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    panels_produced: Mapped[int] = mapped_column()
    panels_rejected: Mapped[int] = mapped_column()
    resin_type: Mapped["ResinType"] = relationship("ResinType", back_populates="production_sheets")
    production_line: Mapped["ProductionLine"] = relationship("ProductionLine", back_populates="production_sheets")
    shift: Mapped["Shift"] = relationship("Shift", back_populates="production_sheets")

    @hybrid_property
    def rejection_rate(self) -> float:
        if not self.panels_produced:
            return 0.0
        return (self.panels_rejected or 0) / self.panels_produced * 100

    @rejection_rate.expression
    def rejection_rate(cls):
        return case(
            ((cls.panels_produced.is_(None)) | (cls.panels_produced == 0), 0.0),
            else_=(cast(func.coalesce(cls.panels_rejected, 0), SaFloat) / cast(cls.panels_produced, SaFloat)) * 100
        )
