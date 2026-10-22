import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.tarifa_temporada import TarifaTemporadaRepository
from app.schemas.tarifa_temporada import TarifaTemporadaCreate, TarifaTemporadaUpdate


class TarifaTemporadaService:
    def __init__(self, db: Session):
        self.repo = TarifaTemporadaRepository(db)

    def criar_tarifa(self, quarto_id: uuid.UUID, schema: TarifaTemporadaCreate):
        return self.repo.create(quarto_id, schema)

    def listar_por_quarto(self, quarto_id: uuid.UUID, skip: int = 0, limit: int = 100):
        return self.repo.get_multi_by_quarto(quarto_id, skip=skip, limit=limit)

    def obter_por_id(self, tarifa_id: uuid.UUID):
        tarifa = self.repo.get_by_id(tarifa_id)
        if not tarifa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarifa de temporada não encontrada."
            )
        return tarifa

    def atualizar_tarifa(self, tarifa_id: uuid.UUID, schema: TarifaTemporadaUpdate):
        tarifa = self.obter_por_id(tarifa_id)
        return self.repo.update(tarifa, schema)

    def deletar_tarifa(self, tarifa_id: uuid.UUID):
        tarifa = self.obter_por_id(tarifa_id)
        self.repo.delete(tarifa)
        return {"detail": "Tarifa de temporada removida com sucesso."}