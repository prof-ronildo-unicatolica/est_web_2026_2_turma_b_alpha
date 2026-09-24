from decimal import Decimal

import pytest

from app.api.deps import get_current_admin
from app.main import app
from app.models.hotel import Cidade, Hotel

BASE = "/api/v1/quartos"


@pytest.fixture
def hotel(db_session):
    cidade = Cidade(nome="Quixadá")
    db_session.add(cidade)
    db_session.commit()
    db_session.refresh(cidade)

    hotel = Hotel(
        nome="Hotel API Teste",
        cidade_id=cidade.id,
        estrelas=4,
    )
    db_session.add(hotel)
    db_session.commit()
    db_session.refresh(hotel)

    return hotel


@pytest.fixture
def admin_override():
    def override_get_current_admin():
        return {
            "id": "admin-teste",
            "nome": "Admin Teste",
            "email": "admin@teste.com",
            "is_admin": True,
        }

    app.dependency_overrides[get_current_admin] = override_get_current_admin

    yield

    app.dependency_overrides.pop(get_current_admin, None)


def test_admin_cria_quarto(client, hotel, admin_override):
    response = client.post(
        BASE,
        json={
            "tipo": "Luxo",
            "preco_diaria": "350.00",
            "max_adultos": 2,
            "max_criancas": 1,
            "hotel_id": str(hotel.id),
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["tipo"] == "Luxo"
    assert Decimal(str(body["preco_diaria"])) == Decimal("350.00")
    assert body["max_adultos"] == 2
    assert body["max_criancas"] == 1
    assert body["hotel_id"] == str(hotel.id)


def test_listagem_de_quartos_e_publica(client, hotel, db_session):
    from app.services.quarto_service import QuartoService

    QuartoService(db_session).criar(
        tipo="Standard",
        preco_diaria=Decimal("180.00"),
        max_adultos=2,
        max_criancas=0,
        hotel_id=hotel.id,
    )

    response = client.get(BASE)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["tipo"] == "Standard"


def test_admin_atualiza_quarto(client, hotel, db_session, admin_override):
    from app.services.quarto_service import QuartoService

    quarto = QuartoService(db_session).criar(
        tipo="Standard",
        preco_diaria=Decimal("180.00"),
        max_adultos=2,
        max_criancas=0,
        hotel_id=hotel.id,
    )

    response = client.put(
        f"{BASE}/{quarto.id}",
        json={
            "tipo": "Suíte",
            "preco_diaria": "400.00",
            "max_adultos": 3,
            "max_criancas": 2,
            "hotel_id": str(hotel.id),
        },
    )

    assert response.status_code == 200
    assert response.json()["tipo"] == "Suíte"
    assert response.json()["max_adultos"] == 3
    assert response.json()["max_criancas"] == 2


def test_admin_exclui_quarto(client, hotel, db_session, admin_override):
    from app.services.quarto_service import QuartoService

    quarto = QuartoService(db_session).criar(
        tipo="Standard",
        preco_diaria=Decimal("180.00"),
        max_adultos=2,
        max_criancas=0,
        hotel_id=hotel.id,
    )

    response = client.delete(f"{BASE}/{quarto.id}")

    assert response.status_code == 204

    response = client.get(f"{BASE}/{quarto.id}")

    assert response.status_code == 404


def test_criar_quarto_com_hotel_inexistente_retorna_404(
    client,
    admin_override,
):
    import uuid

    response = client.post(
        BASE,
        json={
            "tipo": "Standard",
            "preco_diaria": "200.00",
            "max_adultos": 2,
            "max_criancas": 0,
            "hotel_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 404


def test_criar_quarto_com_capacidade_invalida_retorna_422(
    client,
    hotel,
    admin_override,
):
    response = client.post(
        BASE,
        json={
            "tipo": "Standard",
            "preco_diaria": "200.00",
            "max_adultos": 0,
            "max_criancas": 0,
            "hotel_id": str(hotel.id),
        },
    )

    assert response.status_code == 422


def test_criar_quarto_sem_autenticacao_e_bloqueado(client, hotel):
    response = client.post(
        BASE,
        json={
            "tipo": "Standard",
            "preco_diaria": "200.00",
            "max_adultos": 2,
            "max_criancas": 0,
            "hotel_id": str(hotel.id),
        },
    )

    assert response.status_code in (401, 403)
    