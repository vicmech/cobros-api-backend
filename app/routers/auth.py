from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth_jwt import get_current_user
from app import schemas, models
from passlib.context import CryptContext
from app.auth_jwt import create_access_token
from app.security import verify_pwd
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix='/auth',
    tags=["Auth"]
)

@router.post("/login",  dependencies=[], response_model = schemas.LoginResponse,)
def login(
    credentials : OAuth2PasswordRequestForm = Depends(), 
    db : Session = Depends(get_db),
):
    user = db.query(
        models.Users
    ).filter(
        models.Users.username == credentials.username
    ).first()

    if not user or not verify_pwd(credentials.password, user.pwd):
        raise HTTPException(status_code= 401, detail='Credenciales invalidas')
    access_token = create_access_token(data={"sub": str(user.id_user)})

    trabajador = db.query(
        models.Trabajadores
    ).filter(
        models.Trabajadores.id_user == user.id_user
    ).first()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
        "trabajador" : trabajador
    }