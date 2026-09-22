import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.quarto import Quarto
from app.repositories.hotel_repository import HotelRepository
from app.repositories.quarto_repository import QuartoRepository


class QuartoNaoEncontradoError(Exception):
    pass


class HotelNaoEncontradoError(Exception):
    pass


class DadosQuartoInvalidosError(Exception):
    pass


class QuartoService:
    def __init__(self, db: Session):
        self.repository = QuartoRepository(db)
        self.hotel_repository = HotelRepository(db)

    def _validar_dados(
        self,
        preco_diaria: Decimal,
        max_adultos: int,
        max_criancas: int,
    ) -> None:
        if preco_diaria < 0:
            raise DadosQuartoInvalidosError(
                "O preço da diária não pode ser negativo."
            )

        if max_adultos < 1:
            raise DadosQuartoInvalidosError(
                "O quarto deve permitir pelo menos 1 adulto."
            )

        if max_criancas < 0:
            raise DadosQuartoInvalidosError(
                "A capacidade de crianças não pode ser negativa."
            )

    def _validar_hotel(self, hotel_id: uuid.UUID) -> None:
        if self.hotel_repository.get_by_id(hotel_id) is None:
            raise HotelNaoEncontradoError("Hotel não encontrado.")

    def criar(
        self,
        tipo: str,
        preco_diaria: Decimal,
        max_adultos: int,
        max_criancas: int,
        hotel_id: uuid.UUID,
    ) -> Quarto:
        self._validar_dados(
            preco_diaria,
            max_adultos,
            max_criancas,
        )
        self._validar_hotel(hotel_id)

        return self.repository.create(
            tipo=tipo,
            preco_diaria=preco_diaria,
            max_adultos=max_adultos,
            max_criancas=max_criancas,
            hotel_id=hotel_id,
        )

    def listar(self, hotel_id: uuid.UUID | None = None) -> list[Quarto]:
        if hotel_id is not None:
            self._validar_hotel(hotel_id)
            return self.repository.list_by_hotel(hotel_id)

        return self.repository.list()

    def buscar(self, quarto_id: uuid.UUID) -> Quarto:
        quarto = self.repository.get_by_id(quarto_id)

        if quarto is None:
            raise QuartoNaoEncontradoError("Quarto não encontrado.")

        return quarto

    def atualizar(
        self,
        quarto_id: uuid.UUID,
        tipo: str,
        preco_diaria: Decimal,
        max_adultos: int,
        max_criancas: int,
        hotel_id: uuid.UUID,
    ) -> Quarto:
        quarto = self.buscar(quarto_id)

        self._validar_dados(
            preco_diaria,
            max_adultos,
            max_criancas,
        )
        self._validar_hotel(hotel_id)

        return self.repository.update(
            quarto=quarto,
            tipo=tipo,
            preco_diaria=preco_diaria,
            max_adultos=max_adultos,
            max_criancas=max_criancas,
            hotel_id=hotel_id,
        )

    def excluir(self, quarto_id: uuid.UUID) -> None:
        quarto = self.buscar(quarto_id)
        self.repository.delete(quarto)
        