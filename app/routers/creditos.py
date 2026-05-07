from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload, contains_eager, outerjoin
from sqlalchemy import func, case
from typing import Optional
from app.database import get_db
from app.auth_jwt import get_current_user
from app import schemas, models
from datetime import timedelta, date

DIAS_POR_INTERVALO = {
    "DIARIO": 1,
    "SEMANAL": 7,
    "QUINCENAL": 15,
    "MENSUAL": 30
}

router = APIRouter(
    prefix="/creditos",
    tags=["Creditos"],
    dependencies=[Depends(get_current_user)] 
)

@router.post("/create", response_model=schemas.CreditosFullResponse)
def create_credito(credito: schemas.CreditosCreate, db: Session = Depends(get_db)):
    print(credito)
    credito_data = credito.model_dump()
    detalles_data = credito_data.pop("detalles")

    dias_salto = DIAS_POR_INTERVALO.get(credito.intervalo_cobro.upper(), 1)

    try:
        new_credito = models.Creditos(
            **credito_data, 
        )
        
        db.add(new_credito)
        db.flush()

        for item in detalles_data:
            id_producto = item["id_producto"] 
            
            nuevo_detalle = models.Detalles(
                id_credito=new_credito.id_credito,
                id_producto=id_producto,
                cantidad=item["cantidad"]
            )
            db.add(nuevo_detalle)

        fecha_inicial = credito.fecha_inicial
        fecha_final = credito.fecha_final
        monto_total = credito.monto_total

        # Calculamos cuántas cuotas caben en el tiempo del crédito
        dias_totales = (fecha_final - fecha_inicial).days
        num_cuotas = dias_totales // dias_salto

        if num_cuotas > 0:
            monto_cuota_entero = int(monto_total // num_cuotas)
            
            residuo = monto_total - (monto_cuota_entero * (num_cuotas - 1))
            
            proxima_fecha = fecha_inicial + timedelta(days=dias_salto)
            nro_cuota = 1
            
            while nro_cuota <= num_cuotas:
                monto_final_cuota = residuo if nro_cuota == 1 else monto_cuota_entero
                
                if monto_final_cuota > 0:
                    nueva_cuota = models.Cuotas(
                        nro_cuota=nro_cuota,
                        id_credito=new_credito.id_credito,
                        monto=monto_final_cuota,
                        fecha_vencimiento=proxima_fecha,
                        estado="PENDIENTE"
                    )
                    db.add(nueva_cuota)
                
                nro_cuota += 1
                proxima_fecha += timedelta(days=dias_salto)

        db.commit()
        db.refresh(new_credito)
        return new_credito

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail="Error al procesar el crédito y sus detalles")

@router.get("/", response_model=list[schemas.CreditosFullResponse])
def list_creditos(
    id_cliente: Optional[str] = None,
    id_trabajador: Optional[str] = None,
    db: Session = Depends(get_db)):

    query = db.query(models.Creditos)

    if id_cliente:
        query = query.filter(models.Creditos.id_cliente == id_cliente)
    
    if id_trabajador:
        query = query.filter(models.Creditos.id_trabajador == id_trabajador)
    
    return query.all()

@router.get('/summary', response_model=list[schemas.CreditoCardSummary])
def get_creditos_summary(
    db : Session = Depends(get_db)
):
    today = date.today()
    # 1. Calculamos el monto pagado (Suma de cuotas con status 'PAGADA')
    total_pagado = func.coalesce(func.sum(models.Pagos.monto), 0)

    # 2. Buscamos la fecha de la próxima cuota (La fecha mínima que sea >= hoy y no esté pagada)
    proxima_cuota_fecha = func.min(
        case(
            ((models.Cuotas.estado != "PAGADA"), 
             models.Cuotas.fecha_vencimiento),
            else_=None
        )
    )

    query = db.query(
        models.Creditos.id_credito,
        models.Creditos.intervalo_cobro,
        models.Creditos.fecha_inicial,
        models.Creditos.fecha_final,
        models.Creditos.tiempo_credito,
        models.Creditos.monto_total,
        models.Creditos.origen_monto,
        total_pagado.label('monto_pagado'),
        (models.Creditos.monto_total - total_pagado).label('monto_restante'),
        proxima_cuota_fecha.label('proxima_cuota'),
        func.concat(models.Clientes.nombre, ' ', models.Clientes.apellido).label('nombre_cliente')
    ).select_from(
        models.Creditos
    ).join(
        models.Clientes, models.Creditos.id_cliente == models.Clientes.id_cliente
    ).join(
        models.Cuotas
    ).outerjoin(
        models.Pagos, models.Cuotas.id_cuota == models.Pagos.id_cuota
    ).group_by(
        models.Creditos.id_credito,
        models.Creditos.intervalo_cobro,
        models.Creditos.fecha_inicial,
        models.Creditos.fecha_final,
        models.Creditos.tiempo_credito,
        models.Creditos.monto_total,
        models.Creditos.origen_monto,
        models.Clientes.id_cliente,
        models.Clientes.nombre,
        models.Clientes.apellido
    ).having(
        # Solo créditos que aún tengan algo por cobrar
        (models.Creditos.monto_total - total_pagado) > 0
    )

    return query.all()

@router.get("/{id_credito}", response_model=schemas.CreditosFullResponse)
def get_credito(id_credito: str, db: Session = Depends(get_db)):
    
    query = db.query(models.Creditos).filter(
        models.Creditos.id_credito == id_credito
    ).options(
        joinedload(models.Creditos.pagos)
    )
    
    if query:
        return query.first()
    else:
        raise HTTPException(status_code=404, detail="Credito no encontrado")

@router.get("/clientes/{id_cliente}/credito-activo", response_model=Optional[schemas.CreditosFullResponse])
def read_active_credit(id_cliente: str, db: Session = Depends(get_db)):
    credito_activo_id = db.query(models.Cuotas.id_credito)\
        .join(models.Creditos)\
        .filter(
            models.Creditos.id_cliente == id_cliente,
            models.Cuotas.estado.in_(['PENDIENTE', 'VENCIDA']) 
        ).first()

    if not credito_activo_id:
        return None
    
    credito = db.query(models.Creditos)\
        .filter(models.Creditos.id_credito == credito_activo_id[0])\
        .options(
            joinedload(models.Creditos.cuotas).joinedload(models.Cuotas.pagos),
            joinedload(models.Creditos.trabajador),
            joinedload(models.Creditos.cliente)
        )\
        .first()
        
    return credito

@router.get('/{id_credito}/full-info', response_model=schemas.creditos.CreditosFullResponse)
def getCreditFullInfo(
    id_credito: str,
    db: Session = Depends(get_db)
):
    credito = db.query(
        models.Creditos
    ).filter(
        models.Creditos.id_credito == id_credito
    ).options(
        joinedload(models.Creditos.cuotas).options(
            joinedload(models.Cuotas.pagos),
            joinedload(models.Cuotas.visitas)
        ),
        joinedload(models.Creditos.detalles).joinedload(models.Detalles.producto)
    ).first()

    if credito:
        return credito
    
    return None

@router.get('/perdida', response_model=list[schemas.CreditosFullResponse])
def get_clientes_perdida(
    db : Session = Depends(get_db)
):
    today = date.today()
    creditos = db.query(
        models.Creditos
    ).options(
        joinedload(
            models.Creditos.cliente,
        ),
        joinedload(
            models.Creditos.cuotas
        ),
        joinedload(
            models.Creditos.trabajador
        ),
        joinedload(
            models.Creditos.detalles
        )
    ).filter(
        models.Creditos.fecha_final < today
    ).all()

    return creditos
