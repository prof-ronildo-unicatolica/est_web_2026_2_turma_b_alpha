import uuid

from pydantic import BaseModel, ConfigDict, Field


class ComodidadeCreateSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=100)


class ComodidadeUpdateSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=100)


class ComodidadeResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str