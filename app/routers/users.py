from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth_jwt import get_current_user
from app.security import get_pwd_hash 
from app import schemas, models

router = APIRouter(
    prefix='/users',
    tags=["Users"],
    dependencies=[Depends(get_current_user)] 
)
@router.get("/{username}", response_model=schemas.UsersResponse)
def get_user(username: str, db: Session = Depends(get_db)):
    query = db.query(models.Users).filter(models.Users.username == username)
    db_user = query.first()
    if db_user:
        return db_user
    raise HTTPException(status_code=404, detail="Usuario no encontrado")

@router.post("/create", response_model=schemas.UsersResponse)
def create_user(
    user: schemas.UsersCreate,
    db: Session = Depends(get_db)
):
    user_data = user.model_dump()
    user_data["pwd"] = get_pwd_hash(user_data['pwd'])
    new_user = models.Users(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user