from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app import schemas, models
from datetime import date
from app.auth_jwt import get_current_user

router = APIRouter(
    prefix='/cuotas',
    tags=['Cuotas'],
    dependencies=[Depends(get_current_user)]
)

@router.get("/", response_model=schemas.CuotasResponse)
def getCuotas(db: Session = Depends(get_db)):
    query = db.query(models.Cuotas)
    cuotas = query.all()
    if cuotas:
        return cuotas
    raise HTTPException(status_code=401, detail="Cuota no encontrada")

@router.get('/{id_cuota}', response_model=schemas.CuotasBaseResponse)
def get_cuota(
    id_cuota: str,
    db: Session = Depends(get_db)
):
    cuota = db.query(
        models.Cuotas
    ).filter(
        models.Cuotas.id_cuota == id_cuota
    ).first()

    return cuota

@router.get('/{id_trabajador}/route', response_model=list[schemas.CuotasProgressResponse])
def get_trabajador_route(
    id_trabajador: str,
    db: Session = Depends(get_db)
):
    today = date.today()

    cuotas_pendientes = db.query(
        models.Cuotas
    ).options(
        joinedload(
            models.Cuotas.credito
        )
    ).join(
        models.Creditos, models.Cuotas.id_credito == models.Creditos.id_credito
    ).filter(
        models.Creditos.id_trabajador == id_trabajador,
        func.date(models.Cuotas.fecha_vencimiento) == today
    ).all()

    if cuotas_pendientes:
        return cuotas_pendientes
    
    return []

@router.get('/expired/{id_trabajador}', response_model=list[schemas.CuotasProgressResponse])
def get_trabajador_route(
    id_trabajador: str,
    db: Session = Depends(get_db)
):
    cuotas_pendientes = db.query(
        models.Cuotas
    ).options(
        joinedload(
            models.Cuotas.credito
        )
    ).join(
        models.Creditos, models.Cuotas.id_credito == models.Creditos.id_credito
    ).filter(
        models.Creditos.id_trabajador == id_trabajador,
        models.Cuotas.estado == 'VENCIDA'
    ).all()

    if cuotas_pendientes:
        return cuotas_pendientes
    
    return []
