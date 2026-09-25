from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorDatabase
from sqlalchemy.orm import Session

from app.repositories.hotel_repository import HotelRepository
from app.repositories.quarto_repository import QuartoRepository


class CatalogoHoteisService:
    """Mantém a projeção denormalizada de hotéis no MongoDB.

    PostgreSQL permanece como fonte de verdade.
    MongoDB contém somente uma projeção otimizada para leitura pública.
    """

    COLLECTION_NAME = "catalogo_hoteis"

    def __init__(
        self,
        db: Session,
        mongo_db: AsyncIOMotorDatabase,
    ) -> None:
        self.db = db
        self.mongo_db = mongo_db
        self.hotel_repository = HotelRepository(db)
        self.quarto_repository = QuartoRepository(db)

    async def sincronizar_hotel(self, hotel_id: UUID) -> None:
        """Reconstrói integralmente a projeção de um hotel.

        A operação é idempotente: executar várias vezes para o mesmo
        hotel mantém apenas um documento atualizado.
        """
        hotel = self.hotel_repository.get_by_id(hotel_id)

        if hotel is None:
            await self.remover_hotel(hotel_id)
            return

        quartos = self.quarto_repository.list_by_hotel(hotel_id)

        documento = {
            "_id": str(hotel.id),
            "hotel_id": str(hotel.id),
            "nome": hotel.nome,
            "cidade": {
                "id": str(hotel.cidade.id),
                "nome": hotel.cidade.nome,
            },
            "estrelas": hotel.estrelas,
            "quartos": [
                {
                    "id": str(quarto.id),
                    "tipo": quarto.tipo,
                    "preco_diaria": self._decimal_para_float(
                        quarto.preco_diaria
                    ),
                    "max_adultos": quarto.max_adultos,
                    "max_criancas": quarto.max_criancas,
                }
                for quarto in quartos
            ],
        }

        collection = self.mongo_db[self.COLLECTION_NAME]

        await collection.replace_one(
            {"_id": str(hotel.id)},
            documento,
            upsert=True,
        )

    async def remover_hotel(self, hotel_id: UUID) -> None:
        """Remove a projeção de um hotel inexistente no PostgreSQL."""
        collection = self.mongo_db[self.COLLECTION_NAME]

        await collection.delete_one(
            {"_id": str(hotel_id)}
        )

    @staticmethod
    def _decimal_para_float(value: Decimal | float | int) -> float:
        return float(value)