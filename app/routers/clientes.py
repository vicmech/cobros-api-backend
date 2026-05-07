from fastapi import APIRouter, Depends, HTTPException
from app import models, schemas
from app.auth_jwt import get_current_user
from typing import Optional
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import func
from fastapi import Depends
from app.database import get_db

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    dependencies=[Depends(get_current_user)] 
)

@router.post("/create", response_model=schemas.ClientesResponse)
def create_client(cliente: schemas.ClientesCreate, db: Session = Depends(get_db)):

    #ADD THE EXCEPTION, DONT FORGET IT

    #If the exception is not raised, it creates a new client
    new_cliente = models.Clientes(**cliente.model_dump())
    db.add(new_cliente)
    db.commit()
    db.refresh(new_cliente)
    return new_cliente

@router.get("/simple_list", response_model=list[schemas.ClientesSimpleResponse])
def list_simple_clients(
    db: Session = Depends(get_db),
    #Query parameters
    nombre : Optional[str] = None,
    apellido : Optional[str] = None,
    id_distrito : Optional[int] = None, 
):
    
    query = db.query(models.Clientes).options(joinedload(models.Clientes.distrito))

    if id_distrito:
        query = query.filter(models.Clientes.id_distrito == id_distrito)
    
    if nombre:
        query = query.filter(models.Clientes.nombre == nombre)
    
    if apellido:
        query = query.filter(models.Clientes.apellido == apellido)

    return query.all()

@router.get("/{id_cliente}", response_model=schemas.ClienteWithDistrito)
def list_clients(
    #Query parameters
    id_cliente: str,
    nombre : Optional[str] = None,
    apellido : Optional[str] = None,
    id_distrito : Optional[int] = None, 
    db: Session = Depends(get_db)):
    
    query = db.query(models.Clientes).filter(
        models.Clientes.id_cliente == id_cliente
    ).options(
        joinedload(models.Clientes.distrito)
        .joinedload(models.Distritos.provincia)
    )

    if id_distrito:
        query = query.filter(models.Clientes.id_distrito == id_distrito)
    
    if nombre:
        query = query.filter(models.Clientes.nombre == nombre)
    
    if apellido:
        query = query.filter(models.Clientes.apellido == apellido)

    return query.first()

@router.get("/full_credit_info/{id_cliente}", response_model=schemas.ClientesResponse)
def get_client(
    id_cliente: str, 
    db: Session = Depends(get_db)
):
    subquery_pagos = db.query(
        models.Pagos.id_credito,
        func.sum(models.Pagos.monto).label('total_pagado')
    ).group_by(models.Pagos.id_credito).subquery()
    
    query = db.query(models.Clientes).join(
        models.Creditos, models.Clientes.id_cliente == models.Creditos.id_cliente
    ).outerjoin(
        subquery_pagos, models.Creditos.id_credito == subquery_pagos.c.id_credito
    ).filter(
        models.Clientes.id_cliente == id_cliente,
        models.Creditos.monto_total > func.coalesce(subquery_pagos.c.total_pagado, 0)
    ).options(
        joinedload(models.Clientes.distrito)
            .joinedload(models.Distritos.provincia),

        contains_eager(models.Clientes.creditos)
            .joinedload(models.Creditos.detalles)
                .joinedload(models.Detalles.producto)
    )
    
    if query.first():
        return query.first()
    raise HTTPException(status_code=404, detail="Cliente no encontrado")
