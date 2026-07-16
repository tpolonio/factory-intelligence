from __future__ import annotations
from sqlalchemy import ForeignKey, DateTime, Numeric, Enum, Float as SaFloat, func, case, cast
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from app.core.database import Base
from app.models.base_models import ProductionLine, Shift, ResinType, PanelType

class ProductionSheet(Base):
    __tablename__ = "production_sheets"
    
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
            ((cls.panels_produced == None) | (cls.panels_produced == 0), 0.0),
            else_=(cast(cls.panels_rejected, SaFloat) / cast(cls.panels_produced, SaFloat)) * 100
        )