import uuid

from sqlalchemy.orm import Session

from app.models.tarifa_temporada import TarifaTemporada
from app.schemas.tarifa_temporada import TarifaTemporadaCreate, TarifaTemporadaUpdate


class TarifaTemporadaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, quarto_id: uuid.UUID, schema: TarifaTemporadaCreate) -> TarifaTemporada:
        db_obj = TarifaTemporada(**schema.model_dump(), quarto_id=quarto_id)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, tarifa_id: uuid.UUID) -> TarifaTemporada | None:
        return self.db.query(TarifaTemporada).filter(TarifaTemporada.id == tarifa_id).first()

    def get_multi_by_quarto(self, quarto_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[TarifaTemporada]:
        return (
            self.db.query(TarifaTemporada)
            .filter(TarifaTemporada.quarto_id == quarto_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, db_obj: TarifaTemporada, schema: TarifaTemporadaUpdate) -> TarifaTemporada:
        update_data = schema.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: TarifaTemporada) -> None:
        self.db.delete(db_obj)
        self.db.commit()