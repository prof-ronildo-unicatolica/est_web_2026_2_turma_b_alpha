from sqlalchemy.orm import Session

from app.models.hotel import Cidade


class CidadeRepository:
    """Acesso ao banco para a entidade Cidade. Sem regra de negocio aqui."""

    def __init__(self, db: Session):
        # A sessao vem de fora (injecao de dependencia). O repository nao a
        # cria nem a fecha -- quem faz isso e o get_db() do FastAPI. Isso e o
        # que permite trocar por uma sessao de teste sem alterar esta classe.
        self.db = db

    def create(self, nome: str) -> Cidade:
        cidade = Cidade(nome=nome)
        self.db.add(cidade)
        self.db.commit()
        # refresh() recarrega o objeto do banco. Sem isso, 'cidade.id' vem
        # None: o UUID e gerado no INSERT, e o objeto em memoria ainda nao
        # sabe disso. E o id e justamente o que a resposta precisa devolver.
        self.db.refresh(cidade)
        return cidade

    def list(self) -> list[Cidade]:
        return self.db.query(Cidade).order_by(Cidade.nome).all()

    def get_by_id(self, cidade_id) -> Cidade | None:
        """Devolve None quando nao existe -- nao lanca excecao.

        Quem decide se 'nao encontrado' e um 404, um erro de validacao ou algo
        ignoravel e a camada de service. O repository so relata o fato.
        """
        return self.db.query(Cidade).filter(Cidade.id == cidade_id).first()

    def get_by_nome(self, nome: str) -> Cidade | None:
        return self.db.query(Cidade).filter(Cidade.nome == nome).first()