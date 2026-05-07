from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.auth_jwt import get_current_user
from app import schemas, models
from app.schemas import GastosResponse

router = APIRouter(
    prefix="/gastos",
    tags=["Gastos"],
    dependencies=[Depends(get_current_user)] 
)

@router.get("/", response_model=list[GastosResponse])
def list_gastos(
    id_caja: Optional[str] = None,
    db: Session = Depends(get_db)):

    query = db.query(models.Gastos)

    if id_caja:
        query = query.filter(models.Gastos.id_caja == id_caja)
    
    return query.all()

@router.get("/by_date/{fecha}", response_model=schemas.GastosResponse)
def get_gasto(fecha: str, db: Session = Depends(get_db)):
    query = db.query(models.Gastos).join(models.Cajas_Diarias).filter(
        models.Cajas_Diarias.fecha == fecha).all()
    if query:
        return query
    raise HTTPException(status_code=404, detail="Gasto no encontrado")

@router.post("/create", response_model=schemas.GastosResponse)
def create_gasto(
    gasto: schemas.GastosCreate, 
    db: Session = Depends(get_db)
):

    new_gasto = models.Gastos(**gasto.model_dump())
    db.add(new_gasto)
    db.commit()
    db.refresh(new_gasto)
    return new_gasto
