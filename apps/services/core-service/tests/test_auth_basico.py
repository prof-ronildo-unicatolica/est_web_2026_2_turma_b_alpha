"""Testes de autenticacao e autorizacao da Sprint 2."""

import time
import uuid

import jwt

from app.core.security import SECRET_KEY, ALGORITHM


BASE = "/api/v1/auth"


def test_login_valido_retorna_token(client):
    resp = client.post(
        f"{BASE}/login",
        json={"email": "cliente@hotel.com", "senha": "cliente123"},
    )

    assert resp.status_code == 200

    body = resp.json()

    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_invalido_retorna_401(client):
    resp = client.post(
        f"{BASE}/login",
        json={"email": "cliente@hotel.com", "senha": "errada"},
    )

    assert resp.status_code == 401


def test_rota_protegida_sem_token_retorna_401(client):
    resp = client.get(f"{BASE}/me")

    assert resp.status_code == 401


def test_rota_protegida_com_token_invalido_retorna_401(client):
    resp = client.get(
        f"{BASE}/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert resp.status_code == 401


def test_rota_protegida_com_token_expirado_retorna_401(client):
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": int(time.time()) - 60,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    resp = client.get(
        f"{BASE}/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 401


def test_auth_me_com_jwt_valido_retorna_usuario(client):
    login = client.post(
        f"{BASE}/login",
        json={"email": "cliente@hotel.com", "senha": "cliente123"},
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    resp = client.get(
        f"{BASE}/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200

    body = resp.json()

    assert body["email"] == "cliente@hotel.com"
    assert body["is_admin"] is False
    assert "senha" not in body


def test_cliente_nao_acessa_rota_admin(client):
    login = client.post(
        f"{BASE}/login",
        json={"email": "cliente@hotel.com", "senha": "cliente123"},
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    resp = client.get(
        f"{BASE}/admin/verificacao",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 403


def test_admin_acessa_rota_admin(client):
    login = client.post(
        f"{BASE}/login",
        json={"email": "admin@hotel.com", "senha": "admin123"},
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    resp = client.get(
        f"{BASE}/admin/verificacao",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
