from __future__ import annotations
from pydantic import BaseModel
from .provincias import ProvinciasResponse

class DistritosBase(BaseModel):
    nombre_distrito: str

class DistritosCreate(DistritosBase):
    id_provincia: int

class DistritosUpdate(DistritosBase):
    pass


class DistritosResponse(DistritosBase):
    id_distrito: int
    id_provincia: int

    class Config:
        from_attributes = True

class DistritosWithProvincia(DistritosBase):
    id_distrito: int
    provincia: ProvinciasResponse
