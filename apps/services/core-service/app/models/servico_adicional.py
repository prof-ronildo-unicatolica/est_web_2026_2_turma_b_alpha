import enum
import uuid
from decimal import Decimal

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.tutorial import Base


class TipoCobranca(str, enum.Enum):
    POR_DIARIA = "POR_DIARIA"
    POR_PESSOA = "POR_PESSOA"
    TAXA_UNICA = "TAXA_UNICA"


class ServicoAdicional(Base):
    __tablename__ = "servicos_adicionais"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    hotel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hoteis.id", ondelete="CASCADE"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tipo_cobranca: Mapped[TipoCobranca] = mapped_column(
        SQLEnum(TipoCobranca, name="tipo_cobranca_enum"),
        default=TipoCobranca.TAXA_UNICA,
        nullable=False,
    )

    hotel = relationship("Hotel", back_populates="servicos_adicionais")