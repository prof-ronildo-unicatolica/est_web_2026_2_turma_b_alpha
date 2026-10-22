import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.tarifa_temporada import (
    TarifaTemporadaCreate,
    TarifaTemporadaResponse,
    TarifaTemporadaUpdate,
)
from app.services.tarifa_temporada import TarifaTemporadaService

router = APIRouter(prefix="/quartos/{quarto_id}/tarifas-temporada", tags=["Tarifas de Temporada"])


@router.post("/", response_model=TarifaTemporadaResponse, status_code=status.HTTP_201_CREATED)
def criar_tarifa(
    quarto_id: uuid.UUID,
    schema: TarifaTemporadaCreate,
    db: Session = Depends(get_db),
):
    service = TarifaTemporadaService(db)
    return service.criar_tarifa(quarto_id, schema)


@router.get("/", response_model=List[TarifaTemporadaResponse])
def listar_tarifas(
    quarto_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    service = TarifaTemporadaService(db)
    return service.listar_por_quarto(quarto_id, skip=skip, limit=limit)


@router.get("/{tarifa_id}", response_model=TarifaTemporadaResponse)
def obter_tarifa(
    tarifa_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = TarifaTemporadaService(db)
    return service.obter_por_id(tarifa_id)


@router.put("/{tarifa_id}", response_model=TarifaTemporadaResponse)
def atualizar_tarifa(
    tarifa_id: uuid.UUID,
    schema: TarifaTemporadaUpdate,
    db: Session = Depends(get_db),
):
    service = TarifaTemporadaService(db)
    return service.atualizar_tarifa(tarifa_id, schema)


@router.delete("/{tarifa_id}", status_code=status.HTTP_200_OK)
def deletar_tarifa(
    tarifa_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = TarifaTemporadaService(db)
    return service.deletar_tarifa(tarifa_id)
