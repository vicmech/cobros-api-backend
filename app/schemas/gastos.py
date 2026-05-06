from pydantic import BaseModel
from uuid import UUID


class GastosBase(BaseModel):
    id_caja: UUID
    importe: float
    descripcion: str


class GastosCreate(GastosBase):
    pass


class GastosUpdate(GastosBase):
    pass


class GastosResponse(GastosBase):
    id_gasto: UUID

    class Config:
        from_attributes = True
