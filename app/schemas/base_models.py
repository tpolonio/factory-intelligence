from pydantic import BaseModel, ConfigDict

class ProductionLineCreate(BaseModel):
    name: str

class ProductionLineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

class ShiftCreate(BaseModel):
    shift_letter: str
    press_operator: str
    line_operator: str


class ShiftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    shift_letter: str
    press_operator: str
    line_operator: str


class ResinTypeCreate(BaseModel):
    name: str


class ResinTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
