from app.core.database import get_mongo_db
from app.main import app
from tests.test_busca_service import DOCUMENTOS_EXEMPLO, _mongo_db_com_documentos


def test_busca_hoteis_endpoint_retorna_200_e_lista(client):
    mongo_db, _collection = _mongo_db_com_documentos(DOCUMENTOS_EXEMPLO)
    app.dependency_overrides[get_mongo_db] = lambda: mongo_db

    try:
        response = client.get("/api/v1/busca/hoteis")
    finally:
        app.dependency_overrides.pop(get_mongo_db, None)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["resultados"]) == 3


def test_busca_hoteis_endpoint_filtra_por_cidade(client):
    mongo_db, _collection = _mongo_db_com_documentos([DOCUMENTOS_EXEMPLO[0]])
    app.dependency_overrides[get_mongo_db] = lambda: mongo_db

    try:
        response = client.get(
            "/api/v1/busca/hoteis", params={"cidade": "Fortaleza"}
        )
    finally:
        app.dependency_overrides.pop(get_mongo_db, None)

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_busca_hoteis_endpoint_estrelas_fora_do_intervalo_retorna_422(client):
    mongo_db, _collection = _mongo_db_com_documentos([])
    app.dependency_overrides[get_mongo_db] = lambda: mongo_db

    try:
        response = client.get(
            "/api/v1/busca/hoteis", params={"estrelas": 6}
        )
    finally:
        app.dependency_overrides.pop(get_mongo_db, None)

    assert response.status_code == 422