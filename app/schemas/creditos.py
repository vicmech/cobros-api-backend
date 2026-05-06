from __future__ import annotations
from typing import TYPE_CHECKING, Any, Optional
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, field_validator
from app.special_types import tiempo_credito, intervalo_cobro, pay_method

if TYPE_CHECKING:
    from .clientes import ClientesSimpleResponse, ClientesResponse, ClienteWithDistrito
    from .detalles import DetallesCreate
    from .detalles import DetallesResponse
    from .trabajadores import TrabajadoresResponse
    from .cuotas import CuotasResponse

class CreditosBase(BaseModel):
    tiempo_credito: tiempo_credito
    fecha_inicial: date
    fecha_final: date
    monto_total: float
    intervalo_cobro: intervalo_cobro
    origen_monto: Optional[pay_method]

    model_config = {
        "use_enum_values": True
    }

    @field_validator("tiempo_credito", "intervalo_cobro", mode="before", check_fields=False)
    @classmethod
    def validate_tiempo_credito(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v
    
    @field_validator('fecha_inicial', 'fecha_final', mode='before')
    @classmethod
    def parse_fecha(cls, value: Any):
        if isinstance(value, str) and 'T' in value:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        
        return value
    
class CreditosSimpleResponse(BaseModel):
    fecha_inicial: date
    fecha_final: date
    monto_total: float
    id_credito: UUID
    cliente: 'ClienteWithDistrito'
    id_trabajador: UUID
    id_cliente: UUID
    origen_monto: Optional[pay_method]


class CreditosCreate(CreditosBase):
    id_cliente: UUID
    detalles: list["DetallesCreate"]
    id_trabajador: UUID

class CreditosUpdate(CreditosBase):
    pass

class CreditosResponse(CreditosBase):
    id_credito: UUID
    
    class Config:
        from_attributes = True

class CreditosInPayResponse(BaseModel):
    trabajador: "TrabajadoresResponse"
    cliente: "ClientesSimpleResponse"

    class Config:
        from_attributes = True

class CreditosFullResponse(CreditosResponse):
    trabajador: 'TrabajadoresResponse'
    cliente: 'ClientesSimpleResponse'
    detalles: list['DetallesResponse']
    cuotas: list['CuotasResponse']

    class Config:
        from_attributes = True

class CreditoWithCliente(CreditosBase):
    cliente: 'ClientesResponse'

    class Config:
        from_attributes = True

class CreditoPerdida(CreditosBase):
    cliente : 'ClientesResponse'
    cuotas : list['CuotasResponse']

    class Config:
        from_attributes = True

class CreditoCardSummary(CreditosResponse):
    monto_pagado: float
    monto_restante: float
    proxima_cuota: Optional[date]
    nombre_cliente: str

    class Config:
        from_attributes = True