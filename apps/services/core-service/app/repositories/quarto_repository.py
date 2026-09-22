from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload

from app.models.quarto import Quarto


class QuartoRepository:
    """Acesso ao banco para a entidade Quarto."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        tipo: str,
        preco_diaria: Decimal,
        max_adultos: int,
        max_criancas: int,
        hotel_id: uuid.UUID,
    ) -> Quarto:
        quarto = Quarto(
            tipo=tipo,
            preco_diaria=preco_diaria,
            max_adultos=max_adultos,
            max_criancas=max_criancas,
            hotel_id=hotel_id,
        )

        self.db.add(quarto)
        self.db.commit()
        self.db.refresh(quarto)

        return quarto

    def list(self) -> list[Quarto]:
        return (
            self.db.query(Quarto)
            .options(joinedload(Quarto.hotel))
            .order_by(Quarto.tipo)
            .all()
        )

    def list_by_hotel(self, hotel_id: uuid.UUID) -> list[Quarto]:
        return (
            self.db.query(Quarto)
            .options(joinedload(Quarto.hotel))
            .filter(Quarto.hotel_id == hotel_id)
            .order_by(Quarto.tipo)
            .all()
        )

    def get_by_id(self, quarto_id: uuid.UUID) -> Quarto | None:
        return (
            self.db.query(Quarto)
            .options(joinedload(Quarto.hotel))
            .filter(Quarto.id == quarto_id)
            .first()
        )

    def update(
        self,
        quarto: Quarto,
        tipo: str,
        preco_diaria: Decimal,
        max_adultos: int,
        max_criancas: int,
        hotel_id: uuid.UUID,
    ) -> Quarto:
        quarto.tipo = tipo
        quarto.preco_diaria = preco_diaria
        quarto.max_adultos = max_adultos
        quarto.max_criancas = max_criancas
        quarto.hotel_id = hotel_id

        self.db.commit()
        self.db.refresh(quarto)

        return quarto

    def delete(self, quarto: Quarto) -> None:
        self.db.delete(quarto)
        self.db.commit()
        