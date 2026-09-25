import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.tutorial import Base


class TarifaTemporada(Base):
    __tablename__ = "tarifas_temporada"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quarto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("quartos.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    data_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[date] = mapped_column(Date, nullable=False)
    multiplicador: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), default=1.00, nullable=False
    )
    preco_diferenciado: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    quarto = relationship("Quarto", back_populates="tarifas_temporada")

    __table_args__ = (
        CheckConstraint("data_fim >= data_inicio", name="ck_tarifa_datas_validas"),
        CheckConstraint("multiplicador > 0", name="ck_tarifa_multiplicador_positivo"),
    )