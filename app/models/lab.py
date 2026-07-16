from __future__ import annotations
from sqlalchemy import Integer, ForeignKey, DateTime, func, Enum, Numeric
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base_models import ProductionLine, Shift, PanelType


class LabTest(Base):
    __tablename__ = "lab_tests"

    id: Mapped[int] = mapped_column(primary_key=True)
    lab_ref: Mapped[int] = mapped_column(Integer, unique=True)
    lab_test_date: Mapped[datetime] = mapped_column(DateTime)
    production_line_id: Mapped[int] = mapped_column(ForeignKey("production_lines.id"))
    panel_thickness:Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    batch_id: Mapped[int] = mapped_column()
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"))
    panel_type: Mapped[PanelType] = mapped_column(Enum(PanelType))
    
    actual_thickness: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    calculated_density: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    moisture_content: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    internal_bond: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    bending_strength: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    elastic_modulus: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    thickness_swelling: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    water_absorption: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    formaldehyde_emission: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    formaldehyde_content: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    production_line: Mapped["ProductionLine"] = relationship("ProductionLine", back_populates="lab_tests")
    shift: Mapped["Shift"] = relationship("Shift", back_populates="lab_tests")







