import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.servico_adicional import ServicoAdicionalRepository
from app.schemas.servico_adicional import ServicoAdicionalCreate, ServicoAdicionalUpdate


class ServicoAdicionalService:
    def __init__(self, db: Session):
        self.repo = ServicoAdicionalRepository(db)

    def criar_servico(self, hotel_id: uuid.UUID, schema: ServicoAdicionalCreate):
        return self.repo.create(hotel_id, schema)

    def listar_por_hotel(self, hotel_id: uuid.UUID, skip: int = 0, limit: int = 100):
        return self.repo.get_multi_by_hotel(hotel_id, skip=skip, limit=limit)

    def obter_por_id(self, servico_id: uuid.UUID):
        servico = self.repo.get_by_id(servico_id)
        if not servico:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Serviço adicional não encontrado."
            )
        return servico

    def atualizar_servico(self, servico_id: uuid.UUID, schema: ServicoAdicionalUpdate):
        servico = self.obter_por_id(servico_id)
        return self.repo.update(servico, schema)

    def deletar_servico(self, servico_id: uuid.UUID):
        servico = self.obter_por_id(servico_id)
        self.repo.delete(servico)
        return {"detail": "Serviço adicional removido com sucesso."}