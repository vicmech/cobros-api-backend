from __future__ import annotations
from pydantic import BaseModel
from uuid import UUID
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .trabajadores import TrabajadoresResponse
    
class UsersBase(BaseModel):
    username: str
    email: str
    id_role: int


class UsersCreate(UsersBase):
    pwd: str


class UsersUpdate(UsersBase):
    pass


class UsersResponse(UsersBase):
    id_user: UUID

    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    username: str
    pwd: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UsersResponse
    trabajador: 'TrabajadoresResponse'

