import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.schemas.comodidade import (
    ComodidadeCreateSchema,
    ComodidadeResponseSchema,
    ComodidadeUpdateSchema,
)
from app.services.hotel_service import (
    ComodidadeJaExisteError,
    ComodidadeNaoEncontradaError,
    ComodidadeService,
)

router = APIRouter(prefix="/comodidades", tags=["Comodidades"])


@router.post(
    "",
    response_model=ComodidadeResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma comodidade",
)
def criar_comodidade(
    payload: ComodidadeCreateSchema,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        return ComodidadeService(db).criar(payload.nome)
    except ComodidadeJaExisteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[ComodidadeResponseSchema],
    summary="Lista as comodidades",
)
def listar_comodidades(db: Session = Depends(get_db)):
    return ComodidadeService(db).listar()


@router.put(
    "/{comodidade_id}",
    response_model=ComodidadeResponseSchema,
    summary="Atualiza uma comodidade",
)
def atualizar_comodidade(
    comodidade_id: uuid.UUID,
    payload: ComodidadeUpdateSchema,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        return ComodidadeService(db).atualizar(
            comodidade_id=comodidade_id,
            nome=payload.nome,
        )
    except ComodidadeNaoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ComodidadeJaExisteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{comodidade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui uma comodidade",
)
def excluir_comodidade(
    comodidade_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        ComodidadeService(db).excluir(comodidade_id)
    except ComodidadeNaoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc