import uuid
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class CidadeCreateSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=100)


class CidadeUpdateSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=100)


class CidadeResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str


class HotelCreateSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cidade_id: uuid.UUID
    estrelas: int = Field(default=3, ge=1, le=5)


class HotelUpdateSchema(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cidade_id: uuid.UUID
    estrelas: int = Field(ge=1, le=5)


class HotelResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    estrelas: int
    cidade: CidadeResponseSchema


class CidadeComHoteisSchema(CidadeResponseSchema):
    hoteis: List[HotelResponseSchema] = []