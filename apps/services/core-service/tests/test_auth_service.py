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

    assert response.status_code == 201, (
        "O cadastro de um novo usuario deveria retornar HTTP 201."
    )

    body = response.json()
    assert body["nome"] == "Cliente Teste", (
        "O nome retornado deveria corresponder ao nome informado no cadastro."
    )
    assert body["email"] == "cliente@hotel.com", (
        "O e-mail retornado deveria corresponder ao e-mail informado no cadastro."
    )
    assert body["is_admin"] is False, (
        "Um usuario cadastrado como cliente nao deveria possuir privilegios administrativos."
    )
    assert "senha" not in body, (
        "A resposta do cadastro nao deveria expor a senha do usuario."
    )
    assert "senha_hash" not in body, (
        "A resposta do cadastro nao deveria expor o hash da senha do usuario."
    )

    usuario = (
        db_session.query(Usuario)
        .filter(Usuario.email == "cliente@hotel.com")
        .first()
    )

    assert usuario is not None, (
        "O usuario cadastrado deveria estar persistido no banco de dados."
    )
    assert usuario.senha_hash != "cliente123", (
        "A senha do usuario deveria ser armazenada como hash, e nao em texto plano."
    )
    assert usuario.is_admin is False, (
        "O usuario persistido deveria possuir privilegios de cliente."
    )


def test_register_email_duplicado_retorna_409(client):
    payload = {
        "nome": "Cliente Teste",
        "email": "cliente@hotel.com",
        "senha": "cliente123",
    }

    primeira = client.post(f"{BASE}/register", json=payload)
    segunda = client.post(f"{BASE}/register", json=payload)

    assert primeira.status_code == 201, (
        "O primeiro cadastro com o e-mail deveria retornar HTTP 201."
    )
    assert segunda.status_code == 409, (
        "O cadastro com um e-mail ja existente deveria retornar HTTP 409."
    )


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

    assert response.status_code == 200, (
        "O login com credenciais validas deveria retornar HTTP 200."
    )

    body = response.json()
    assert body["token_type"] == "bearer", (
        "O tipo de token retornado deveria ser 'bearer'."
    )
    assert body["access_token"], (
        "A resposta do login deveria conter um access_token."
    )

    payload = jwt.decode(
        body["access_token"],
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"], (
        "O JWT deveria conter o identificador do usuario no campo 'sub'."
    )


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

    assert payload["sub"] == str(usuario.id), (
        "O campo 'sub' do JWT deveria corresponder ao ID do usuario autenticado."
    )


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

    assert response.status_code == 401, (
        "O login com senha incorreta deveria retornar HTTP 401."
    )


def test_login_email_inexistente_retorna_401(client):
    response = client.post(
        f"{BASE}/login",
        json={
            "email": "naoexiste@hotel.com",
            "senha": "qualquer",
        },
    )

    assert response.status_code == 401, (
        "O login com um e-mail nao cadastrado deveria retornar HTTP 401."
    )
