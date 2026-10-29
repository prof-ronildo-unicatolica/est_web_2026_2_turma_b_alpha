from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services.reserva_service import (
    EntradaCalculoReserva,
    Hospede,
    calcular_preco_reserva,
)
from app.models.servico_adicional import TipoCobranca


def criar_entrada(**alteracoes):
    dados = {
        "preco_diaria": Decimal("100.00"),
        "check_in": date(2026, 11, 1),
        "check_out": date(2026, 11, 3),
        "hospedes": [Hospede(idade=30)],
        "tarifas_temporada": [],
        "servicos_adicionais": [],
    }
    dados.update(alteracoes)
    return EntradaCalculoReserva(**dados)


def criar_servico(preco, tipo):
    return SimpleNamespace(
        preco=Decimal(preco),
        tipo_cobranca=tipo,
    )


def criar_tarifa(inicio, fim, multiplicador="1.00", preco_diferenciado=None):
    return SimpleNamespace(
        data_inicio=inicio,
        data_fim=fim,
        multiplicador=Decimal(multiplicador),
        preco_diferenciado=(
            Decimal(preco_diferenciado)
            if preco_diferenciado is not None
            else None
        ),
    )


def test_calcula_diarias_basicas():
    resultado = calcular_preco_reserva(criar_entrada())

    assert resultado.quantidade_diarias == 2
    assert resultado.subtotal_diarias == Decimal("200.00")
    assert resultado.total == Decimal("200.00")


def test_aplica_tarifa_de_temporada():
    tarifa = criar_tarifa(
        date(2026, 11, 2),
        date(2026, 11, 2),
        multiplicador="1.50",
    )

    resultado = calcular_preco_reserva(
        criar_entrada(tarifas_temporada=[tarifa])
    )

    assert resultado.subtotal_diarias == Decimal("250.00")


def test_aplica_preco_diferenciado_da_temporada():
    tarifa = criar_tarifa(
        date(2026, 11, 1),
        date(2026, 11, 1),
        preco_diferenciado="180.00",
    )

    resultado = calcular_preco_reserva(
        criar_entrada(tarifas_temporada=[tarifa])
    )

    assert resultado.subtotal_diarias == Decimal("280.00")


def test_calcula_adicional_de_crianca_de_seis_a_doze_anos():
    resultado = calcular_preco_reserva(
        criar_entrada(hospedes=[Hospede(idade=30), Hospede(idade=8)])
    )

    assert resultado.adicional_hospedes == Decimal("100.00")
    assert resultado.total == Decimal("300.00")


def test_crianca_de_ate_cinco_anos_nao_paga_adicional():
    resultado = calcular_preco_reserva(
        criar_entrada(hospedes=[Hospede(idade=30), Hospede(idade=5)])
    )

    assert resultado.adicional_hospedes == Decimal("0.00")
    assert resultado.total == Decimal("200.00")


def test_calcula_early_check_in_e_late_check_out():
    resultado = calcular_preco_reserva(
        criar_entrada(early_check_in=True, late_check_out=True)
    )

    assert resultado.adicional_early_late == Decimal("60.00")
    assert resultado.total == Decimal("260.00")


def test_calcula_servicos_por_diaria_por_pessoa_e_taxa_unica():
    servicos = [
        criar_servico("10.00", TipoCobranca.POR_DIARIA),
        criar_servico("5.00", TipoCobranca.POR_PESSOA),
        criar_servico("20.00", TipoCobranca.TAXA_UNICA),
    ]

    resultado = calcular_preco_reserva(
        criar_entrada(
            hospedes=[Hospede(idade=30), Hospede(idade=25)],
            servicos_adicionais=servicos,
        )
    )

    assert resultado.total_servicos == Decimal("50.00")
    assert resultado.total == Decimal("250.00")


def test_aplica_desconto_nao_reembolsavel():
    resultado = calcular_preco_reserva(
        criar_entrada(nao_reembolsavel=True)
    )

    assert resultado.desconto_nao_reembolsavel == Decimal("20.00")
    assert resultado.total == Decimal("180.00")


@pytest.mark.parametrize(
    "alteracoes,mensagem",
    [
        (
            {
                "check_in": date(2026, 11, 3),
                "check_out": date(2026, 11, 1),
            },
            "check_out deve ser posterior ao check_in",
        ),
        (
            {"preco_diaria": Decimal("-1.00")},
            "preco_diaria não pode ser negativo",
        ),
        (
            {"hospedes": [Hospede(idade=-1)]},
            "idade do hóspede não pode ser negativa",
        ),
    ],
)
def test_rejeita_entrada_invalida(alteracoes, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        calcular_preco_reserva(criar_entrada(**alteracoes))
