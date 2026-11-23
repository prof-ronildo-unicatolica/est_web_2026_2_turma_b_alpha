from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CancelamentoReservaRequest(BaseModel):
    data_cancelamento: datetime | None = Field(
        default=None,
        description="Data/hora do cancelamento; se omitida, usa o momento atual UTC.",
    )


class CancelamentoReservaResponse(BaseModel):
    reserva_id: str
    status_anterior: str
    status_atual: str
    politica_aplicada: str
    data_limite_cancelamento: datetime
    percentual_multa: Decimal
    valor_multa: Decimal
    valor_reembolso: Decimal
