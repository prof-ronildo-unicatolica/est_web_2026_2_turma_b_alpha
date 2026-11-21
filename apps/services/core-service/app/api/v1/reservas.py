from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.quarto_repository import QuartoRepository
from app.repositories.servico_adicional import ServicoAdicionalRepository
from app.repositories.tarifa_temporada import TarifaTemporadaRepository
from app.schemas.reserva import ReservaPreviewRequest
from app.services.reserva_service import (
    EntradaCalculoReserva,
    Hospede,
    calcular_preco_reserva,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("/preview")
def visualizar_preco_reserva(
    dados: ReservaPreviewRequest,
    db: Session = Depends(get_db),
):
    quarto = QuartoRepository(db).get_by_id(dados.quarto_id)

    if quarto is None:
        raise HTTPException(status_code=404, detail="Quarto não encontrado.")

    hospedes = [Hospede(idade=idade) for idade in dados.hospedes_idades]

    adultos = sum(idade > 12 for idade in dados.hospedes_idades)
    criancas = len(hospedes) - adultos

    if adultos > quarto.max_adultos:
        raise HTTPException(
            status_code=400,
            detail="Quantidade de adultos excede a capacidade do quarto.",
        )

    if criancas > quarto.max_criancas:
        raise HTTPException(
            status_code=400,
            detail="Quantidade de crianças excede a capacidade do quarto.",
        )

    if len(set(dados.servicos_adicionais_ids)) != len(
        dados.servicos_adicionais_ids
    ):
        raise HTTPException(
            status_code=400,
            detail="Não informe serviços adicionais repetidos.",
        )

    tarifas = TarifaTemporadaRepository(db).get_multi_by_quarto(
        dados.quarto_id
    )

    servicos_disponiveis = ServicoAdicionalRepository(db).get_multi_by_hotel(
        quarto.hotel_id
    )

    servicos_selecionados = [
        servico
        for servico in servicos_disponiveis
        if servico.id in dados.servicos_adicionais_ids
    ]

    if len(servicos_selecionados) != len(dados.servicos_adicionais_ids):
        raise HTTPException(
            status_code=400,
            detail="Um ou mais serviços adicionais são inválidos para este hotel.",
        )

    entrada = EntradaCalculoReserva(
        preco_diaria=Decimal(str(quarto.preco_diaria)),
        check_in=dados.check_in,
        check_out=dados.check_out,
        hospedes=hospedes,
        tarifas_temporada=tarifas,
        servicos_adicionais=servicos_selecionados,
        early_check_in=dados.early_check_in,
        late_check_out=dados.late_check_out,
        nao_reembolsavel=dados.nao_reembolsavel,
    )

    try:
        resultado = calcular_preco_reserva(entrada)
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro

    return {
        "quarto_id": str(quarto.id),
        "check_in": dados.check_in,
        "check_out": dados.check_out,
        "quantidade_diarias": resultado.quantidade_diarias,
        "quantidade_hospedes": len(hospedes),
        "subtotal_diarias": str(resultado.subtotal_diarias),
        "adicional_hospedes": str(resultado.adicional_hospedes),
        "adicional_early_late": str(resultado.adicional_early_late),
        "total_servicos": str(resultado.total_servicos),
        "desconto_nao_reembolsavel": str(
            resultado.desconto_nao_reembolsavel
        ),
        "total": str(resultado.total),
    }