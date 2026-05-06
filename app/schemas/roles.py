from pydantic import BaseModel


class RolesBase(BaseModel):
    nombre_rol: str


class RolesCreate(RolesBase):
    pass


class RolesUpdate(RolesBase):
    pass


class RolesResponse(RolesBase):
    id_rol: str

    class Config:
        from_attributes = True
