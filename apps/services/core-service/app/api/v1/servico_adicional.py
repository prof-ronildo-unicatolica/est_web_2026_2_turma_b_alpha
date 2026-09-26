import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.servico_adicional import (
    ServicoAdicionalCreate,
    ServicoAdicionalResponse,
    ServicoAdicionalUpdate,
)
from app.services.servico_adicional import ServicoAdicionalService

router = APIRouter(prefix="/hoteis/{hotel_id}/servicos-adicionais", tags=["Serviços Adicionais"])


@router.post("/", response_model=ServicoAdicionalResponse, status_code=status.HTTP_201_CREATED)
def criar_servico(
    hotel_id: uuid.UUID,
    schema: ServicoAdicionalCreate,
    db: Session = Depends(get_db),
):
    service = ServicoAdicionalService(db)
    return service.criar_servico(hotel_id, schema)


@router.get("/", response_model=List[ServicoAdicionalResponse])
def listar_servicos(
    hotel_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    service = ServicoAdicionalService(db)
    return service.listar_por_hotel(hotel_id, skip=skip, limit=limit)


@router.get("/{servico_id}", response_model=ServicoAdicionalResponse)
def obter_servico(
    servico_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = ServicoAdicionalService(db)
    return service.obter_por_id(servico_id)


@router.put("/{servico_id}", response_model=ServicoAdicionalResponse)
def atualizar_servico(
    servico_id: uuid.UUID,
    schema: ServicoAdicionalUpdate,
    db: Session = Depends(get_db),
):
    service = ServicoAdicionalService(db)
    return service.atualizar_servico(servico_id, schema)


@router.delete("/{servico_id}", status_code=status.HTTP_200_OK)
def deletar_servico(
    servico_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    service = ServicoAdicionalService(db)
    return service.deletar_servico(servico_id)
