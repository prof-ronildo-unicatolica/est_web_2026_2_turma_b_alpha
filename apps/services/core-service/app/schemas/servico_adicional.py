import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.servico_adicional import TipoCobranca


class ServicoAdicionalBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: str | None = Field(None, max_length=255)
    preco: Decimal = Field(..., gt=0, decimal_places=2)
    tipo_cobranca: TipoCobranca = TipoCobranca.TAXA_UNICA


class ServicoAdicionalCreate(ServicoAdicionalBase):
    pass


class ServicoAdicionalUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=100)
    descricao: str | None = Field(None, max_length=255)
    preco: Decimal | None = Field(None, gt=0, decimal_places=2)
    tipo_cobranca: TipoCobranca | None = None


class ServicoAdicionalResponse(ServicoAdicionalBase):
    id: uuid.UUID
    hotel_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)