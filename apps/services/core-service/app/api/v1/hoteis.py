import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.hotel import HotelCreateSchema, HotelResponseSchema
from app.services.hotel_service import CidadeNaoEncontradaError, HotelService
from app.core.database import get_db, get_mongo_db
from app.services.catalogo_hoteis_service import CatalogoHoteisService

router = APIRouter(prefix="/hoteis", tags=["Hoteis"])


@router.post(
    "",
    response_model=HotelResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Cria um hotel vinculado a uma cidade",
)
async def criar_hotel(
    payload: HotelCreateSchema,
    db: Session = Depends(get_db),
    mongo_db=Depends(get_mongo_db),
):
    service = HotelService(db)

    try:
        hotel = service.criar(
            nome=payload.nome,
            cidade_id=payload.cidade_id,
        )

        await CatalogoHoteisService(
            db=db,
            mongo_db=mongo_db,
        ).sincronizar_hotel(hotel.id)

        return hotel

    except CidadeNaoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "",
    response_model=list[HotelResponseSchema],
    summary="Lista os hoteis, com a cidade aninhada",
)
def listar_hoteis(
    cidade_id: uuid.UUID | None = Query(
        default=None, description="Filtra os hoteis de uma cidade especifica"
    ),
    db: Session = Depends(get_db),
):
    try:
        return HotelService(db).listar(cidade_id=cidade_id)
    except CidadeNaoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))