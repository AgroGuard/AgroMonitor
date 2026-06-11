"""
tests/test_login.py — Testes de Login e Logout
Coloque em: agromonitor/Backend/tests/test_login.py
"""
import json
import pytest
import bcrypt
from django.test import Client
from django.urls import reverse
from Cadastro.models import Usuario, UsuarioToken


def post_json(client, url, data):
    return client.post(
        url,
        data=json.dumps(data),
        content_type="application/json",
    )


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLoginApi:

    def test_login_com_email_correto(self, client, usuario_owner, senha_padrao):
        resp = post_json(client, "/Cadastro/login/", {
            "email": usuario_owner.email,
            "password": senha_padrao,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["role"] == "owner"
        assert data["usuario"] == usuario_owner.usuario

    def test_login_com_nome_usuario_correto(self, client, usuario_owner, senha_padrao):
        resp = post_json(client, "/Cadastro/login/", {
            "usuario": usuario_owner.usuario,
            "password": senha_padrao,
        })
        assert resp.status_code == 200
        assert "token" in resp.json()

    def test_login_senha_errada_retorna_401(self, client, usuario_owner):
        resp = post_json(client, "/Cadastro/login/", {
            "email": usuario_owner.email,
            "password": "senha_errada_xpto",
        })
        assert resp.status_code == 401

    def test_login_usuario_inexistente_retorna_401(self, client, db):
        resp = post_json(client, "/Cadastro/login/", {
            "email": "naoexiste@fazenda.com",
            "password": "qualquer",
        })
        assert resp.status_code == 401

    def test_login_sem_campos_retorna_400(self, client, db):
        resp = post_json(client, "/Cadastro/login/", {})
        assert resp.status_code == 400

    def test_login_metodo_get_retorna_405(self, client, db):
        resp = client.get("/Cadastro/login/")
        assert resp.status_code == 405

    def test_login_conta_bloqueada_retorna_403(self, client, usuario_owner, senha_padrao):
        usuario_owner.bloqueio = True
        usuario_owner.save()
        resp = post_json(client, "/Cadastro/login/", {
            "email": usuario_owner.email,
            "password": senha_padrao,
        })
        assert resp.status_code == 403

    def test_login_incrementa_tentativas_falhas(self, client, usuario_owner):
        tentativas_antes = usuario_owner.tentativas_falhas
        post_json(client, "/Cadastro/login/", {
            "email": usuario_owner.email,
            "password": "senha_errada",
        })
        usuario_owner.refresh_from_db()
        assert usuario_owner.tentativas_falhas == tentativas_antes + 1

    def test_login_bem_sucedido_zera_tentativas_falhas(self, client, usuario_owner, senha_padrao):
        usuario_owner.tentativas_falhas = 3
        usuario_owner.save()
        post_json(client, "/Cadastro/login/", {
            "email": usuario_owner.email,
            "password": senha_padrao,
        })
        usuario_owner.refresh_from_db()
        assert usuario_owner.tentativas_falhas == 0

    def test_login_bem_sucedido_atualiza_ultimo_login(self, client, usuario_owner, senha_padrao):
        assert usuario_owner.ultimo_login is None
        post_json(client, "/Cadastro/login/", {
            "email": usuario_owner.email,
            "password": senha_padrao,
        })
        usuario_owner.refresh_from_db()
        assert usuario_owner.ultimo_login is not None

    def test_login_cria_token_no_banco(self, client, usuario_owner, senha_padrao):
        resp = post_json(client, "/Cadastro/login/", {
            "email": usuario_owner.email,
            "password": senha_padrao,
        })
        token_key = resp.json()["token"]
        assert UsuarioToken.objects.filter(key=token_key).exists()

    def test_login_super_admin_retorna_role_admin(self, client, usuario_super_admin, senha_padrao):
        """super_admin deve aparecer como 'admin' para o frontend."""
        resp = post_json(client, "/Cadastro/login/", {
            "email": usuario_super_admin.email,
            "password": senha_padrao,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "admin"
        assert data["is_super_admin"] is True

    def test_login_5_tentativas_falhas_bloqueia_conta(self, client, usuario_owner):
        for _ in range(5):
            post_json(client, "/Cadastro/login/", {
                "email": usuario_owner.email,
                "password": "senha_errada",
            })
        usuario_owner.refresh_from_db()
        assert usuario_owner.bloqueio is True


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

class TestLogoutApi:

    def test_logout_com_token_valido(self, client_owner, token_owner):
        resp = client_owner.post("/Cadastro/logout/")
        assert resp.status_code == 200
        assert not UsuarioToken.objects.filter(key=token_owner.key).exists()

    def test_logout_sem_autenticacao_retorna_401(self, client):
        resp = client.post("/Cadastro/logout/")
        assert resp.status_code == 401

    def test_logout_metodo_get_retorna_405(self, client_owner):
        resp = client_owner.get("/Cadastro/logout/")
        assert resp.status_code == 405
