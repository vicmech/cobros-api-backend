from __future__ import annotations
from typing import TYPE_CHECKING
from pydantic import BaseModel
from uuid import UUID

if TYPE_CHECKING:
    from .productos import ProductosResponse


class DetallesBase(BaseModel):
    cantidad: int

    class Config:
        from_attributes = True


class DetallesCreate(DetallesBase):
    id_producto: int

    class Config:
        from_attributes = True


class DetallesUpdate(DetallesBase):
    pass


class DetallesResponse(DetallesBase):
    id_detalle: UUID
    id_credito: UUID
    producto: "ProductosResponse"

    class Config:
        from_attributes = True

