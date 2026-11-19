from app.repositories.tutorial_repository import TutorialRepository


def test_create_professor_in_repository(db_session):
    repo = TutorialRepository(db_session)
    prof = repo.create_professor(
        nome="Professor de Teste",
        email="teste@unicatolica.edu.br",
        sala="Sala Teste, Bloco T",
        biografia="Uma biografia de teste.",
    )

    assert prof.id is not None, "O professor criado deveria possuir um ID."
    assert prof.nome == "Professor de Teste", "O nome do professor deveria corresponder ao informado."
    assert prof.email == "teste@unicatolica.edu.br", "O e-mail do professor deveria corresponder ao informado."
    assert prof.detalhe is not None, "Os detalhes do professor deveriam ter sido criados."
    assert prof.detalhe.sala == "Sala Teste, Bloco T", "A sala do professor deveria corresponder à informada."
    assert prof.detalhe.biografia == "Uma biografia de teste.", "A biografia do professor deveria corresponder à informada."


def test_get_professor_by_id_in_repository(db_session):
    repo = TutorialRepository(db_session)
    created_prof = repo.create_professor(
        nome="Outro Prof",
        email="outro@unicatolica.edu.br",
        sala="Sala B",
    )

    fetched_prof = repo.get_professor_by_id(created_prof.id)
    assert fetched_prof is not None, "O repositório deveria retornar o professor existente."
    assert fetched_prof.id == created_prof.id, "O ID do professor retornado deveria corresponder ao ID consultado."
    assert fetched_prof.nome == "Outro Prof", "O nome do professor retornado deveria corresponder ao cadastrado."