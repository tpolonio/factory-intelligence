from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.base_models import ProductionLineCreate, ProductionLineRead
from app.models.base_models import ProductionLine
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select

router = APIRouter()

@router.get("/health")
def production_health_check():
    return {"domain": "production","status": "healthy"}


@router.post("/lines", response_model=ProductionLineRead, status_code=201)
def add_new_production_line(production_line_input: ProductionLineCreate, db: Session = Depends(get_db)):

    statement = select(ProductionLine).where(ProductionLine.name == production_line_input.name)
    existing_production_line = db.scalars(statement).first()
    if existing_production_line:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Production Line with that name already exists."
        )

    new_production_line = ProductionLine(name=production_line_input.name)

    db.add(new_production_line)
    db.commit()
    db.refresh(new_production_line)

    return new_production_line

@router.get("/lines", response_model=list[ProductionLineRead])
def list_production_lines(name: str | None = None, db: Session = Depends(get_db)):

    statement = select(ProductionLine)
    if name:
        statement = statement.where(ProductionLine.name == name)

    return db.scalars(statement).all()

@router.get("/lines/{line_id}", response_model=ProductionLineRead)
def show_production_line(line_id: int, db: Session = Depends(get_db)):
    
    production_line = db.get(ProductionLine, line_id)
    if not production_line:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Production Line not found.")

    return production_line