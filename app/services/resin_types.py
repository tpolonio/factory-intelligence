from fastapi import HTTPException, status
from app.models.base_models import ResinType
from app.schemas.base_models import ResinTypeCreate
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError



def create_resin_type(
        resin_type_input: ResinTypeCreate, 
        db: Session
        ) -> ResinType:

    resin_type_name = clean_resin_type_name(resin_type_input.name)

    ensure_unique_resin_type_name(resin_type_name, db)

    new_resin_type = ResinType(name=resin_type_name)

    try: 
        db.add(new_resin_type)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resin Type with that name already exists."
        )
    db.refresh(new_resin_type)

    return new_resin_type


def list_resin_types(
        name: str | None, 
        db: Session,
        limit: int,
        offset: int,
    ) -> list[ResinType]:

    statement = select(ResinType)
    if name:
        lookup_name = normalize_resin_type_lookup(name)
        statement = statement.where(func.lower(ResinType.name) == lookup_name)

    statement = statement.offset(offset).limit(limit)
    return db.scalars(statement).all()


def get_resin_type(resin_type_id: int, db: Session) -> ResinType:

    resin_type = db.get(ResinType, resin_type_id)
    if not resin_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Resin Type not found.")

    return resin_type

def ensure_unique_resin_type_name(resin_type_name: str, db: Session):

    lookup_name = normalize_resin_type_lookup(resin_type_name)
    statement = select(ResinType).where(func.lower(ResinType.name) == lookup_name)
    existing_resin_type = db.scalars(statement).first()
    if existing_resin_type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Resin Type with that name already exists."
        )
    return 


def clean_resin_type_name(resin_type_name: str):

    return resin_type_name.strip()


def normalize_resin_type_lookup(resin_type_name: str):

    return resin_type_name.strip().lower()
