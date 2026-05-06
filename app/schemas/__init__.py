from .productos import *
from .detalles import *
from .provincias import *
from .distritos import *
from .users import *
from .gastos import *
from .cajas_diarias import *
from .roles import *
from .clientes import *
from .creditos import *
from .cuotas import *
from .pagos import *
from .trabajadores import *
from .visitas import *
from .stats import *

DetallesResponse.model_rebuild()
DetallesCreate.model_rebuild()

CreditosResponse.model_rebuild()
CreditosInPayResponse.model_rebuild()
CreditosCreate.model_rebuild()
CreditosSimpleResponse.model_rebuild()
CreditosFullResponse.model_rebuild()
CreditoWithCliente.model_rebuild()
CreditoPerdida.model_rebuild()
CreditoCardSummary.model_rebuild()

CuotasResponse.model_rebuild()
CuotasProgressResponse.model_rebuild()

PagosResponse.model_rebuild()
PagosWithCuotaResponse.model_rebuild()

Cajas_DiariasResponse.model_rebuild()
Cajas_DiariasWorker.model_rebuild()
Cajas_DiariasWithGastos.model_rebuild()

DistritosBase.model_rebuild()

ClientesBase.model_rebuild()
ClienteWithDistrito.model_rebuild()

TrabajadoresCajaResponse.model_rebuild()
TrabajadorDailyActivity.model_rebuild()
TrabajadoresRouteResponse.model_rebuild()

VisitasWithTrabajador.model_rebuild()

LoginResponse.model_rebuild()