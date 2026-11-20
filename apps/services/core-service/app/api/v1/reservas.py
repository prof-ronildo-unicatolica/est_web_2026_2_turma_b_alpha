from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.rabbitmq import publish_event
from app.models.reserva import Reserva, StatusReserva
from app.repositories.quarto_repository import QuartoRepository
from app.repositories.servico_adicional import ServicoAdicionalRepository
from app.repositories.tarifa_temporada import TarifaTemporadaRepository
from app.schemas.reserva import (
    ReservaCreateRequest,
    ReservaPreviewRequest,
    ReservaResponse,
    ReservaSolicitacaoResponse,
)
from app.services.reserva_service import (
    EntradaCalculoReserva,
    Hospede,
    calcular_preco_reserva,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])

FILA_SOLICITACOES_RESERVA = "solicitacoes-reserva"


def _validar_e_calcular_reserva(dados: ReservaPreviewRequest, db: Session):
    quarto = QuartoRepository(db).get_by_id(dados.quarto_id)
    if quarto is None:
        raise HTTPException(status_code=404, detail="Quarto nao encontrado.")

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
            detail="Quantidade de criancas excede a capacidade do quarto.",
        )

    if len(set(dados.servicos_adicionais_ids)) != len(dados.servicos_adicionais_ids):
        raise HTTPException(
            status_code=400,
            detail="Nao informe servicos adicionais repetidos.",
        )

    tarifas = TarifaTemporadaRepository(db).get_multi_by_quarto(dados.quarto_id)
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
            detail="Um ou mais servicos adicionais sao invalidos para este hotel.",
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

    return quarto, hospedes, resultado


@router.post("/preview")
def visualizar_preco_reserva(
    dados: ReservaPreviewRequest,
    db: Session = Depends(get_db),
):
    quarto, hospedes, resultado = _validar_e_calcular_reserva(dados, db)

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
        "desconto_nao_reembolsavel": str(resultado.desconto_nao_reembolsavel),
        "total": str(resultado.total),
    }


@router.get("", response_model=list[ReservaResponse])
def listar_reservas(
    status_filtro: StatusReserva | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
    usuario_atual: dict = Depends(get_current_user),
):
    stmt = (
        select(Reserva)
        .where(Reserva.usuario_id == usuario_atual["id"])
        .order_by(desc(Reserva.criado_em))
    )
    if status_filtro is not None:
        stmt = stmt.where(Reserva.status == status_filtro)

    return list(db.scalars(stmt).all())


@router.get("/{reserva_id}", response_model=ReservaResponse)
def obter_reserva_por_id(
    reserva_id: UUID,
    db: Session = Depends(get_db),
    usuario_atual: dict = Depends(get_current_user),
):
    reserva = db.scalar(select(Reserva).where(Reserva.id == reserva_id))
    if reserva is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva nao encontrada.",
        )

    if str(reserva.usuario_id) != str(usuario_atual["id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado a esta reserva.",
        )

    return reserva


@router.post(
    "",
    response_model=ReservaSolicitacaoResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def solicitar_reserva(
    dados: ReservaCreateRequest,
    db: Session = Depends(get_db),
    usuario_atual: dict = Depends(get_current_user),
):
    quarto, _, resultado = _validar_e_calcular_reserva(dados, db)

    servicos_ids_str = [str(sid) for sid in dados.servicos_adicionais_ids]

    reserva = Reserva(
        usuario_id=usuario_atual["id"],
        quarto_id=quarto.id,
        check_in=dados.check_in,
        check_out=dados.check_out,
        hospedes_idades=dados.hospedes_idades,
        servicos_adicionais_ids=servicos_ids_str,
        early_check_in=dados.early_check_in,
        late_check_out=dados.late_check_out,
        nao_reembolsavel=dados.nao_reembolsavel,
        valor_total=resultado.total,
        status=StatusReserva.PENDENTE,
    )

    db.add(reserva)
    db.commit()
    db.refresh(reserva)

    evento = {
        "evento": "SOLICITACAO_RESERVA_CRIADA",
        "reserva_id": str(reserva.id),
        "usuario_id": str(reserva.usuario_id),
        "quarto_id": str(reserva.quarto_id),
        "check_in": reserva.check_in.isoformat(),
        "check_out": reserva.check_out.isoformat(),
        "valor_total": str(reserva.valor_total),
        "status": reserva.status.value,
    }

    try:
        await publish_event(FILA_SOLICITACOES_RESERVA, evento)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Reserva registrada como PENDENTE, mas houve falha ao publicar na fila de processamento.",
        ) from exc

    return ReservaSolicitacaoResponse.model_validate(reserva)