from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float
from datetime import datetime
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
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