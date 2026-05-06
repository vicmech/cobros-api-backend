from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID

from .distritos import DistritosWithProvincia, DistritosResponse

class ClientesBase(BaseModel):
    nombre: str
    apellido: str
    calle: str
    casa: str

class ClientesCreate(ClientesBase):
    telefono: str   
    id_distrito: int
    pass

class ClientesUpdate(ClientesBase):
    telefono: str
    pass

class ClientesSimpleResponse(ClientesBase):
    id_cliente: UUID
    distrito: 'DistritosResponse'

    class Config:
        from_attributes = True

class ClientesResponse(ClientesBase):
    id_cliente: UUID
    telefono: str
    id_distrito: int

    class Config:
        from_attributes = True

class ClienteWithDistrito(ClientesBase):
    id_cliente: UUID
    telefono: str
    distrito : 'DistritosWithProvincia'

    class Config:
        from_attributes = True
