import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_current_user
from app.main import app


@pytest.fixture
def client_autenticado():
    usuario_id = str(uuid.uuid4())

    def _override_user():
        return {
            "id": usuario_id,
            "email": "hospede@exemplo.com",
            "nome": "Hospede Teste",
            "is_admin": False,
        }

    app.dependency_overrides[get_current_user] = _override_user
    with TestClient(app) as client:
        yield client, usuario_id
    app.dependency_overrides.clear()


def test_post_cancelar_sem_token_retorna_401():
    with TestClient(app) as client:
        response = client.post("/api/v1/reservas/res-123/cancelar")

    assert response.status_code == 401


def test_post_cancelar_autenticado_retorna_estrutura_esperada(client_autenticado):
    client, _ = client_autenticado
    data_cancelamento = datetime(2026, 12, 1, 10, 0, 0)

    response = client.post(
        "/api/v1/reservas/res-123/cancelar",
        json={"data_cancelamento": data_cancelamento.isoformat()},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["reserva_id"] == "res-123"
    assert body["status_anterior"] == "CONFIRMADA"
    assert body["status_atual"] == "CANCELADA"
    assert body["politica_aplicada"] == "REEMBOLSAVEL_MENOS_48H_MULTA_50"
    assert body["data_limite_cancelamento"] == (
        data_cancelamento - timedelta(hours=48)
    ).isoformat()
    assert Decimal(str(body["percentual_multa"])) == Decimal("50.00")
    assert Decimal(str(body["valor_multa"])) == Decimal("0.00")
    assert Decimal(str(body["valor_reembolso"])) == Decimal("0.00")


