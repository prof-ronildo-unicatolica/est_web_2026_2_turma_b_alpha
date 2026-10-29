"""S6-05 - Teste concorrente de overbooking.

Esqueleto: depende da S6-01/S6-02 (criacao de reserva + worker).
Preencher os TODO quando elas estiverem integradas na develop.
"""
from concurrent.futures import ThreadPoolExecutor

import pytest

pytestmark = pytest.mark.skip(reason="aguardando S6-01/S6-02 integradas na develop")


def _solicitar_reserva(client, payload):
    # TODO: trocar pelo endpoint real de reserva (S6-01)
    return client.post("/api/v1/reservas", json=payload)


def test_duas_solicitacoes_concorrentes_nao_geram_overbooking(client):
    # 1. TODO: preparar um quarto com apenas uma disponibilidade
    payload = {}  # TODO: dados da reserva para o quarto preparado

    # 2. Dispara duas solicitacoes concorrentes
    with ThreadPoolExecutor(max_workers=2) as pool:
        futuros = [pool.submit(_solicitar_reserva, client, payload) for _ in range(2)]
        respostas = [f.result() for f in futuros]

    # 3. TODO: aguardar o processamento do worker
    # 4. TODO: consultar o status final das duas reservas
    status = []  # TODO: ex.: ["CONFIRMADA", "CANCELADA"]

    # 5. Exatamente uma confirmada e uma cancelada
    assert status.count("CONFIRMADA") == 1
    assert status.count("CANCELADA") == 1