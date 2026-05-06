from fastapi import APIRouter, Depends
from app.database import get_db
from app.auth_jwt import get_current_user
from app import schemas, models
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/visitas",
    tags=["Visitas"],
    dependencies=[Depends(get_current_user)] 
)

@router.get('/', response_model=list[schemas.VisitasResponse])
def get_visitas(
    db : Session = Depends(get_db)
):
    visitas = db.query(models.Visitas).all()

    return visitas

@router.post('/create', response_model=schemas.VisitasResponse)
def post_visita(
    visita : schemas.VisitasCreate,
    db : Session = Depends(get_db)
):
    newVisita = models.Visitas(**visita.model_dump())
    db.add(newVisita)
    db.commit()
    db.refresh(newVisita)
    return newVisita
