from __future__ import annotations
from pydantic import BaseModel, field_validator
from datetime import date, datetime
from app.special_types import pay_method
from uuid import UUID
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .creditos import CreditosSimpleResponse
    from .cuotas import CuotasProgressResponse

class PagosBase(BaseModel):
    id_cuota: UUID
    id_trabajador: UUID
    monto: float
    fecha_pago: date
    metodo_pago: pay_method

    @field_validator("metodo_pago", mode="before")
    @classmethod
    def validate_metodo_pago(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v
    
    @field_validator('fecha_pago', mode='before')
    @classmethod
    def parse_fecha(cls, value: Any):
        if isinstance(value, str) and 'T' in value:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        
        return value
class PagosCreate(PagosBase):
    id_trabajador: UUID
    pass

class PagosUpdate(PagosBase):
    pass

class PagosInCreditoResponse(BaseModel):
    id_pago: UUID
    monto: float
    fecha_pago: date
    metodo_pago: pay_method

    class Config:
        from_attributes = True

class PagosResponse(PagosBase):
    id_pago: UUID
    
    class Config:
        from_attributes = True

class PagosWithCreditoResponse(PagosBase):
    credito : CreditosSimpleResponse

class PagosWithCuotaResponse(PagosResponse):
    cuota : CuotasProgressResponse

    class Config:
        from_attributes = True
    

