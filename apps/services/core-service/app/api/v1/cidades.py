import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.schemas.hotel import (
    CidadeCreateSchema,
    CidadeResponseSchema,
    CidadeUpdateSchema,
)
from app.services.hotel_service import (
    CidadeJaExisteError,
    CidadeNaoEncontradaError,
    CidadeService,
)

router = APIRouter(prefix="/cidades", tags=["Cidades"])


@router.post(
    "",
    response_model=CidadeResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma cidade",
)
def criar_cidade(
    payload: CidadeCreateSchema,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        return CidadeService(db).criar(nome=payload.nome)
    except CidadeJaExisteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[CidadeResponseSchema],
    summary="Lista as cidades",
)
def listar_cidades(db: Session = Depends(get_db)):
    return CidadeService(db).listar()


@router.put(
    "/{cidade_id}",
    response_model=CidadeResponseSchema,
    summary="Atualiza uma cidade",
)
def atualizar_cidade(
    cidade_id: uuid.UUID,
    payload: CidadeUpdateSchema,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        return CidadeService(db).atualizar(
            cidade_id=cidade_id,
            nome=payload.nome,
        )
    except CidadeNaoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CidadeJaExisteError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{cidade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui uma cidade",
)
def excluir_cidade(
    cidade_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        CidadeService(db).excluir(cidade_id)
    except CidadeNaoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc