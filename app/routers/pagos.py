from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.auth_jwt import get_current_user
from app import schemas, models
from app.special_types import pay_method

router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"],
    dependencies=[Depends(get_current_user)] 
)

@router.post("/create", response_model=schemas.PagosResponse)
def create_pago(
    pago: schemas.PagosCreate, 
    db: Session = Depends(get_db)
):
    new_pago = models.Pagos(**pago.model_dump())
    db.add(new_pago)
    db.flush()

    total_pagado = db.query(
        func.sum(models.Pagos.monto)
    ).filter(
        models.Pagos.id_cuota == pago.id_cuota
    ).scalar() or 0

    cuota = db.query(
        models.Cuotas
    ).filter(
        models.Cuotas.id_cuota == pago.id_cuota
    ).first()

    if cuota:
        if total_pagado >= cuota.monto:
            cuota.estado = "PAGADA"
        elif total_pagado > 0:
            cuota.estado = "ABONO_PARCIAL"
        else:
            cuota.estado = "PENDIENTE"


    db.commit()
    db.refresh(new_pago)
    return new_pago

@router.get("/", response_model=list[schemas.PagosResponse])
def list_pagos(
    id_credito: Optional[str] = None,
    id_trabajador: Optional[str] = None,
    metodo_pago: Optional[pay_method] = None,
    db: Session = Depends(get_db)):

    query = db.query(models.Pagos)

    if id_credito:
        query = query.filter(models.Pagos.id_credito == id_credito)
    
    if id_trabajador:
        query = query.filter(models.Pagos.id_trabajador == id_trabajador)
    
    return query.all()

@router.get("/trabajador/{id_trabajador}/", response_model=list[schemas.PagosResponse])
def list_pagos_trabajador(
    id_trabajador: str,
    metodo_pago: Optional[pay_method] = None,
    fecha: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Pagos).filter(
        models.Pagos.id_trabajador == id_trabajador
    )

    if metodo_pago:
        query = query.filter(models.Pagos.metodo_pago == metodo_pago)

    if fecha:
        query = query.filter(models.Pagos.fecha_pago == fecha)
        
    query = query.options(
        joinedload(models.Pagos.credito)
            .joinedload(models.Creditos.cliente)
    )
    return query.all()

@router.get("/{id_pago}/", response_model=schemas.PagosResponse)
def get_pago(id_pago: str, db: Session = Depends(get_db)):
    query = db.query(models.Pagos).filter(models.Pagos.id_pago == id_pago)
    db_pago = query.first()
    if db_pago:
        return db_pago
    raise HTTPException(status_code=404, detail="Pago no encontrado")