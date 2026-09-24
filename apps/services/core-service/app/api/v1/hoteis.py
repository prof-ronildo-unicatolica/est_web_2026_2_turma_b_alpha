import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.schemas.hotel import (
    HotelCreateSchema,
    HotelResponseSchema,
    HotelUpdateSchema,
)
from app.services.hotel_service import (
    CidadeNaoEncontradaError,
    HotelNaoEncontradoError,
    HotelService,
)

router = APIRouter(prefix="/hoteis", tags=["Hoteis"])


@router.post(
    "",
    response_model=HotelResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um hotel vinculado a uma cidade",
)
def criar_hotel(
    payload: HotelCreateSchema,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        return HotelService(db).criar(
            nome=payload.nome,
            cidade_id=payload.cidade_id,
            estrelas=payload.estrelas,
        )
    except CidadeNaoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[HotelResponseSchema],
    summary="Lista os hoteis, com a cidade aninhada",
)
def listar_hoteis(
    cidade_id: uuid.UUID | None = Query(
        default=None,
        description="Filtra os hotéis por cidade",
    ),
    db: Session = Depends(get_db),
):
    try:
        return HotelService(db).listar(cidade_id=cidade_id)
    except CidadeNaoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/{hotel_id}",
    response_model=HotelResponseSchema,
    summary="Atualiza um hotel",
)
def atualizar_hotel(
    hotel_id: uuid.UUID,
    payload: HotelUpdateSchema,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        return HotelService(db).atualizar(
            hotel_id=hotel_id,
            nome=payload.nome,
            cidade_id=payload.cidade_id,
            estrelas=payload.estrelas,
        )
    except HotelNaoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except CidadeNaoEncontradaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{hotel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um hotel",
)
def excluir_hotel(
    hotel_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    try:
        HotelService(db).excluir(hotel_id)
    except HotelNaoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc