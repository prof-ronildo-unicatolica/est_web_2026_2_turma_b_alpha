import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class QuartoBase(BaseModel):
    tipo: str = Field(min_length=1, max_length=100)
    preco_diaria: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    max_adultos: int = Field(ge=1)
    max_criancas: int = Field(ge=0)
    hotel_id: uuid.UUID


class QuartoCreate(QuartoBase):
    pass


class QuartoUpdate(QuartoBase):
    pass


class QuartoResponse(QuartoBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID