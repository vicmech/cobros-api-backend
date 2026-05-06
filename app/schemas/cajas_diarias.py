from __future__ import annotations
from datetime import date, datetime
from pydantic import BaseModel, field_validator
from uuid import UUID
from typing import TYPE_CHECKING, Any
from app.special_types import caja_status

if TYPE_CHECKING:
    from . import GastosResponse
    from . import PagosResponse
    from . import CreditosSimpleResponse


class Cajas_DiariasBase(BaseModel):
    fecha: date
    monto_base: float
    renovaciones: float
    status: caja_status

    @field_validator('fecha', mode='before')
    @classmethod
    def parse_fecha(cls, value: Any):
        if isinstance(value, str) and 'T' in value:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        
        return value


class Cajas_DiariasCreate(Cajas_DiariasBase):
    id_trabajador: UUID

    


class Cajas_DiariasUpdate(Cajas_DiariasBase):
    pass

class Cajas_DiariasResponse(Cajas_DiariasBase):
    id_caja: UUID
    id_trabajador: UUID

    class Config:
        from_attributes = True

class Cajas_DiariasWithGastos(Cajas_DiariasResponse):
    gastos: list["GastosResponse"]

    class Config:
        from_attributes = True

class Cajas_DiariasWorker(BaseModel):
    caja: Cajas_DiariasWithGastos
    pagos: list["PagosResponse"]
    creditos: list["CreditosSimpleResponse"]

    class Config:
        from_attributes = True

    