from unittest.mock import MagicMock

import pytest

from app.services.busca_service import BuscaService


class FakeAsyncCursor:
    """Simula um cursor assincrono do Motor para os testes.

    O metodo find() do Motor retorna um cursor que suporta 'async for';
    esta classe reproduz esse comportamento sem precisar de um MongoDB
    real rodando durante os testes.
    """

    def __init__(self, items):
        self._items = list(items)

    def __aiter__(self):
        return self._iterate()

    async def _iterate(self):
        for item in self._items:
            yield item


def _mongo_db_com_documentos(documentos):
    collection = MagicMock()
    collection.find = MagicMock(return_value=FakeAsyncCursor(documentos))

    db = MagicMock()
    db.__getitem__.return_value = collection

    return db, collection


DOCUMENTOS_EXEMPLO = [
    {
        "hotel_id": "1",
        "nome": "Hotel Beira-Mar",
        "cidade": {"nome": "Fortaleza"},
        "estrelas": 4,
        "quartos": [],
    },
    {
        "hotel_id": "2",
        "nome": "Pousada Central",
        "cidade": {"nome": "Sobral"},
        "estrelas": 2,
        "quartos": [],
    },
    {
        "hotel_id": "3",
        "nome": "Resort Jericoacoara",
        "cidade": {"nome": "Jericoacoara"},
        "estrelas": 4,
        "quartos": [],
    },
]


@pytest.mark.asyncio
async def test_buscar_sem_filtros_retorna_todos_os_documentos():
    mongo_db, collection = _mongo_db_com_documentos(DOCUMENTOS_EXEMPLO)
    service = BuscaService(mongo_db)

    resultado = await service.buscar_hoteis()

    assert len(resultado) == 3
    collection.find.assert_called_once_with({}, {"_id": 0})


@pytest.mark.asyncio
async def test_buscar_filtra_por_cidade_case_insensitive():
    mongo_db, collection = _mongo_db_com_documentos([DOCUMENTOS_EXEMPLO[0]])
    service = BuscaService(mongo_db)

    resultado = await service.buscar_hoteis(cidade="fortaleza")

    assert len(resultado) == 1
    assert resultado[0]["cidade"]["nome"] == "Fortaleza"

    filtro_usado = collection.find.call_args.args[0]
    assert filtro_usado["cidade.nome"]["$options"] == "i"


@pytest.mark.asyncio
async def test_buscar_filtra_por_estrelas():
    mongo_db, collection = _mongo_db_com_documentos(
        [DOCUMENTOS_EXEMPLO[0], DOCUMENTOS_EXEMPLO[2]]
    )
    service = BuscaService(mongo_db)

    resultado = await service.buscar_hoteis(estrelas=4)

    assert len(resultado) == 2

    filtro_usado = collection.find.call_args.args[0]
    assert filtro_usado["estrelas"] == 4


@pytest.mark.asyncio
async def test_buscar_combina_cidade_e_estrelas():
    mongo_db, collection = _mongo_db_com_documentos([DOCUMENTOS_EXEMPLO[0]])
    service = BuscaService(mongo_db)

    resultado = await service.buscar_hoteis(cidade="Fortaleza", estrelas=4)

    assert len(resultado) == 1

    filtro_usado = collection.find.call_args.args[0]
    assert filtro_usado["cidade.nome"]["$regex"] == "^Fortaleza$"
    assert filtro_usado["estrelas"] == 4


@pytest.mark.asyncio
async def test_buscar_sem_resultados_retorna_lista_vazia():
    mongo_db, _collection = _mongo_db_com_documentos([])
    service = BuscaService(mongo_db)

    resultado = await service.buscar_hoteis(cidade="CidadeQueNaoExiste")

    assert resultado == []