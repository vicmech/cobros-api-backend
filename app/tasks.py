from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date
from .database import SessionLocal
from . import models

def check_expired_quotas():
    db = SessionLocal()
    today = date.today()
    try:
        expired_count = db.query(models.Cuotas).filter(
            models.Cuotas.estado == "PENDIENTE",
            models.Cuotas.fecha_vencimiento < today
        ).update({"estado": "VENCIDA"})
        
        db.commit()
        print(f"Se actualizaron {expired_count} cuotas a VENCIDO.")
    except Exception as e:
        print(f"Error en cron job: {e}")
        db.rollback()
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(check_expired_quotas, 'cron', hour=0, minute=1)
scheduler.start()