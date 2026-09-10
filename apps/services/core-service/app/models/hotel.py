import uuid
from typing import List

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.tutorial import Base


class Cidade(Base):
    __tablename__ = "cidades"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    hoteis: Mapped[List["Hotel"]] = relationship(
        back_populates="cidade", cascade="all, delete-orphan"
    )


class Hotel(Base):
    __tablename__ = "hoteis"
    __table_args__ = (
        CheckConstraint("estrelas >= 1 AND estrelas <= 5", name="ck_hoteis_estrelas_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    estrelas: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    cidade_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cidades.id", ondelete="CASCADE"), nullable=False
    )

    cidade: Mapped["Cidade"] = relationship(back_populates="hoteis")