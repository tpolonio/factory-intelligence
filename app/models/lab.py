from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List
from app.core.database import Base
from app.models.base_models import ProductionLine, Shift


class LabTest(Base):
    __tablename__ = "lab_tests"
    id: Mapped[int] = mapped_column(primary_key=True)
    lab_ref: Mapped[int] = mapped_column(Integer, unique=True)
    lab_test_date: Mapped[datetime] = mapped_column(DateTime)
    production_line_id: Mapped[int] = mapped_column(ForeignKey("production_lines.id"))
    panel_type: Mapped[str] = mapped_column(String(50))
    panel_thickness: Mapped[float] = mapped_column(Float)
    batch_id: Mapped[int] = mapped_column(Integer)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"))
    actual_thickness: Mapped[float] = mapped_column(Float)
    calculated_density: Mapped[float] = mapped_column(Float)
    moisture_content: Mapped[float] = mapped_column(Float)
    internal_bond: Mapped[float] = mapped_column(Float)
    bending_strength: Mapped[float] = mapped_column(Float)
    elastic_modulus: Mapped[float] = mapped_column(Float)
    thickness_swelling: Mapped[float] = mapped_column(Float)
    water_absorption: Mapped[float] = mapped_column(Float)
    formaldehyde_emission: Mapped[float] = mapped_column(Float)
    formaldehyde_content: Mapped[float] = mapped_column(Float)
    production_line: Mapped["ProductionLine"] = relationship("ProductionLine", back_populates="lab_tests")
    shift: Mapped["Shift"] = relationship("Shift", back_populates="lab_tests")







