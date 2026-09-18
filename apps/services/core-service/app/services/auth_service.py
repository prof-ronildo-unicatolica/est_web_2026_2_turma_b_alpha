from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository


class AuthError(Exception):
    """Base para erros de negocio relacionados a autenticacao."""


class EmailJaCadastradoError(AuthError):
    pass


class CredenciaisInvalidasError(AuthError):
    pass


class AuthService:
    def __init__(self, db: Session):
        self.repository = UsuarioRepository(db)

    def registrar(self, nome: str, email: str, senha: str) -> Usuario:
        nome = nome.strip()
        email = email.strip().lower()

        if self.repository.get_by_email(email):
            raise EmailJaCadastradoError(
                f"O e-mail '{email}' ja esta cadastrado."
            )

        senha_hash = hash_password(senha)

        return self.repository.create(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            is_admin=False,
        )

    def autenticar(self, email: str, senha: str) -> Usuario:
        email = email.strip().lower()
        usuario = self.repository.get_by_email(email)

        if usuario is None or not verify_password(senha, usuario.senha_hash):
            raise CredenciaisInvalidasError("E-mail ou senha incorretos.")

        return usuario

    def gerar_token(self, usuario: Usuario) -> str:
        return create_access_token(subject=str(usuario.id))