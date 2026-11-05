"""S3-04 - Testes de integracao do catalogo.

Esqueleto: preencher os TODO quando o CRUD admin (S3-02, PR #43) estiver
mergeado na develop. As rotas publicas usadas pelo frontend sao
/api/v1/cidades e /api/v1/hoteis.
"""
import pytest

pytestmark = pytest.mark.skip(reason="aguardando S3-02 (CRUD admin) na develop")

BASE_CIDADES = "/api/v1/cidades"
BASE_HOTEIS = "/api/v1/hoteis"


def test_admin_cria_cidade_e_hotel(client):
    # TODO: autenticar como admin (fixture admin_override)
    # TODO: POST em cidades e depois POST em hoteis ligado a essa cidade
    # TODO: esperar 201 nas duas respostas
    pass


def test_cliente_nao_altera_catalogo(client):
    # TODO: autenticar como cliente comum
    # TODO: tentar POST/PUT/DELETE em cidades e hoteis
    # TODO: esperar 403 em todos
    pass


def test_publico_lista_cidades_e_hoteis(client):
    # TODO: criar uma cidade e um hotel de exemplo
    # TODO: GET sem token em BASE_CIDADES e BASE_HOTEIS
    # TODO: esperar 200 e os itens criados na lista
    pass


def test_relacionamento_cidade_hotel_comodidade(client):
    # TODO: criar cidade, hotel e comodidade
    # TODO: conferir que o hotel retorna a cidade e as comodidades
    pass