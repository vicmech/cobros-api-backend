from fastapi import APIRouter, Depends, HTTPException
from app.auth_jwt import get_current_user
from app import schemas, models
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import func
from app.database import get_db
from datetime import date


router = APIRouter(
    prefix= '/trabajadores',
    tags= ['Trabajadores'],
    dependencies=[Depends(get_current_user)]
)

@router.get("/", response_model=list[schemas.TrabajadoresResponse])
def list_trabajadores(
    db: Session = Depends(get_db)):

    query = db.query(models.Trabajadores)
    
    return query.all()

@router.get('/summary', response_model=list[schemas.TrabajadoresProgressSummary])
def getWorkerSummary(
    db: Session = Depends(get_db)
):
    today = date.today()
    
    today_pays = db.query(
        models.Pagos.id_trabajador,
        func.sum(models.Pagos.monto).label("total_cobrado")
    ).filter(
        func.date(models.Pagos.fecha_pago) == today
    ).group_by(
        models.Pagos.id_trabajador
    ).subquery()

    today_paymentFees = db.query(
        models.Trabajadores.id_trabajador,
        func.sum(models.Cuotas.monto).label("total_objetivo")
    ).join(
        models.Creditos, models.Trabajadores.id_trabajador == models.Creditos.id_trabajador
    ).join(
        models.Cuotas, models.Creditos.id_credito == models.Cuotas.id_credito
    ).filter(
        func.date(models.Cuotas.fecha_vencimiento) == today
    ).group_by(
        models.Trabajadores.id_trabajador
    ).subquery()

    results = db.query(
        models.Trabajadores.id_trabajador,
        models.Trabajadores.nombre,
        models.Trabajadores.apellido,
        models.Trabajadores.id_user,
        models.Trabajadores.telefono,
        func.coalesce(today_pays.c.total_cobrado, 0).label("cobrado_total"),
        func.coalesce(today_paymentFees.c.total_objetivo, 0).label("cuotas_total")
    ).outerjoin(
        today_pays, models.Trabajadores.id_trabajador == today_pays.c.id_trabajador
    ).outerjoin(
        today_paymentFees, models.Trabajadores.id_trabajador == today_paymentFees.c.id_trabajador
    ).all()

    return results

@router.get('/{id_trabajador}/daily_activity', response_model=schemas.TrabajadorDailyActivity)
def getWorkerDailyActivity(
    id_trabajador: str,
    db: Session = Depends(get_db)
):
    today = date.today()
    
    trabajador = db.query(
        models.Trabajadores
    ).filter(
        models.Trabajadores.id_trabajador == id_trabajador
    ).first()

    cobros_realizados = db.query(
        models.Pagos
    ).options(
        joinedload(
            models.Pagos.cuota
        ).joinedload(
            models.Cuotas.credito
        ).joinedload(
            models.Creditos.cliente
        )
    ).filter(
        models.Pagos.id_trabajador == id_trabajador,
        func.date(models.Pagos.fecha_pago) == today
    ).all()

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

    return {
        "trabajador" : trabajador,
        "cobros_realizados": cobros_realizados,
        "cuotas_pendientes": cuotas_pendientes
    }

@router.get("/{id_trabajador}", response_model=schemas.TrabajadoresResponse)
def get_trabajador(id_trabajador: str, db: Session = Depends(get_db)):

    query = db.query(models.Trabajadores).filter(models.Trabajadores.id_trabajador == id_trabajador)
    db_trabajador = query.first()
    if db_trabajador:
        return db_trabajador
    raise HTTPException(status_code=404, detail="Trabajador no encontrado")

@router.get('/{id_trabajador}/route', response_model=schemas.TrabajadoresRouteResponse)
def get_trabajador_route(
    id_trabajador: str,
    db: Session = Depends(get_db)
):
    today = date.today()

    trabajador = db.query(
        models.Trabajadores
    ).join(
        models.Trabajadores.creditos
    ).join(
        models.Creditos.cuotas
    ).filter(
        models.Trabajadores.id_trabajador == id_trabajador
    ).filter(
        models.Cuotas.fecha_vencimiento == today
    ).options(
        contains_eager(models.Trabajadores.creditos)
        .contains_eager(models.Creditos.cuotas) 
    ).first()

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

    if trabajador:
        return trabajador
    
    return {}

@router.post("/create", response_model=schemas.TrabajadoresResponse)
def create_trabajador(trabajador: schemas.TrabajadoresCreate, db: Session = Depends(get_db)):
    new_trabajador = models.Trabajadores(**trabajador.model_dump())
    db.add(new_trabajador)
    db.commit()
    db.refresh(new_trabajador)
    return new_trabajador

