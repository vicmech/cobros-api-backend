from fastapi import FastAPI
from . import models
from . import database
from fastapi.middleware.cors import CORSMiddleware
from app.routers import stats, productos, clientes, creditos, pagos, gastos, users, auth, trabajadores, visitas, cuotas, distritos, cajas_diarias
from apscheduler.schedulers.background import BackgroundScheduler
from app.tasks import check_expired_quotas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router)
app.include_router(creditos.router)
app.include_router(pagos.router)
app.include_router(gastos.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(trabajadores.router)
app.include_router(visitas.router)
app.include_router(cuotas.router)
app.include_router(distritos.router)
app.include_router(cajas_diarias.router)
app.include_router(productos.router)
app.include_router(stats.router)

scheduler = BackgroundScheduler()

@app.on_event("startup")
def iniciar_planificador():
    check_expired_quotas()

    scheduler.add_job(
        check_expired_quotas, 
        'cron', 
        hour=0, 
        minute=5,
        id="task_vencimiento_cuotas" 
    )
    
    scheduler.start()
    print("Scheduler iniciado: Revisión de vencimientos programada.")

@app.on_event("shutdown")
def detener_planificador():
    scheduler.shutdown()
    print("Scheduler detenido.")

