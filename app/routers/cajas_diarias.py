from fastapi import APIRouter, Depends, HTTPException
from app.auth_jwt import get_current_user
from sqlalchemy.orm import Session, joinedload, contains_eager
from sqlalchemy import func, Date, cast
from app.database import get_db
from app import models, schemas
from datetime import date
from typing import Optional
from app.special_types import caja_status

router = APIRouter(
    prefix="/cajas_diarias",
    tags=["Cajas Diarias"],
    dependencies=[Depends(get_current_user)] 
)

@router.get('/trabajador/{id_trabajador}', response_model=schemas.Cajas_DiariasWorker)
def get_trabajador_caja(
    id_trabajador: str,
    db: Session = Depends(get_db)
):
    today = date.today()
    
    print(today)

    caja = db.query(
        models.Cajas_Diarias
    ).options(
        joinedload(
            models.Cajas_Diarias.gastos
        )
    ).filter(
        models.Cajas_Diarias.id_trabajador == id_trabajador ,
        models.Cajas_Diarias.fecha == today
    ).first()

    if not caja:
        raise HTTPException(
            status_code=404, 
            detail="No existe caja diaria para este trabajador"
        )

    total_renovaciones = db.query(func.sum(models.Creditos.monto_total)).filter(
        models.Creditos.id_trabajador == id_trabajador,
        cast(models.Creditos.fecha_inicial, Date) == today,
        models.Creditos.detalles.any(id_producto=1) 
    ).scalar() or 0

    creditos = db.query(models.Creditos).filter(
        models.Creditos.id_trabajador == id_trabajador,
        cast(models.Creditos.fecha_inicial, Date) == today,
        models.Creditos.detalles.any(id_producto=1) 

    ).all()

    caja.renovaciones = total_renovaciones

    pagos = db.query(
        models.Pagos
    ).filter(
        models.Pagos.id_trabajador == id_trabajador,
        models.Pagos.fecha_pago == today
    ).all()

    if(caja):
        return {
            "caja": caja,
            "pagos" : pagos if pagos else [],
            "creditos" : creditos if creditos else []
        }

@router.get('/all/today', response_model=list[schemas.TrabajadoresCajaResponse])
def get_all_cajas(
    db : Session = Depends(get_db)
):
    today = date.today()

    trabajadores = db.query(models.Trabajadores).outerjoin(
        models.Cajas_Diarias, 
        (models.Cajas_Diarias.id_trabajador == models.Trabajadores.id_trabajador) & 
        (models.Cajas_Diarias.fecha == today)
    ).options(contains_eager(models.Trabajadores.cajas_diarias)).all()

    resultado = []
    for t in trabajadores:
        caja_hoy : Optional[models.Cajas_Diarias]= t.cajas_diarias[0] if t.cajas_diarias else None
        
        resultado.append({
            "id_trabajador": t.id_trabajador,
            "nombre": t.nombre,
            "apellido": t.apellido,
            "telefono": t.telefono,
            "id_user": t.id_user,
            "caja": caja_hoy if caja_hoy else None,
        })

    return resultado

@router.post('/create', response_model=schemas.Cajas_DiariasResponse)
def create_caja(
    caja: schemas.Cajas_DiariasCreate,
    db : Session = Depends(get_db)
):
    newCaja = models.Cajas_Diarias(**caja.model_dump())
    db.add(newCaja)
    db.flush()
    db.commit()
    db.refresh(newCaja)
    return newCaja

@router.put('/accept/{id_caja}', response_model=schemas.Cajas_DiariasResponse)
def accept_session(
    id_caja : str,
    db: Session = Depends(get_db)
):
    caja = db.query(
        models.Cajas_Diarias
    ).filter(
        models.Cajas_Diarias.id_caja == id_caja
    ).first()

    print(f"DEBUG: El estado de la caja {id_caja} es: '{caja.status}'")

    if not caja:
        raise HTTPException(status_code=404, detail="La caja no existe")
    
    if caja.status != caja_status.ASIGNADA:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede abrir una caja en estado {caja.status}"
        )
    
    caja.status = caja_status.ABIERTA

    db.commit()
    db.refresh(caja)

    return caja

@router.put('/close/{id_caja}', response_model=schemas.Cajas_DiariasResponse)
def accept_session(
    id_caja : str,
    db: Session = Depends(get_db)
):
    caja = db.query(
        models.Cajas_Diarias
    ).filter(
        models.Cajas_Diarias.id_caja == id_caja
    ).first()

    if not caja:
        raise HTTPException(status_code=404, detail="La caja no existe")
    
    if caja.status != caja_status.ABIERTA:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede cerrar una caja en estado {caja.status}"
        )
    
    caja.status = caja_status.CERRADA

    db.commit()
    db.refresh(caja)

    return caja
    