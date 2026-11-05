
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.models.hotel import Cidade, Hotel
from app.models.quarto import Quarto
from app.services.catalogo_hoteis_service import CatalogoHoteisService


@pytest.fixture
def hotel_com_quarto(db_session):
    cidade = Cidade(nome="Quixadá")

    hotel = Hotel(
        nome="Hotel Catálogo",
        cidade=cidade,
        estrelas=4,
    )

    quarto = Quarto(
        tipo="Deluxe",
        preco_diaria=Decimal("350.00"),
        max_adultos=2,
        max_criancas=2,
        hotel=hotel,
    )

    db_session.add(hotel)
    db_session.add(quarto)
    db_session.commit()
    db_session.refresh(hotel)

    return hotel


@pytest.fixture
def mongo_db():
    collection = MagicMock()
    collection.replace_one = AsyncMock()
    collection.delete_one = AsyncMock()

    db = MagicMock()
    db.__getitem__.return_value = collection

    return db


@pytest.mark.asyncio
async def test_sincronizar_hotel_cria_projecao(
    db_session,
    hotel_com_quarto,
    mongo_db,
):
    service = CatalogoHoteisService(
        db=db_session,
        mongo_db=mongo_db,
    )

    await service.sincronizar_hotel(hotel_com_quarto.id)

    collection = mongo_db["catalogo_hoteis"]

    collection.replace_one.assert_awaited_once()

    args, kwargs = collection.replace_one.call_args

    assert args[0] == {
        "_id": str(hotel_com_quarto.id)
    }, "A projeção deveria utilizar o ID do hotel como identificador no MongoDB."

    documento = args[1]

    assert documento["_id"] == str(hotel_com_quarto.id), (
        "O documento deveria conter o ID do hotel no campo '_id'."
    )
    assert documento["hotel_id"] == str(hotel_com_quarto.id), (
        "O campo 'hotel_id' deveria corresponder ao ID do hotel sincronizado."
    )
    assert documento["nome"] == "Hotel Catálogo", (
        "O documento deveria preservar o nome original do hotel."
    )
    assert documento["estrelas"] == 4, (
        "O documento deveria preservar a classificação de estrelas do hotel."
    )
    assert documento["cidade"]["nome"] == "Quixadá", (
        "O documento deveria conter o nome da cidade associada ao hotel."
    )

    assert len(documento["quartos"]) == 1, (
        "A projeção deveria conter exatamente o quarto cadastrado para o hotel."
    )
    assert documento["quartos"][0]["tipo"] == "Deluxe", (
        "O quarto projetado deveria preservar o tipo cadastrado."
    )
    assert documento["quartos"][0]["preco_diaria"] == 350.00, (
        "O quarto projetado deveria preservar o preço da diária."
    )
    assert documento["quartos"][0]["max_adultos"] == 2, (
        "O quarto projetado deveria preservar a quantidade máxima de adultos."
    )
    assert documento["quartos"][0]["max_criancas"] == 2, (
        "O quarto projetado deveria preservar a quantidade máxima de crianças."
    )

    assert kwargs == {"upsert": True}, (
        "A sincronização deveria utilizar upsert para criar ou atualizar a projeção."
    )


@pytest.mark.asyncio
async def test_sincronizar_hotel_e_idempotente(
    db_session,
    hotel_com_quarto,
    mongo_db,
):
    service = CatalogoHoteisService(
        db=db_session,
        mongo_db=mongo_db,
    )

    await service.sincronizar_hotel(hotel_com_quarto.id)
    await service.sincronizar_hotel(hotel_com_quarto.id)

    collection = mongo_db["catalogo_hoteis"]

    assert collection.replace_one.await_count == 2, (
        "Duas sincronizações deveriam executar exatamente duas operações de atualização."
    )

    for call in collection.replace_one.await_args_list:
        assert call.args[0] == {
            "_id": str(hotel_com_quarto.id)
        }, "Cada sincronização deveria utilizar o ID correto do hotel."

        assert call.kwargs["upsert"] is True, (
            "Cada sincronização deveria manter o upsert habilitado."
        )


@pytest.mark.asyncio
async def test_sincronizar_hotel_inexistente_remove_projecao(
    db_session,
    mongo_db,
):
    service = CatalogoHoteisService(
        db=db_session,
        mongo_db=mongo_db,
    )

    hotel_id = uuid4()

    await service.sincronizar_hotel(hotel_id)

    collection = mongo_db["catalogo_hoteis"]

    collection.delete_one.assert_awaited_once_with(
        {"_id": str(hotel_id)}
    )
