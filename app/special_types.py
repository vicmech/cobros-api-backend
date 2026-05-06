import enum

class pay_method(enum.Enum):
    EFECTIVO = "EFECTIVO"
    YAPE = "YAPE"

class tiempo_credito(enum.Enum):
    SEMANAL = "SEMANAL"
    QUINCENAL = "QUINCENAL"
    MENSUAL = "MENSUAL"

class estado_cuota(enum.Enum):
    PAGADA = "PAGADA"
    PENDIENTE = "PENDIENTE"
    ABONO_PARCIAL = "ABONO_PARCIAL"
    VENCIDA = "VENCIDA"
    CANCELADA = "CANCELADA"

class resultado_visita(enum.Enum):
    COBRO_EXITOSO = "COBRO_EXITOSO"
    CLIENTE_AUSENTE = "CLIENTE_AUSENTE"
    RECHAZO = "RECHAZO"

class intervalo_cobro(enum.Enum):
    DIARIO = "DIARIO"
    SEMANAL = "SEMANAL"
    QUINCENAL = "QUINCENAL"
    MENSUAL = "MENSUAL"

class caja_status(enum.Enum):
    ASIGNADA = "ASIGNADA"
    ABIERTA = "ABIERTA"
    CERRADA = "CERRADA"