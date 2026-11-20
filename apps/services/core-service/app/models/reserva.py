import enum
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.tutorial import Base


class StatusReserva(str, enum.Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADA = "CONFIRMADA"
    REJEITADA = "REJEITADA"
    CANCELADA = "CANCELADA"


class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        CheckConstraint("check_out > check_in", name="ck_reservas_periodo_valido"),
        CheckConstraint("valor_total >= 0", name="ck_reservas_valor_total_nao_negativo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quarto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quartos.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    check_in: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_out: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    hospedes_idades: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    servicos_adicionais_ids: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    early_check_in: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    late_check_out: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    nao_reembolsavel: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    valor_total: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    status: Mapped[StatusReserva] = mapped_column(
        Enum(StatusReserva, name="status_reserva_enum"),
        nullable=False,
        default=StatusReserva.PENDENTE,
        index=True,
    )

    motivo_rejeicao: Mapped[str | None] = mapped_column(String(255), nullable=True)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
