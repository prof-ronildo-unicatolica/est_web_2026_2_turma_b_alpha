
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.services.reserva_service import (
    AutorizacaoCancelamentoError,
    EstadoCancelamentoInvalidoError,
    SolicitacaoCancelamento,
    avaliar_cancelamento_reserva,
)


def test_cenario_1_reembolsavel_dentro_48h_sem_multa():
    check_in = datetime(2026, 12, 10, 14, 0)
    data_cancelamento = check_in - timedelta(hours=48)

    resultado = avaliar_cancelamento_reserva(
        SolicitacaoCancelamento(
            reserva_id="res-1",
            dono_usuario_id="user-1",
            solicitante_usuario_id="user-1",
            status_atual="CONFIRMADA",
            valor_total=Decimal("600.00"),
            check_in=check_in,
            data_cancelamento=data_cancelamento,
            nao_reembolsavel=False,
        )
    )

    assert resultado.status_atual == "CANCELADA"
    assert resultado.percentual_multa == Decimal("0.00")
    assert resultado.valor_multa == Decimal("0.00")
    assert resultado.valor_reembolso == Decimal("600.00")


def test_cenario_2_reembolsavel_fora_48h_multa_50():
    check_in = datetime(2026, 12, 10, 14, 0)
    data_cancelamento = check_in - timedelta(hours=24)

    resultado = avaliar_cancelamento_reserva(
        SolicitacaoCancelamento(
            reserva_id="res-2",
            dono_usuario_id="user-1",
            solicitante_usuario_id="user-1",
            status_atual="CONFIRMADA",
            valor_total=Decimal("600.00"),
            check_in=check_in,
            data_cancelamento=data_cancelamento,
            nao_reembolsavel=False,
        )
    )

    assert resultado.status_atual == "CANCELADA"
    assert resultado.percentual_multa == Decimal("50.00")
    assert resultado.valor_multa == Decimal("300.00")
    assert resultado.valor_reembolso == Decimal("300.00")


def test_cenario_3_nao_reembolsavel_multa_100():
    check_in = datetime(2026, 12, 10, 14, 0)
    data_cancelamento = check_in - timedelta(hours=72)

    resultado = avaliar_cancelamento_reserva(
        SolicitacaoCancelamento(
            reserva_id="res-3",
            dono_usuario_id="user-1",
            solicitante_usuario_id="user-1",
            status_atual="CONFIRMADA",
            valor_total=Decimal("600.00"),
            check_in=check_in,
            data_cancelamento=data_cancelamento,
            nao_reembolsavel=True,
        )
    )

    assert resultado.status_atual == "CANCELADA"
    assert resultado.percentual_multa == Decimal("100.00")
    assert resultado.valor_multa == Decimal("600.00")
    assert resultado.valor_reembolso == Decimal("0.00")


def test_cenario_4_bloqueio_outro_usuario_e_ja_cancelada():
    check_in = datetime(2026, 12, 10, 14, 0)
    data_cancelamento = check_in - timedelta(hours=72)

    with pytest.raises(AutorizacaoCancelamentoError):
        avaliar_cancelamento_reserva(
            SolicitacaoCancelamento(
                reserva_id="res-4",
                dono_usuario_id="user-1",
                solicitante_usuario_id="user-2",
                status_atual="CONFIRMADA",
                valor_total=Decimal("600.00"),
                check_in=check_in,
                data_cancelamento=data_cancelamento,
            )
        )

    with pytest.raises(EstadoCancelamentoInvalidoError):
        avaliar_cancelamento_reserva(
            SolicitacaoCancelamento(
                reserva_id="res-4",
                dono_usuario_id="user-1",
                solicitante_usuario_id="user-1",
                status_atual="CANCELADA",
                valor_total=Decimal("600.00"),
                check_in=check_in,
                data_cancelamento=data_cancelamento,
            )
        )
