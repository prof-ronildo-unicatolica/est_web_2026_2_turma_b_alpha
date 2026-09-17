import jwt

from app.core.security import ALGORITHM, SECRET_KEY
from app.models.usuario import Usuario

BASE = "/api/v1/auth"


def test_register_retorna_201(client, db_session):
    response = client.post(
        f"{BASE}/register",
        json={
            "nome": "Cliente Teste",
            "email": "cliente@hotel.com",
            "senha": "cliente123",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["nome"] == "Cliente Teste"
    assert body["email"] == "cliente@hotel.com"
    assert body["is_admin"] is False
    assert "senha" not in body
    assert "senha_hash" not in body

    usuario = (
        db_session.query(Usuario)
        .filter(Usuario.email == "cliente@hotel.com")
        .first()
    )

    assert usuario is not None
    assert usuario.senha_hash != "cliente123"
    assert usuario.is_admin is False


def test_register_email_duplicado_retorna_409(client):
    payload = {
        "nome": "Cliente Teste",
        "email": "cliente@hotel.com",
        "senha": "cliente123",
    }

    primeira = client.post(f"{BASE}/register", json=payload)
    segunda = client.post(f"{BASE}/register", json=payload)

    assert primeira.status_code == 201
    assert segunda.status_code == 409


def test_login_valido_retorna_jwt(client):
    client.post(
        f"{BASE}/register",
        json={
            "nome": "Cliente Teste",
            "email": "cliente@hotel.com",
            "senha": "cliente123",
        },
    )

    response = client.post(
        f"{BASE}/login",
        json={
            "email": "cliente@hotel.com",
            "senha": "cliente123",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    payload = jwt.decode(
        body["access_token"],
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"]


def test_login_jwt_sub_e_id_do_usuario(client, db_session):
    client.post(
        f"{BASE}/register",
        json={
            "nome": "Cliente Teste",
            "email": "cliente@hotel.com",
            "senha": "cliente123",
        },
    )

    usuario = (
        db_session.query(Usuario)
        .filter(Usuario.email == "cliente@hotel.com")
        .first()
    )

    response = client.post(
        f"{BASE}/login",
        json={
            "email": "cliente@hotel.com",
            "senha": "cliente123",
        },
    )

    token = response.json()["access_token"]

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == str(usuario.id)


def test_login_senha_invalida_retorna_401(client):
    client.post(
        f"{BASE}/register",
        json={
            "nome": "Cliente Teste",
            "email": "cliente@hotel.com",
            "senha": "cliente123",
        },
    )

    response = client.post(
        f"{BASE}/login",
        json={
            "email": "cliente@hotel.com",
            "senha": "senha-errada",
        },
    )

    assert response.status_code == 401


def test_login_email_inexistente_retorna_401(client):
    response = client.post(
        f"{BASE}/login",
        json={
            "email": "naoexiste@hotel.com",
            "senha": "qualquer",
        },
    )

    assert response.status_code == 401