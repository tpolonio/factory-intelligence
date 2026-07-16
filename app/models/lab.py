from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import CheckConstraint, Integer, ForeignKey, DateTime, func, Enum, Numeric
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base_models import PanelType

if TYPE_CHECKING:
    from app.models.base_models import ProductionLine, Shift


class LabTest(Base):
    __tablename__ = "lab_tests"
    __table_args__ = (
        CheckConstraint("panel_thickness > 0", name="ck_lab_tests_panel_thickness_positive"),
        CheckConstraint("actual_thickness > 0", name="ck_lab_tests_actual_thickness_positive"),
        CheckConstraint("calculated_density >= 0", name="ck_lab_tests_calculated_density_nonnegative"),
        CheckConstraint("moisture_content >= 0", name="ck_lab_tests_moisture_content_nonnegative"),
        CheckConstraint("internal_bond >= 0", name="ck_lab_tests_internal_bond_nonnegative"),
        CheckConstraint("bending_strength >= 0", name="ck_lab_tests_bending_strength_nonnegative"),
        CheckConstraint("elastic_modulus >= 0", name="ck_lab_tests_elastic_modulus_nonnegative"),
        CheckConstraint("thickness_swelling >= 0", name="ck_lab_tests_thickness_swelling_nonnegative"),
        CheckConstraint("water_absorption >= 0", name="ck_lab_tests_water_absorption_nonnegative"),
        CheckConstraint("formaldehyde_emission >= 0", name="ck_lab_tests_formaldehyde_emission_nonnegative"),
        CheckConstraint("formaldehyde_content >= 0", name="ck_lab_tests_formaldehyde_content_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lab_ref: Mapped[int] = mapped_column(Integer, unique=True)
    lab_test_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    production_line_id: Mapped[int] = mapped_column(ForeignKey("production_lines.id"))
    panel_thickness: Mapped[Decimal] = mapped_column(Numeric(precision=6, scale=2))
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





