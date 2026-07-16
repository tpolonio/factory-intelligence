from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PyEnum
from typing import List
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.lab import LabTest

class ProductionLine(Base):
    __tablename__ = "production_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    lab_tests: Mapped [List["LabTest"]] = relationship("LabTest", back_populates="production_line") 

class Shift(Base):
    __tablename__ = "shifts"
    id: Mapped[int] = mapped_column(primary_key=True)
    shift_letter: Mapped[str] = mapped_column(String(1), unique=True)
    press_operator: Mapped[str] = mapped_column(String(50))
    line_operator: Mapped[str] = mapped_column(String(50))
    lab_tests: Mapped [List["LabTest"]] = relationship("LabTest", back_populates="shift")

class ResinType(Base):
    __tablename__ = "resin_types"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

class PanelType(str, PyEnum):
    MDF = "MDF"
    PB = "Particleboard"
    OSB = "OSB"
    HDF = "HDF"
    HID = "MDF Hydro"
    IGN = "MDF Igni"
