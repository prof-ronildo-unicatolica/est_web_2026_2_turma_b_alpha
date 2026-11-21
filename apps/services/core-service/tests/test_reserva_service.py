from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.models.servico_adicional import TipoCobranca
from app.services.reserva_service import (
    EntradaCalculoReserva,
    Hospede,
    calcular_preco_reserva,
)


def _tarifa(
    data_inicio: date,
    data_fim: date,
    *,
    multiplicador: Decimal | None = None,
    preco_diferenciado: Decimal | None = None,
):
    return SimpleNamespace(
        data_inicio=data_inicio,
        data_fim=data_fim,
        multiplicador=multiplicador,
        preco_diferenciado=preco_diferenciado,
    )


def _servico(
    preco: Decimal,
    tipo_cobranca: TipoCobranca,
):
    return SimpleNamespace(
        preco=preco,
        tipo_cobranca=tipo_cobranca,
    )


def test_calculo_basico_diarias_e_adultos():
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("200.00"),
        check_in=date(2026, 12, 10),
        check_out=date(2026, 12, 13),
        hospedes=[Hospede(30), Hospede(13)],
        tarifas_temporada=[],
        servicos_adicionais=[],
    )

    resultado = calcular_preco_reserva(entrada)

    assert resultado.quantidade_diarias == 3
    assert resultado.subtotal_diarias == Decimal("600.00")
    assert resultado.adicional_hospedes == Decimal("0.00")
    assert resultado.adicional_early_late == Decimal("0.00")
    assert resultado.total_servicos == Decimal("0.00")
    assert resultado.desconto_nao_reembolsavel == Decimal("0.00")
    assert resultado.total == Decimal("600.00")


def test_tarifas_temporada_multiplicador_e_preco_diferenciado():
    tarifas = [
        _tarifa(
            date(2026, 12, 20),
            date(2026, 12, 21),
            multiplicador=Decimal("1.5"),
        ),
        _tarifa(
            date(2026, 12, 22),
            date(2026, 12, 22),
            preco_diferenciado=Decimal("450.00"),
        ),
    ]
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("200.00"),
        check_in=date(2026, 12, 20),
        check_out=date(2026, 12, 23),
        hospedes=[Hospede(25)],
        tarifas_temporada=tarifas,
        servicos_adicionais=[],
    )

    resultado = calcular_preco_reserva(entrada)

    # Dia 20: 200 * 1.5 = 300; Dia 21: 200 * 1.5 = 300; Dia 22: 450 => 1050.00
    assert resultado.quantidade_diarias == 3
    assert resultado.subtotal_diarias == Decimal("1050.00")
    assert resultado.total == Decimal("1050.00")


def test_regras_idades_bebe_gratuito_e_crianca_50_porcento():
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("100.00"),
        check_in=date(2026, 11, 1),
        check_out=date(2026, 11, 3),
        hospedes=[
            Hospede(0),
            Hospede(5),
            Hospede(6),
            Hospede(12),
            Hospede(30),
        ],
        tarifas_temporada=[],
        servicos_adicionais=[],
    )

    resultado = calcular_preco_reserva(entrada)

    # 2 diárias * 100 = 200.00; 2 crianças (6 e 12) => 2 * (200 * 0.50) = 200.00
    assert resultado.subtotal_diarias == Decimal("200.00")
    assert resultado.adicional_hospedes == Decimal("200.00")
    assert resultado.total == Decimal("400.00")


def test_early_late_servicos_e_desconto_nao_reembolsavel():
    tarifas = [
        _tarifa(
            date(2026, 10, 10),
            date(2026, 10, 10),
            multiplicador=Decimal("2.0"),
        )
    ]
    servicos = [
        _servico(Decimal("50.00"), TipoCobranca.POR_DIARIA),
        _servico(Decimal("30.00"), TipoCobranca.POR_PESSOA),
        _servico(Decimal("80.00"), TipoCobranca.TAXA_UNICA),
    ]
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("100.00"),
        check_in=date(2026, 10, 10),
        check_out=date(2026, 10, 12),
        hospedes=[Hospede(28), Hospede(7)],
        tarifas_temporada=tarifas,
        servicos_adicionais=servicos,
        early_check_in=True,
        late_check_out=True,
        nao_reembolsavel=True,
    )

    resultado = calcular_preco_reserva(entrada)

    # Diárias: dia 10 = 200 (primeira diária), dia 11 = 100 => subtotal_diarias = 300.00
    # Criança (7 anos): 300 * 0.50 = 150.00
    # Early + Late: (200 * 0.30) + (200 * 0.30) = 60.00 + 60.00 = 120.00
    # Serviços: (50 * 2) + (30 * 2) + 80 = 100 + 60 + 80 = 240.00
    # Subtotal antes do desconto: 300 + 150 + 120 + 240 = 810.00
    # Desconto 10%: 81.00 => Total: 729.00
    assert resultado.subtotal_diarias == Decimal("300.00")
    assert resultado.adicional_hospedes == Decimal("150.00")
    assert resultado.adicional_early_late == Decimal("120.00")
    assert resultado.total_servicos == Decimal("240.00")
    assert resultado.desconto_nao_reembolsavel == Decimal("81.00")
    assert resultado.total == Decimal("729.00")


@pytest.mark.parametrize(
    ("check_in", "check_out", "preco_diaria", "idades"),
    [
        (date(2026, 11, 5), date(2026, 11, 5), Decimal("100.00"), [20]),
        (date(2026, 11, 6), date(2026, 11, 5), Decimal("100.00"), [20]),
        (date(2026, 11, 5), date(2026, 11, 6), Decimal("-1.00"), [20]),
        (date(2026, 11, 5), date(2026, 11, 6), Decimal("100.00"), [-1]),
    ],
)
def test_entradas_invalidas_levantam_value_error(
    check_in, check_out, preco_diaria, idades
):
    entrada = EntradaCalculoReserva(
        preco_diaria=preco_diaria,
        check_in=check_in,
        check_out=check_out,
        hospedes=[Hospede(i) for i in idades],
        tarifas_temporada=[],
        servicos_adicionais=[],
    )

    with pytest.raises(ValueError):
        calcular_preco_reserva(entrada)