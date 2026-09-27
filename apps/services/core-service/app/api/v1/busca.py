from fastapi import APIRouter, Depends, Query

from app.core.database import get_mongo_db
from app.services.busca_service import BuscaService

router = APIRouter(prefix="/busca", tags=["Busca"])


@router.get(
    "/hoteis",
    summary="Busca publica de hoteis por cidade e/ou estrelas (le do MongoDB)",
)
async def buscar_hoteis(
    cidade: str | None = Query(
        default=None,
        description="Nome da cidade, sem diferenciar maiusculas/minusculas",
    ),
    estrelas: int | None = Query(
        default=None,
        ge=1,
        le=5,
        description="Categoria de estrelas do hotel (1 a 5)",
    ),
    mongo_db=Depends(get_mongo_db),
):
    resultados = await BuscaService(mongo_db).buscar_hoteis(
        cidade=cidade,
        estrelas=estrelas,
    )

    return {"total": len(resultados), "resultados": resultados}