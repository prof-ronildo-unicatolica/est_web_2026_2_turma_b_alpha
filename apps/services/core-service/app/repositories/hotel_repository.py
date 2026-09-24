from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.models.hotel import Cidade, Comodidade, Hotel


class CidadeRepository:
    """Acesso ao banco para a entidade Cidade."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nome: str) -> Cidade:
        cidade = Cidade(nome=nome)
        self.db.add(cidade)
        self.db.commit()
        self.db.refresh(cidade)
        return cidade

    def list(self) -> list[Cidade]:
        return self.db.query(Cidade).order_by(Cidade.nome).all()

    def get_by_id(self, cidade_id) -> Cidade | None:
        return self.db.query(Cidade).filter(Cidade.id == cidade_id).first()

    def get_by_nome(self, nome: str) -> Cidade | None:
        return self.db.query(Cidade).filter(Cidade.nome == nome).first()

    def update(self, cidade: Cidade, nome: str) -> Cidade:
        cidade.nome = nome
        self.db.commit()
        self.db.refresh(cidade)
        return cidade

    def delete(self, cidade: Cidade) -> None:
        self.db.delete(cidade)
        self.db.commit()


class HotelRepository:
    """Acesso ao banco para a entidade Hotel."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nome: str, cidade_id, estrelas: int = 3) -> Hotel:
        hotel = Hotel(
            nome=nome,
            cidade_id=cidade_id,
            estrelas=estrelas,
        )
        self.db.add(hotel)
        self.db.commit()
        self.db.refresh(hotel)
        return self.get_by_id(hotel.id)

    def list(self) -> list[Hotel]:
        return (
            self.db.query(Hotel)
            .options(joinedload(Hotel.cidade))
            .order_by(Hotel.nome)
            .all()
        )

    def list_by_cidade(self, cidade_id) -> list[Hotel]:
        return (
            self.db.query(Hotel)
            .options(joinedload(Hotel.cidade))
            .filter(Hotel.cidade_id == cidade_id)
            .order_by(Hotel.nome)
            .all()
        )

    def get_by_id(self, hotel_id) -> Hotel | None:
        return (
            self.db.query(Hotel)
            .options(joinedload(Hotel.cidade))
            .filter(Hotel.id == hotel_id)
            .first()
        )

    def update(
        self,
        hotel: Hotel,
        nome: str,
        cidade_id,
        estrelas: int,
    ) -> Hotel:
        hotel.nome = nome
        hotel.cidade_id = cidade_id
        hotel.estrelas = estrelas
        self.db.commit()
        self.db.refresh(hotel)
        return self.get_by_id(hotel.id)

    def delete(self, hotel: Hotel) -> None:
        self.db.delete(hotel)
        self.db.commit()


class ComodidadeRepository:
    """Acesso ao banco para a entidade Comodidade."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nome: str) -> Comodidade:
        comodidade = Comodidade(nome=nome)
        self.db.add(comodidade)
        self.db.commit()
        self.db.refresh(comodidade)
        return comodidade

    def list(self) -> list[Comodidade]:
        return self.db.query(Comodidade).order_by(Comodidade.nome).all()

    def get_by_id(self, comodidade_id) -> Comodidade | None:
        return (
            self.db.query(Comodidade)
            .filter(Comodidade.id == comodidade_id)
            .first()
        )

    def get_by_nome(self, nome: str) -> Comodidade | None:
        return (
            self.db.query(Comodidade)
            .filter(Comodidade.nome == nome)
            .first()
        )

    def update(self, comodidade: Comodidade, nome: str) -> Comodidade:
        comodidade.nome = nome
        self.db.commit()
        self.db.refresh(comodidade)
        return comodidade

    def delete(self, comodidade: Comodidade) -> None:
        self.db.delete(comodidade)
        self.db.commit()