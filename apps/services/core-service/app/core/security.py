import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

# SECRET_KEY vem de variavel de ambiente. O valor abaixo e so um fallback
# para nao quebrar em ambiente local sem .env configurado -- o valor real
# NUNCA deve ser versionado no Git (issue S2-02, criterio de aceite).
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-CHANGE-ME-IN-PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Contexto do passlib configurado so com bcrypt. "deprecated=auto" permite
# trocar de algoritmo no futuro sem quebrar hashes ja existentes no banco.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Gera o hash bcrypt de uma senha em texto plano.

    O resultado NUNCA e igual a senha original (bcrypt inclui salt
    aleatorio), entao duas chamadas com a mesma senha geram hashes
    diferentes -- isso e esperado, nao um bug.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Confere se a senha em texto plano corresponde ao hash armazenado."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Cria um JWT assinado contendo, no minimo, 'sub' (o dono do token) e
    'exp' (quando ele expira). extra_claims permite acrescentar coisas como
    o papel do usuario (role), sem essa funcao precisar saber o que e um
    Usuario -- essa camada nao conhece banco nem regra de negocio.
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode: dict[str, Any] = {"sub": subject, "exp": expire, "iat": now}
    if extra_claims:
        to_encode.update(extra_claims)

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodifica e valida um JWT (assinatura + expiracao).

    Deixa as excecoes do PyJWT subirem (ExpiredSignatureError,
    InvalidTokenError) em vez de esconde-las: quem chama esta funcao (o
    guard, na issue S2-03) e quem decide traduzir isso para um 401 HTTP --
    essa camada nao conhece FastAPI.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
