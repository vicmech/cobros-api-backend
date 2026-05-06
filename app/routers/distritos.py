from fastapi import APIRouter, Depends
from app.auth_jwt import get_current_user
from app.database import get_db
from app import models, schemas
from sqlalchemy.orm import Session, joinedload
from datetime import date
from collections import defaultdict

router = APIRouter(
    prefix='/distritos',
    tags=['Distritos'],
    dependencies=[Depends(get_current_user)]
)

@router.get("/", response_model=list[schemas.DistritosResponse])
def list_distritos(
    db: Session = Depends(get_db)
):
    query = db.query(models.Distritos)
    return query.all()


@router.get('/trabajador/{id_trabajador}/ruta')
def get_ruta_trabajador(
    id_trabajador: str,
    db : Session = Depends(get_db)
):
    today = date.today()

    cuotas = db.query(models.Cuotas)\
        .join(models.Creditos)\
        .options(
            joinedload(models.Cuotas.credito)
            .joinedload(models.Creditos.cliente)
            .joinedload(models.Clientes.distrito)
        )\
        .filter(
            models.Creditos.id_trabajador == id_trabajador,
            models.Cuotas.fecha_vencimiento == today
        ).all()

    # 2. Agrupamos manualmente en Python
    ruta_agrupada = defaultdict(list)
    
    for c in cuotas:
        nombre_distrito = c.credito.cliente.distrito.nombre_distrito
        ruta_agrupada[nombre_distrito].append(c)

    # 3. Retornamos un formato fácil de leer: {"Belen": [...], "Iquitos": [...]}
    return ruta_agrupada