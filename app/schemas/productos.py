from pydantic import BaseModel

class ProductosBase(BaseModel):
    nombre: str
    precio_unitario: float

    class Config:
        from_attributes = True

class ProductosCreate(ProductosBase):
    pass


class ProductosUpdate(ProductosBase):
    pass


class ProductosResponse(ProductosBase):
    id_producto: int

    class Config:
        from_attributes = True
