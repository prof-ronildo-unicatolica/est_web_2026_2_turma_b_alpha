from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Sequence

from app.models.servico_adicional import ServicoAdicional, TipoCobranca
from app.models.tarifa_temporada import TarifaTemporada

ZERO = Decimal("0.00")
CEM = Decimal("100")
PERCENTUAL_CRIANCA = Decimal("0.50")
PERCENTUAL_EARLY_LATE = Decimal("0.30")
PERCENTUAL_NAO_REEMBOLSAVEL = Decimal("0.10")


@dataclass(frozen=True)
class Hospede:
    idade: int


@dataclass(frozen=True)
class EntradaCalculoReserva:
    preco_diaria: Decimal
    check_in: date
    check_out: date
    hospedes: Sequence[Hospede]
    tarifas_temporada: Sequence[TarifaTemporada]
    servicos_adicionais: Sequence[ServicoAdicional]
    early_check_in: bool = False
    late_check_out: bool = False
    nao_reembolsavel: bool = False


@dataclass(frozen=True)
class ResultadoCalculoReserva:
    quantidade_diarias: int
    subtotal_diarias: Decimal
    adicional_hospedes: Decimal
    adicional_early_late: Decimal
    total_servicos: Decimal
    desconto_nao_reembolsavel: Decimal
    total: Decimal


def _moeda(valor: Decimal) -> Decimal:
    """Arredonda um valor monetário para duas casas decimais."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _validar_entrada(entrada: EntradaCalculoReserva) -> None:
    if entrada.check_out <= entrada.check_in:
        raise ValueError("check_out deve ser posterior ao check_in")

    if entrada.preco_diaria < ZERO:
        raise ValueError("preco_diaria não pode ser negativo")

    for hospede in entrada.hospedes:
        if hospede.idade < 0:
            raise ValueError("idade do hóspede não pode ser negativa")


def _buscar_tarifa_da_data(
    data_diaria: date,
    tarifas: Sequence[TarifaTemporada],
) -> TarifaTemporada | None:
    for tarifa in tarifas:
        if tarifa.data_inicio <= data_diaria <= tarifa.data_fim:
            return tarifa

    return None


def _calcular_valor_diaria(
    preco_base: Decimal,
    data_diaria: date,
    tarifas: Sequence[TarifaTemporada],
) -> Decimal:
    tarifa = _buscar_tarifa_da_data(data_diaria, tarifas)

    if tarifa is None:
        return preco_base

    if tarifa.preco_diferenciado is not None:
        return Decimal(tarifa.preco_diferenciado)

    return preco_base * Decimal(tarifa.multiplicador)


def _calcular_diarias(
    entrada: EntradaCalculoReserva,
) -> tuple[int, Decimal, Decimal]:
    quantidade_diarias = (entrada.check_out - entrada.check_in).days

    subtotal = ZERO
    primeira_diaria = ZERO

    for indice in range(quantidade_diarias):
        data_diaria = entrada.check_in + timedelta(days=indice)

        valor_diaria = _calcular_valor_diaria(
            entrada.preco_diaria,
            data_diaria,
            entrada.tarifas_temporada,
        )

        if indice == 0:
            primeira_diaria = valor_diaria

        subtotal += valor_diaria

    return quantidade_diarias, _moeda(subtotal), _moeda(primeira_diaria)


def _calcular_adicional_hospedes(
    subtotal_diarias: Decimal,
    hospedes: Sequence[Hospede],
) -> Decimal:
    adicional = ZERO

    for hospede in hospedes:
        if 0 <= hospede.idade <= 5:
            continue

        if 6 <= hospede.idade <= 12:
            adicional += subtotal_diarias * PERCENTUAL_CRIANCA

    return _moeda(adicional)


def _calcular_early_late(
    primeira_diaria: Decimal,
    early_check_in: bool,
    late_check_out: bool,
) -> Decimal:
    adicional = ZERO

    if early_check_in:
        adicional += primeira_diaria * PERCENTUAL_EARLY_LATE

    if late_check_out:
        adicional += primeira_diaria * PERCENTUAL_EARLY_LATE

    return _moeda(adicional)


def _calcular_servicos(
    servicos: Sequence[ServicoAdicional],
    quantidade_diarias: int,
    quantidade_hospedes: int,
) -> Decimal:
    total = ZERO

    for servico in servicos:
        preco = Decimal(servico.preco)

        if servico.tipo_cobranca == TipoCobranca.POR_DIARIA:
            total += preco * quantidade_diarias
        elif servico.tipo_cobranca == TipoCobranca.POR_PESSOA:
            total += preco * quantidade_hospedes
        elif servico.tipo_cobranca == TipoCobranca.TAXA_UNICA:
            total += preco

    return _moeda(total)


def calcular_preco_reserva(
    entrada: EntradaCalculoReserva,
) -> ResultadoCalculoReserva:
    """
    Calcula o preço oficial de uma reserva.

    Ordem das regras:
    1. Diárias base e tarifa de temporada.
    2. Regras de hóspedes por idade.
    3. Early check-in e late check-out.
    4. Serviços adicionais.
    5. Desconto de tarifa não reembolsável.
    """
    _validar_entrada(entrada)

    (
        quantidade_diarias,
        subtotal_diarias,
        primeira_diaria,
    ) = _calcular_diarias(entrada)

    adicional_hospedes = _calcular_adicional_hospedes(
        subtotal_diarias,
        entrada.hospedes,
    )

    adicional_early_late = _calcular_early_late(
        primeira_diaria,
        entrada.early_check_in,
        entrada.late_check_out,
    )

    total_servicos = _calcular_servicos(
        entrada.servicos_adicionais,
        quantidade_diarias,
        len(entrada.hospedes),
    )

    subtotal = (
        subtotal_diarias
        + adicional_hospedes
        + adicional_early_late
        + total_servicos
    )

    desconto_nao_reembolsavel = ZERO

    if entrada.nao_reembolsavel:
        desconto_nao_reembolsavel = _moeda(
            subtotal * PERCENTUAL_NAO_REEMBOLSAVEL
        )

    total = _moeda(subtotal - desconto_nao_reembolsavel)

    return ResultadoCalculoReserva(
        quantidade_diarias=quantidade_diarias,
        subtotal_diarias=subtotal_diarias,
        adicional_hospedes=adicional_hospedes,
        adicional_early_late=adicional_early_late,
        total_servicos=total_servicos,
        desconto_nao_reembolsavel=desconto_nao_reembolsavel,
        total=total,
    )