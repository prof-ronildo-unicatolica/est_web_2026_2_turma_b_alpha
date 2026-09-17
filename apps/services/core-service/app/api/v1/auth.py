from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user
from app.core.database import get_db
from app.schemas.usuario import LoginRequest, Token, UsuarioCreate, UsuarioPublic
from app.services.auth_service import (
    AuthService,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UsuarioPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UsuarioCreate, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        return service.registrar(
            nome=payload.nome,
            email=payload.email,
            senha=payload.senha,
        )
    except EmailJaCadastradoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)

    try:
        usuario = service.autenticar(
            email=payload.email,
            senha=payload.senha,
        )
    except CredenciaisInvalidasError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    token = service.gerar_token(usuario)

    return Token(access_token=token)


@router.get("/me", response_model=UsuarioPublic)
def get_me(usuario_atual: dict = Depends(get_current_user)):
    """Rota protegida: retorna o perfil do usuario autenticado."""
    return usuario_atual


@router.get("/admin/verificacao")
def somente_admin(admin: dict = Depends(get_current_admin)):
    """Rota administrativa de exemplo (autorizacao por is_admin)."""
    return {"mensagem": f"Acesso administrativo concedido para {admin['nome']}"}
