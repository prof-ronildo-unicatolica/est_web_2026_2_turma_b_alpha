from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class BuscaService:
    """Busca publica de hoteis, lendo a projecao catalogo_hoteis no MongoDB.

    Apenas LE a colecao criada pelo CatalogoHoteisService (S4-02, de
    responsabilidade do Wladysson). Nunca escreve nela nem assume nada
    alem do formato de documento ja publicado -- ver "zonas de conflito"
    do plano operacional antes de alterar este arquivo.
    """

    COLLECTION_NAME = "catalogo_hoteis"

    def __init__(self, mongo_db: AsyncIOMotorDatabase) -> None:
        self.mongo_db = mongo_db

    async def buscar_hoteis(
        self,
        cidade: str | None = None,
        estrelas: int | None = None,
    ) -> list[dict[str, Any]]:
        """Filtra a projecao por cidade (case-insensitive) e/ou estrelas.

        Sem filtros, retorna todos os hoteis da projecao. A consulta
        acontece inteiramente no MongoDB (via find), nunca no PostgreSQL --
        e exatamente esse o ponto da S4-03.
        """
        filtro: dict[str, Any] = {}

        if cidade is not None:
            filtro["cidade.nome"] = {"$regex": f"^{cidade}$", "$options": "i"}

        if estrelas is not None:
            filtro["estrelas"] = estrelas

        collection = self.mongo_db[self.COLLECTION_NAME]
        # _id fora da projecao: e um ObjectId/string interno do Mongo, sem
        # valor para quem consome a busca publica.
        cursor = collection.find(filtro, {"_id": 0})

        return [documento async for documento in cursor]