import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.core.database import get_db, get_mongo_db
from app.services.catalogo_hoteis_service import CatalogoHoteisService
from app.schemas.quarto import QuartoCreate, QuartoResponse, QuartoUpdate
from app.services.quarto_service import (
    DadosQuartoInvalidosError,
    HotelNaoEncontradoError,
    QuartoNaoEncontradoError,
    QuartoService,
)

router = APIRouter(prefix="/quartos", tags=["Quartos"])


@router.post(
    "",
    response_model=QuartoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um quarto vinculado a um hotel",
)
async def criar_quarto(
    payload: QuartoCreate,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db)

    try:
        quarto = service.criar(
            tipo=payload.tipo,
            preco_diaria=payload.preco_diaria,
            max_adultos=payload.max_adultos,
            max_criancas=payload.max_criancas,
            hotel_id=payload.hotel_id,
        )

        await CatalogoHoteisService(
            db=db,
            mongo_db=mongo_db,
        ).sincronizar_hotel(quarto.hotel_id)

        return quarto

    except HotelNaoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DadosQuartoInvalidosError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[QuartoResponse],
    summary="Lista os quartos",
)
def listar_quartos(
    hotel_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        return QuartoService(db).listar(hotel_id=hotel_id)
    except HotelNaoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{quarto_id}",
    response_model=QuartoResponse,
    summary="Busca um quarto por ID",
)
def buscar_quarto(
    quarto_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    try:
        return QuartoService(db).buscar(quarto_id)
    except QuartoNaoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.put(
    "/{quarto_id}",
    response_model=QuartoResponse,
    summary="Atualiza um quarto",
)
async def atualizar_quarto(
    quarto_id: uuid.UUID,
    payload: QuartoUpdate,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db)

    try:
        quarto_anterior = service.buscar(quarto_id)
        hotel_anterior_id = quarto_anterior.hotel_id

        quarto = service.atualizar(
            quarto_id=quarto_id,
            tipo=payload.tipo,
            preco_diaria=payload.preco_diaria,
            max_adultos=payload.max_adultos,
            max_criancas=payload.max_criancas,
            hotel_id=payload.hotel_id,
        )

        catalogo_service = CatalogoHoteisService(
            db=db,
            mongo_db=mongo_db,
        )

        await catalogo_service.sincronizar_hotel(
            hotel_anterior_id
        )

        if quarto.hotel_id != hotel_anterior_id:
            await catalogo_service.sincronizar_hotel(
                quarto.hotel_id
            )

        return quarto

    except (QuartoNaoEncontradoError, HotelNaoEncontradoError) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DadosQuartoInvalidosError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

@router.delete(
    "/{quarto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Exclui um quarto",
)
async def excluir_quarto(
    quarto_id: uuid.UUID,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
    _admin: dict = Depends(get_current_admin),
):
    service = QuartoService(db)

    try:
        quarto = service.buscar(quarto_id)
        hotel_id = quarto.hotel_id

        service.excluir(quarto_id)

        await CatalogoHoteisService(
            db=db,
            mongo_db=mongo_db,
        ).sincronizar_hotel(hotel_id)

    except QuartoNaoEncontradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc