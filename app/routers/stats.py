from fastapi import APIRouter, Depends
from app.auth_jwt import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models, schemas, special_types
from datetime import date

router = APIRouter(
    prefix='/stats',
    tags=['Stats'],
    dependencies= [Depends(get_current_user)]
)

@router.get('/financial-healt', response_model=schemas.FinantialHealtResponse)
def get_financial_healt(
    db : Session = Depends(get_db)
):
    today = date.today()    

    capital_calle = db.query(
        func.sum(models.Cuotas.monto) - func.coalesce(func.sum(models.Pagos.monto), 0)
    ).select_from(models.Cuotas).outerjoin(
        models.Pagos, models.Cuotas.id_cuota == models.Pagos.id_cuota
    ).filter(
        models.Cuotas.estado != "PAGADA"
    ).scalar() or 0

    meta_cobro = db.query(
        func.sum(models.Cuotas.monto) - func.coalesce(func.sum(models.Pagos.monto), 0)
    ).select_from(models.Cuotas).outerjoin(
        models.Pagos, models.Cuotas.id_cuota == models.Pagos.id_cuota
    ).filter(
        models.Cuotas.fecha_vencimiento == today,
        models.Cuotas.estado != 'PAGADA'
    ).scalar() or 0

    montos_base = db.query(
        func.sum(models.Cajas_Diarias.monto_base)
    ).filter(
        func.date(models.Cajas_Diarias.fecha) == today
    ).scalar() or 0
    
    return {
        'capital_calle': capital_calle,
        'meta_hoy': meta_cobro,
        'total_base': montos_base
    }