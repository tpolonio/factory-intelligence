from fastapi import HTTPException, status
from app.models.base_models import Shift
from app.schemas.base_models import ShiftCreate
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

def create_shift(
        shift_input: ShiftCreate,
        db: Session
        ) -> Shift:

    normalized_shift_letter = normalize_shift_letter(shift_input.shift_letter)
    normalized_press_operator_name = clean_operator_name(shift_input.press_operator)
    normalized_line_operator_name = clean_operator_name(shift_input.line_operator)

    validate_shift_letter(normalized_shift_letter, db)

    new_shift = Shift(
        shift_letter=normalized_shift_letter, 
        press_operator=normalized_press_operator_name,
        line_operator=normalized_line_operator_name
    )

    try: 
        db.add(new_shift)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shift with that letter already exists."
        )
    db.refresh(new_shift)

    return new_shift


def list_shifts(
        shift_letter: str | None,
        press_operator: str | None,
        line_operator: str | None,
        db: Session,
        limit: int,
        offset: int,
    ) -> list[Shift]:

    statement = select(Shift)
    if shift_letter:
        statement = statement.where(Shift.shift_letter == normalize_shift_letter(shift_letter))

    if press_operator:
        statement = statement.where(func.lower(Shift.press_operator) == normalize_operator_lookup(press_operator))

    if line_operator:
        statement = statement.where(func.lower(Shift.line_operator) == normalize_operator_lookup(line_operator))

    statement = statement.offset(offset).limit(limit)
    return db.scalars(statement).all()


def get_shift(shift_id: int, db: Session) -> Shift:

    shift = db.get(Shift, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Shift not found.")

    return shift


def validate_shift_letter(shift_letter: str, db: Session):

    normalized_shift_letter = normalize_shift_letter(shift_letter)

    if len(normalized_shift_letter) != 1:
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Shift letter must be exactly 1 character."
                )

    statement = select(Shift).where(Shift.shift_letter == normalized_shift_letter)
    existing_shift_letter = db.scalars(statement).first()
    if existing_shift_letter:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shift with that letter already exists."
        )
    return 


def normalize_shift_letter(shift_letter: str):
    return shift_letter.strip().upper()


def clean_operator_name(operator_name: str):
    return operator_name.strip()

def normalize_operator_lookup(operator_name: str):
    return operator_name.strip().lower()