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
    assert hashed != senha, (
        f"Falha de segurança: o hash gerado ({hashed}) não deve ser idêntico à senha em texto plano original."
    )


def test_hash_password_gera_hashes_diferentes_para_mesma_senha():
    senha = "minhaSenha123"
    assert hash_password(senha) != hash_password(senha)


def test_verify_password_com_senha_correta_retorna_true():
    senha = "minhaSenha123"
    hashed = hash_password(senha)
    assert verify_password(senha, hashed) is True, (
        f"Falha na validação de credenciais válidas: a função verify_password deveria retornar True "
        f"ao comparar a senha correta com o hash correspondente."
    )


def test_verify_password_com_senha_incorreta_retorna_false():
    hashed = hash_password("minhaSenha123")
    assert verify_password("senhaErrada", hashed) is False, (
        "Falha na verificação de segurança: a função verify_password aceitou incorretamente "
        "uma senha divergente ('senhaErrada') como válida para o hash armazenado."
    )


def test_create_access_token_contem_sub_e_exp():
    token = create_access_token(subject="usuario@teste.com")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["sub"] == "usuario@teste.com", (
        f"Falha no payload do token JWT: o subject ('sub') esperado era 'usuario@teste.com', "
        f"mas o payload decodificado retornou '{payload.get('sub')}'."
    )
    assert "exp" in payload, (
        "Falha na especificação do token JWT: a claim obrigatória de expiração ('exp') "
        "não foi encontrada no payload gerado."
    )


def test_create_access_token_aceita_claims_extras():
    token = create_access_token(subject="admin@teste.com", extra_claims={"role": "admin"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload.get("role") == "admin", (
        f"Falha na inclusão de claims personalizadas: a claim extra 'role' com valor 'admin' "
        f"não foi mapeada corretamente no payload decodificado (retornou: {payload.get('role')})."
    )


def test_decode_access_token_com_token_valido_retorna_payload():
    token = create_access_token(subject="usuario@teste.com")
    payload = decode_access_token(token)
    assert payload["sub"] == "usuario@teste.com", (
        f"Falha na decodificação do token válido: o campo 'sub' obtido pelo decode_access_token "
        f"(' {payload.get('sub')}') difere do esperado ('usuario@teste.com')."
    )


def test_decode_access_token_com_token_invalido_levanta_excecao():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("token-completamente-invalido")


def test_decode_access_token_com_token_expirado_levanta_excecao():
    token = create_access_token(subject="usuario@teste.com", expires_delta=timedelta(seconds=-1))
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)
        