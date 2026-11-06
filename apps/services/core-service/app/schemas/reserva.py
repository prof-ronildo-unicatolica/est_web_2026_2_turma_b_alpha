from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


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
            raise ValueError("A idade dos hóspedes não pode ser negativa.")
        return self