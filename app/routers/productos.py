from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth_jwt import get_current_user
from app.database import get_db

router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
    dependencies=[Depends(get_current_user)] 
)

@router.get('/', response_model= list[schemas.ProductosResponse])
def get_products(
    db : Session = Depends(get_db)
):
    products = db.query(
        models.Productos
    ).all()

    return products

@router.post('/create', response_model=schemas.ProductosResponse)
def create_product(
    product : schemas.ProductosCreate,
    db: Session = Depends(get_db)
):
    NewProduct = models.Productos(**product.model_dump())
    db.add(NewProduct)
    db.commit()
    db.refresh(NewProduct)
    return NewProduct