from datetime import timedelta

import jwt
import pytest

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_nao_e_igual_a_senha_original():
    senha = "minhaSenha123"
    hashed = hash_password(senha)
    assert hashed != senha


def test_hash_password_gera_hashes_diferentes_para_mesma_senha():
    senha = "minhaSenha123"
    assert hash_password(senha) != hash_password(senha)


def test_verify_password_com_senha_correta_retorna_true():
    senha = "minhaSenha123"
    hashed = hash_password(senha)
    assert verify_password(senha, hashed) is True


def test_verify_password_com_senha_incorreta_retorna_false():
    hashed = hash_password("minhaSenha123")
    assert verify_password("senhaErrada", hashed) is False


def test_create_access_token_contem_sub_e_exp():
    token = create_access_token(subject="usuario@teste.com")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["sub"] == "usuario@teste.com"
    assert "exp" in payload


def test_create_access_token_aceita_claims_extras():
    token = create_access_token(subject="admin@teste.com", extra_claims={"role": "admin"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["role"] == "admin"


def test_decode_access_token_com_token_valido_retorna_payload():
    token = create_access_token(subject="usuario@teste.com")
    payload = decode_access_token(token)
    assert payload["sub"] == "usuario@teste.com"


def test_decode_access_token_com_token_invalido_levanta_excecao():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("token-completamente-invalido")


def test_decode_access_token_com_token_expirado_levanta_excecao():
    token = create_access_token(subject="usuario@teste.com", expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)
        