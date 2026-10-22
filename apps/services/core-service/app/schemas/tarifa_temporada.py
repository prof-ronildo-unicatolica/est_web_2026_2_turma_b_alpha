import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TarifaTemporadaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    data_inicio: date
    data_fim: date
    multiplicador: Decimal = Field(Decimal("1.00"), gt=0, decimal_places=2)
    preco_diferenciado: Decimal | None = Field(None, gt=0, decimal_places=2)

    @model_validator(mode="after")
    def validar_datas(self) -> "TarifaTemporadaBase":
        if self.data_fim < self.data_inicio:
            raise ValueError("A data de fim deve ser posterior ou igual à data de início.")
        return self


class TarifaTemporadaCreate(TarifaTemporadaBase):
    pass


class TarifaTemporadaUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=100)
    data_inicio: date | None = None
    data_fim: date | None = None
    multiplicador: Decimal | None = Field(None, gt=0, decimal_places=2)
    preco_diferenciado: Decimal | None = Field(None, gt=0, decimal_places=2)


class TarifaTemporadaResponse(TarifaTemporadaBase):
    id: uuid.UUID
    quarto_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)