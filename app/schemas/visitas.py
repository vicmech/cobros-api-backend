from __future__ import annotations
from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import date, datetime
from app.special_types import resultado_visita
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .trabajadores import TrabajadoresResponse

class VisitasBase(BaseModel):
    id_trabajador: UUID
    id_cuota: UUID
    fecha: date
    resultado: resultado_visita
    observaciones: str

    @field_validator('fecha', mode='before')
    @classmethod
    def parse_fecha(cls, value: Any):
        if isinstance(value, str) and 'T' in value:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        
        return value

    class Config:
        from_attributes = True

class VisitasCreate(VisitasBase):
    pass

class VisitasUpdate(VisitasBase):
    pass

class VisitasResponse(VisitasBase):
    id_visita : UUID

    class Config:
        from_attributes = True
    
class VisitasWithTrabajador(VisitasResponse):
    trabajador: 'TrabajadoresResponse'
    
    class Config:
        from_attributes = True
