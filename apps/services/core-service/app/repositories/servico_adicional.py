import uuid

from sqlalchemy.orm import Session

from app.models.servico_adicional import ServicoAdicional
from app.schemas.servico_adicional import ServicoAdicionalCreate, ServicoAdicionalUpdate


class ServicoAdicionalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, hotel_id: uuid.UUID, schema: ServicoAdicionalCreate) -> ServicoAdicional:
        db_obj = ServicoAdicional(**schema.model_dump(), hotel_id=hotel_id)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, servico_id: uuid.UUID) -> ServicoAdicional | None:
        return self.db.query(ServicoAdicional).filter(ServicoAdicional.id == servico_id).first()

    def get_multi_by_hotel(self, hotel_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[ServicoAdicional]:
        return (
            self.db.query(ServicoAdicional)
            .filter(ServicoAdicional.hotel_id == hotel_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, db_obj: ServicoAdicional, schema: ServicoAdicionalUpdate) -> ServicoAdicional:
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ServicoAdicional) -> None:
        self.db.delete(db_obj)
        self.db.commit()