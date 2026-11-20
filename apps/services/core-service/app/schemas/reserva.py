from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.reserva import StatusReserva


class ReservaPreviewRequest(BaseModel):
    quarto_id: UUID
    check_in: date
    check_out: date
    hospedes_idades: list[int] = Field(min_length=1)
    servicos_adicionais_ids: list[UUID] = Field(default_factory=list)
    early_check_in: bool = False
    late_check_out: bool = False
    nao_reembolsavel: bool = False

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.check_out <= self.check_in:
            raise ValueError("Check-out deve ser posterior ao check-in.")
        if any(idade < 0 for idade in self.hospedes_idades):
            raise ValueError("A idade dos hospedes nao pode ser negativa.")
        return self


class ReservaCreateRequest(ReservaPreviewRequest):
    pass


class ReservaSolicitacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    quarto_id: UUID
    check_in: date
    check_out: date
    hospedes_idades: list[int]
    servicos_adicionais_ids: list[str]
    early_check_in: bool
    late_check_out: bool
    nao_reembolsavel: bool
    valor_total: Decimal
    status: StatusReserva
    criado_em: datetime
    mensagem: str = "Solicitacao de reserva recebida e enviada para processamento."


class ReservaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    usuario_id: UUID
    quarto_id: UUID
    check_in: date
    check_out: date
    hospedes_idades: list[int]
    servicos_adicionais_ids: list[str]
    early_check_in: bool
    late_check_out: bool
    nao_reembolsavel: bool
    valor_total: Decimal
    status: StatusReserva
    motivo_rejeicao: str | None = None
    criado_em: datetime
    atualizado_em: datetime | None = None