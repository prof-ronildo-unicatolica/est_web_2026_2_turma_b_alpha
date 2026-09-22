from decimal import Decimal

import pytest

from app.models.hotel import Cidade, Hotel
from app.services.quarto_service import (
    DadosQuartoInvalidosError,
    HotelNaoEncontradoError,
    QuartoNaoEncontradoError,
    QuartoService,
)


@pytest.fixture
def hotel(db_session):
    cidade = Cidade(nome="Quixadá")
    db_session.add(cidade)
    db_session.commit()
    db_session.refresh(cidade)

    hotel = Hotel(
        nome="Hotel Teste",
        cidade_id=cidade.id,
        estrelas=3,
    )
    db_session.add(hotel)
    db_session.commit()
    db_session.refresh(hotel)

    return hotel


def test_criar_quarto(db_session, hotel):
    service = QuartoService(db_session)

    quarto = service.criar(
        tipo="Casal",
        preco_diaria=Decimal("250.00"),
        max_adultos=2,
        max_criancas=1,
        hotel_id=hotel.id,
    )

    assert quarto.id is not None
    assert quarto.tipo == "Casal"
    assert quarto.preco_diaria == Decimal("250.00")
    assert quarto.max_adultos == 2
    assert quarto.max_criancas == 1
    assert quarto.hotel_id == hotel.id


def test_criar_quarto_com_hotel_inexistente(db_session):
    import uuid

    service = QuartoService(db_session)

    with pytest.raises(HotelNaoEncontradoError):
        service.criar(
            tipo="Casal",
            preco_diaria=Decimal("250.00"),
            max_adultos=2,
            max_criancas=0,
            hotel_id=uuid.uuid4(),
        )


@pytest.mark.parametrize(
    ("preco", "adultos", "criancas"),
    [
        (Decimal("-1.00"), 2, 0),
        (Decimal("100.00"), 0, 0),
        (Decimal("100.00"), 2, -1),
    ],
)
def test_criar_quarto_com_dados_invalidos(
    db_session,
    hotel,
    preco,
    adultos,
    criancas,
):
    service = QuartoService(db_session)

    with pytest.raises(DadosQuartoInvalidosError):
        service.criar(
            tipo="Standard",
            preco_diaria=preco,
            max_adultos=adultos,
            max_criancas=criancas,
            hotel_id=hotel.id,
        )


def test_atualizar_quarto(db_session, hotel):
    service = QuartoService(db_session)

    quarto = service.criar(
        tipo="Standard",
        preco_diaria=Decimal("150.00"),
        max_adultos=2,
        max_criancas=0,
        hotel_id=hotel.id,
    )

    atualizado = service.atualizar(
        quarto_id=quarto.id,
        tipo="Luxo",
        preco_diaria=Decimal("300.00"),
        max_adultos=3,
        max_criancas=2,
        hotel_id=hotel.id,
    )

    assert atualizado.tipo == "Luxo"
    assert atualizado.preco_diaria == Decimal("300.00")
    assert atualizado.max_adultos == 3
    assert atualizado.max_criancas == 2


def test_excluir_quarto(db_session, hotel):
    service = QuartoService(db_session)

    quarto = service.criar(
        tipo="Standard",
        preco_diaria=Decimal("150.00"),
        max_adultos=2,
        max_criancas=0,
        hotel_id=hotel.id,
    )

    quarto_id = quarto.id
    service.excluir(quarto_id)

    with pytest.raises(QuartoNaoEncontradoError):
        service.buscar(quarto_id)