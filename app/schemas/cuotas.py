from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel
from datetime import date
from uuid import UUID
from app.special_types import estado_cuota

if TYPE_CHECKING:
    from .creditos import CreditosSimpleResponse
    from .pagos import PagosResponse
    from .visitas import VisitasWithTrabajador

class CuotasBase(BaseModel):
    nro_cuota: int
    fecha_vencimiento: date
    monto: float
    estado: estado_cuota
    id_credito: UUID

class CuotasCreate(CuotasBase):
    pass

class CuotasUpdate(CuotasBase):
    pass

class CuotasBaseResponse(CuotasBase):
    id_cuota: UUID

    class Config:
        from_attributes = True

class CuotasResponse(CuotasBase):
    id_cuota: UUID
    pagos: list['PagosResponse']    
    visitas: list['VisitasWithTrabajador']

    class Config:
        from_attributes = True

class CuotasProgressResponse(BaseModel):
    id_cuota: UUID
    nro_cuota : int
    fecha_vencimiento: date
    monto: float
    estado: estado_cuota
    credito: 'CreditosSimpleResponse'

    class Config:
        from_attributes = True

