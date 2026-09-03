from sqlalchemy.orm import Session, joinedload

from app.models.hotel import Cidade, Hotel


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

    def get_by_nome(self, nome: str) -> Cidade | None:
        return self.db.query(Cidade).filter(Cidade.nome == nome).first()

    def get_by_id(self, cidade_id) -> Cidade | None:
        return self.db.query(Cidade).filter(Cidade.id == cidade_id).first()

    def list(self) -> list[Cidade]:
        return self.db.query(Cidade).order_by(Cidade.nome).all()


class HotelRepository:
    """Acesso ao banco para a entidade Hotel."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, nome: str, cidade_id) -> Hotel:
        hotel = Hotel(nome=nome, cidade_id=cidade_id)
        self.db.add(hotel)
        self.db.commit()
        self.db.refresh(hotel)
        return hotel

    def list(self) -> list[Hotel]:
        return (
            self.db.query(Hotel)
            # joinedload: traz a cidade no MESMO SELECT, via JOIN. Sem isso,
            # cada hotel da lista dispara um SELECT extra quando alguem le
            # 'hotel.cidade' -- o problema N+1 (ver item 3 da issue #13).
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