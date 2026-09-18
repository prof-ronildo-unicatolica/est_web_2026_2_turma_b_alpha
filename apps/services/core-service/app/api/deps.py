"""Dependencias de autenticacao e autorizacao."""

import uuid

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.repositories.usuario_repository import UsuarioRepository


bearer_scheme = HTTPBearer(
    description="Use o token JWT retornado por POST /auth/login",
    auto_error=False,
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """Valida o JWT e retorna o usuario autenticado consultado no PostgreSQL."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso ausente",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")

        if not subject:
            raise ValueError("JWT sem identificador de usuario")

        usuario_id = uuid.UUID(subject)

    except (jwt.InvalidTokenError, ValueError, TypeError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    usuario = UsuarioRepository(db).get_by_id(usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "email": usuario.email,
        "nome": usuario.nome,
        "is_admin": usuario.is_admin,
    }


def get_current_admin(usuario: dict = Depends(get_current_user)) -> dict:
    """Verifica se o usuario autenticado possui permissao administrativa."""

    if not usuario["is_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )

    return usuario