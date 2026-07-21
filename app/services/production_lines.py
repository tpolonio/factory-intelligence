from fastapi import HTTPException, status
from app.models.base_models import ProductionLine
from app.schemas.base_models import ProductionLineCreate
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError



def create_production_line(
        production_line_input: ProductionLineCreate, 
        db: Session
        ) -> ProductionLine:

    normalized_name = normalize_line_name(production_line_input.name)

    ensure_unique_line_name(normalized_name, db)

    new_production_line = ProductionLine(name=normalized_name)

    try: 
        db.add(new_production_line)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Production Line with that name already exists."
        )
    db.refresh(new_production_line)

    return new_production_line


def list_production_lines(
        name: str | None, 
        db: Session,
        limit: int,
        offset: int,
    ) -> list[ProductionLine]:

    statement = select(ProductionLine)
    if name:
        statement = statement.where(ProductionLine.name == normalize_line_name(name))

    statement = statement.offset(offset).limit(limit)
    return db.scalars(statement).all()


def get_production_line(line_id: int, db: Session) -> ProductionLine:

    production_line = db.get(ProductionLine, line_id)
    if not production_line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Production Line not found.")

    return production_line




def ensure_unique_line_name(line_name: str, db: Session):

    statement = select(ProductionLine).where(ProductionLine.name == normalize_line_name(line_name))
    existing_production_line = db.scalars(statement).first()
    if existing_production_line:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Production Line with that name already exists."
        )
    return 


def normalize_line_name(line_name: str):

    normalized_line_name = line_name.strip().lower()
    return normalized_line_name