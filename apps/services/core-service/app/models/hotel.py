import uuid
from typing import List

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.tutorial import Base

hotel_comodidades = Table(
    "hotel_comodidades",
    Base.metadata,
    Column(
        "hotel_id",
        ForeignKey("hoteis.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "comodidade_id",
        ForeignKey("comodidades.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Cidade(Base):
    __tablename__ = "cidades"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    limite_territorial: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )

    hoteis: Mapped[List["Hotel"]] = relationship(
        back_populates="cidade",
        cascade="all, delete-orphan",
    )


class Hotel(Base):
    __tablename__ = "hoteis"
    __table_args__ = (
        CheckConstraint(
            "estrelas >= 1 AND estrelas <= 5",
            name="ck_hoteis_estrelas_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)

    estrelas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
    )

    cidade_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cidades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    cidade: Mapped["Cidade"] = relationship(back_populates="hoteis")

    comodidades: Mapped[List["Comodidade"]] = relationship(
        secondary=hotel_comodidades,
        back_populates="hoteis",
    )


class Comodidade(Base):
    __tablename__ = "comodidades"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    hoteis: Mapped[List["Hotel"]] = relationship(
        secondary=hotel_comodidades,
        back_populates="comodidades",
    )
    