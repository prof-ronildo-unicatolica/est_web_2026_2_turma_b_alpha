from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user
from app.schemas.reserva import (
    CancelamentoReservaRequest,
    CancelamentoReservaResponse,
)
from app.services.reserva_service import (
    AutorizacaoCancelamentoError,
    EstadoCancelamentoInvalidoError,
    SolicitacaoCancelamento,
    avaliar_cancelamento_reserva,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post(
    "/{reserva_id}/cancelar",
    response_model=CancelamentoReservaResponse,
    summary="Cancela uma reserva aplicando regra de 48h e multas",
)
def cancelar_reserva(
    reserva_id: str,
    payload: CancelamentoReservaRequest | None = None,
    usuario_atual: dict = Depends(get_current_user),
):
    data_cancelamento = (
        payload.data_cancelamento
        if payload and payload.data_cancelamento is not None
        else datetime.now(timezone.utc).replace(tzinfo=None)
    )

    solicitacao = SolicitacaoCancelamento(
        reserva_id=reserva_id,
        dono_usuario_id=usuario_atual["id"],
        solicitante_usuario_id=usuario_atual["id"],
        status_atual="CONFIRMADA",
        valor_total=Decimal("0.00"),
        check_in=data_cancelamento,
        data_cancelamento=data_cancelamento,
        nao_reembolsavel=False,
    )

    try:
        resultado = avaliar_cancelamento_reserva(solicitacao)
    except AutorizacaoCancelamentoError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except EstadoCancelamentoInvalidoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return CancelamentoReservaResponse(
        reserva_id=resultado.reserva_id,
        status_anterior=resultado.status_anterior,
        status_atual=resultado.status_atual,
        politica_aplicada=resultado.politica_aplicada,
        data_limite_cancelamento=resultado.data_limite_cancelamento,
        percentual_multa=resultado.percentual_multa,
        valor_multa=resultado.valor_multa,
        valor_reembolso=resultado.valor_reembolso,
    )
