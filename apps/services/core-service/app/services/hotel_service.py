from sqlalchemy.orm import Session

from app.models.hotel import Cidade, Comodidade, Hotel
from app.repositories.hotel_repository import (
    CidadeRepository,
    ComodidadeRepository,
    HotelRepository,
)


class RegraDeNegocioError(Exception):
    """Base das exceções de negócio do catálogo."""


class CidadeJaExisteError(RegraDeNegocioError):
    pass

class CidadeNaoEncontradaError(RegraDeNegocioError):
    pass

class CidadeNaoPodeSerExcluidaError(RegraDeNegocioError):
    pass

class HotelNaoEncontradoError(RegraDeNegocioError):
    pass

class ComodidadeJaExisteError(RegraDeNegocioError):
    pass

class ComodidadeNaoEncontradaError(RegraDeNegocioError):
    pass

class CidadeService:
    def __init__(self, db: Session):
        self.repository = CidadeRepository(db)

    def criar(self, nome: str) -> Cidade:
        nome = nome.strip()

        if self.repository.get_by_nome(nome):
            raise CidadeJaExisteError(
                f"Ja existe uma cidade chamada '{nome}'."
            )

        return self.repository.create(nome=nome)

    def listar(self) -> list[Cidade]:
        return self.repository.list()

    def atualizar(self, cidade_id, nome: str) -> Cidade:
        cidade = self.repository.get_by_id(cidade_id)

        if not cidade:
            raise CidadeNaoEncontradaError(
                f"Nao existe cidade com id '{cidade_id}'."
            )

        nome = nome.strip()

        outra = self.repository.get_by_nome(nome)
        if outra and outra.id != cidade.id:
            raise CidadeJaExisteError(
                f"Ja existe uma cidade chamada '{nome}'."
            )

        return self.repository.update(cidade, nome)

    def excluir(self, cidade_id) -> None:
        cidade = self.repository.get_by_id(cidade_id)

        if not cidade:
            raise CidadeNaoEncontradaError(
                f"Nao existe cidade com id '{cidade_id}'."
            )

        self.repository.delete(cidade)


class HotelService:
    def __init__(self, db: Session):
        self.repository = HotelRepository(db)
        self.cidades = CidadeRepository(db)

    def criar(
        self,
        nome: str,
        cidade_id,
        estrelas: int = 3,
    ) -> Hotel:
        nome = nome.strip()

        if not self.cidades.get_by_id(cidade_id):
            raise CidadeNaoEncontradaError(
                f"Nao existe cidade com id '{cidade_id}'."
            )

        return self.repository.create(
            nome=nome,
            cidade_id=cidade_id,
            estrelas=estrelas,
        )

    def listar(self, cidade_id=None) -> list[Hotel]:
        if cidade_id is not None:
            if not self.cidades.get_by_id(cidade_id):
                raise CidadeNaoEncontradaError(
                    f"Nao existe cidade com id '{cidade_id}'."
                )

            return self.repository.list_by_cidade(cidade_id)

        return self.repository.list()

    def atualizar(
        self,
        hotel_id,
        nome: str,
        cidade_id,
        estrelas: int,
    ) -> Hotel:
        hotel = self.repository.get_by_id(hotel_id)

        if not hotel:
            raise HotelNaoEncontradoError(
                f"Nao existe hotel com id '{hotel_id}'."
            )

        if not self.cidades.get_by_id(cidade_id):
            raise CidadeNaoEncontradaError(
                f"Nao existe cidade com id '{cidade_id}'."
            )

        return self.repository.update(
            hotel=hotel,
            nome=nome.strip(),
            cidade_id=cidade_id,
            estrelas=estrelas,
        )

    def excluir(self, hotel_id) -> None:
        hotel = self.repository.get_by_id(hotel_id)

        if not hotel:
            raise HotelNaoEncontradoError(
                f"Nao existe hotel com id '{hotel_id}'."
            )

        self.repository.delete(hotel)


class ComodidadeService:
    def __init__(self, db: Session):
        self.repository = ComodidadeRepository(db)

    def criar(self, nome: str) -> Comodidade:
        nome = nome.strip()

        if self.repository.get_by_nome(nome):
            raise ComodidadeJaExisteError(
                f"Ja existe uma comodidade chamada '{nome}'."
            )

        return self.repository.create(nome)

    def listar(self) -> list[Comodidade]:
        return self.repository.list()

    def atualizar(self, comodidade_id, nome: str) -> Comodidade:
        comodidade = self.repository.get_by_id(comodidade_id)

        if not comodidade:
            raise ComodidadeNaoEncontradaError(
                f"Nao existe comodidade com id '{comodidade_id}'."
            )

        nome = nome.strip()

        outra = self.repository.get_by_nome(nome)
        if outra and outra.id != comodidade.id:
            raise ComodidadeJaExisteError(
                f"Ja existe uma comodidade chamada '{nome}'."
            )

        return self.repository.update(comodidade, nome)

    def excluir(self, comodidade_id) -> None:
        comodidade = self.repository.get_by_id(comodidade_id)

        if not comodidade:
            raise ComodidadeNaoEncontradaError(
                f"Nao existe comodidade com id '{comodidade_id}'."
            )

        self.repository.delete(comodidade)