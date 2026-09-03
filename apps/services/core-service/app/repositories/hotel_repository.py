from sqlalchemy.orm import Session, joinedload

from app.models.hotel import Cidade, Hotel


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
            # 'hotel.cidade' -- o problema N+1 (ver item 3).
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