from datetime import date
from decimal import Decimal

import pytest

from app.services.reserva_service import (
    EntradaCalculoReserva,
    Hospede,
    calcular_preco_reserva,
)


def test_calculo_basico_e_capacidade_valida():
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("200.00"),
        check_in=date(2026, 12, 10),
        check_out=date(2026, 12, 12),
        hospedes=[Hospede(idade=30), Hospede(idade=28)],
        tarifas_temporada=[],
        servicos_adicionais=[],
        max_adultos=2,
        max_criancas=1,
    )

    resultado = calcular_preco_reserva(entrada)

    assert resultado.quantidade_diarias == 2
    assert resultado.subtotal_diarias == Decimal("400.00")
    assert resultado.adicional_hospedes == Decimal("0.00")
    assert resultado.total == Decimal("400.00")


def test_capacidade_exata_adultos_e_criancas_permitida():
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("250.00"),
        check_in=date(2026, 12, 10),
        check_out=date(2026, 12, 11),
        hospedes=[
            Hospede(idade=35),
            Hospede(idade=25),
            Hospede(idade=4),
            Hospede(idade=10),
        ],
        tarifas_temporada=[],
        servicos_adicionais=[],
        max_adultos=2,
        max_criancas=2,
    )

    resultado = calcular_preco_reserva(entrada)

    assert resultado.quantidade_diarias == 1
    assert resultado.subtotal_diarias == Decimal("250.00")
    assert resultado.adicional_hospedes == Decimal("125.00")
    assert resultado.total == Decimal("375.00")


def test_excede_max_adultos_levanta_erro():
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("200.00"),
        check_in=date(2026, 12, 10),
        check_out=date(2026, 12, 12),
        hospedes=[Hospede(idade=30), Hospede(idade=28), Hospede(idade=22)],
        tarifas_temporada=[],
        servicos_adicionais=[],
        max_adultos=2,
        max_criancas=1,
    )

    with pytest.raises(ValueError, match="adultos"):
        calcular_preco_reserva(entrada)


def test_excede_max_criancas_levanta_erro():
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("200.00"),
        check_in=date(2026, 12, 10),
        check_out=date(2026, 12, 12),
        hospedes=[Hospede(idade=30), Hospede(idade=5), Hospede(idade=8)],
        tarifas_temporada=[],
        servicos_adicionais=[],
        max_adultos=2,
        max_criancas=1,
    )

    with pytest.raises(ValueError, match="crianças"):
        calcular_preco_reserva(entrada)


def test_idade_negativa_ou_datas_invalidas_levanta_erro():
    entrada_idade_negativa = EntradaCalculoReserva(
        preco_diaria=Decimal("200.00"),
        check_in=date(2026, 12, 10),
        check_out=date(2026, 12, 12),
        hospedes=[Hospede(idade=-1)],
        tarifas_temporada=[],
        servicos_adicionais=[],
    )

    with pytest.raises(ValueError, match="idade"):
        calcular_preco_reserva(entrada_idade_negativa)

    entrada_datas = EntradaCalculoReserva(
        preco_diaria=Decimal("200.00"),
        check_in=date(2026, 12, 12),
        check_out=date(2026, 12, 10),
        hospedes=[Hospede(idade=30)],
        tarifas_temporada=[],
        servicos_adicionais=[],
    )

    with pytest.raises(ValueError, match="check_out"):
        calcular_preco_reserva(entrada_datas)


def test_fronteira_idades_e_desconto_nao_reembolsavel():
    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal("100.00"),
        check_in=date(2026, 12, 10),
        check_out=date(2026, 12, 11),
        hospedes=[
            Hospede(idade=13),
            Hospede(idade=5),
            Hospede(idade=6),
            Hospede(idade=12),
        ],
        tarifas_temporada=[],
        servicos_adicionais=[],
        nao_reembolsavel=True,
        max_adultos=1,
        max_criancas=3,
    )

    resultado = calcular_preco_reserva(entrada)

    assert resultado.subtotal_diarias == Decimal("100.00")
    assert resultado.adicional_hospedes == Decimal("100.00")
    assert resultado.desconto_nao_reembolsavel == Decimal("20.00")
    assert resultado.total == Decimal("180.00")


def test_limites_capacidade_invalidos_e_preco_negativo():
    with pytest.raises(ValueError, match="preco_diaria"):
        calcular_preco_reserva(
            EntradaCalculoReserva(
                preco_diaria=Decimal("-1.00"),
                check_in=date(2026, 12, 10),
                check_out=date(2026, 12, 11),
                hospedes=[],
                tarifas_temporada=[],
                servicos_adicionais=[],
            )
        )

    with pytest.raises(ValueError, match="max_adultos"):
        calcular_preco_reserva(
            EntradaCalculoReserva(
                preco_diaria=Decimal("100.00"),
                check_in=date(2026, 12, 10),
                check_out=date(2026, 12, 11),
                hospedes=[Hospede(idade=20)],
                tarifas_temporada=[],
                servicos_adicionais=[],
                max_adultos=0,
            )
        )

    with pytest.raises(ValueError, match="max_criancas"):
        calcular_preco_reserva(
            EntradaCalculoReserva(
                preco_diaria=Decimal("100.00"),
                check_in=date(2026, 12, 10),
                check_out=date(2026, 12, 11),
                hospedes=[],
                tarifas_temporada=[],
                servicos_adicionais=[],
                max_criancas=-1,
            )
        )
