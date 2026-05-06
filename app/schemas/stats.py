from pydantic import BaseModel

class FinantialHealtResponse(BaseModel): 
    capital_calle: float
    meta_hoy: float
    total_base: float

    class Config:
        from_attributes = True