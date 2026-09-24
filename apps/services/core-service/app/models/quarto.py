import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.tutorial import Base

if TYPE_CHECKING:
    from app.models.hotel import Hotel

class Quarto(Base):
    __tablename__ = "quartos"
    __table_args__ = (
        CheckConstraint("preco_diaria >= 0", name="ck_quartos_preco_nao_negativo"),
        CheckConstraint("max_adultos >= 1", name="ck_quartos_max_adultos_positivo"),
        CheckConstraint("max_criancas >= 0", name="ck_quartos_max_criancas_nao_negativo"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    tipo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    preco_diaria: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    max_adultos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    max_criancas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    hotel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hoteis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    hotel: Mapped["Hotel"] = relationship(
        back_populates="quartos",
    )
    