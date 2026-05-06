from pydantic import BaseModel

class ProvinciasBase(BaseModel):
    nombre_provincia: str


class ProvinciasCreate(ProvinciasBase):
    pass


class ProvinciasUpdate(ProvinciasBase):
    pass


class ProvinciasResponse(ProvinciasBase):
    id_provincia: int

    class Config:
        from_attributes = True
