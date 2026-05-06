from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel
from uuid import UUID

if TYPE_CHECKING:
    from .pagos import PagosResponse, PagosWithCuotaResponse
    from .cuotas import CuotasProgressResponse
    from .cajas_diarias import Cajas_DiariasResponse


class TrabajadoresBase(BaseModel):
    nombre: str
    apellido: str
    telefono: str
    id_user: UUID

class TrabajadorDailyActivity(BaseModel):
    trabajador: TrabajadoresResponse
    cobros_realizados: list['PagosWithCuotaResponse'] 
    cuotas_pendientes: list['CuotasProgressResponse']

    class Config:
        from_attributes = True

class TrabajadoresCreate(TrabajadoresBase):
    pass


class TrabajadoresUpdate(TrabajadoresBase):
    pass

class TrabajadoresResponse(TrabajadoresBase):
    id_trabajador: UUID

    class Config:
        from_attributes = True

class TrabajadoresProgressSummary(TrabajadoresResponse):
    cobrado_total: float
    cuotas_total: float

    class Config:
        from_attributes = True

class TrabajadoresRouteResponse(TrabajadoresResponse):
    cuotas: list['CuotasProgressResponse']

    class Config:
        from_attributes = True

class TrabajadoresCajaResponse(TrabajadoresResponse):
    caja : Optional['Cajas_DiariasResponse']

    class Config:
        from_attributes = True
