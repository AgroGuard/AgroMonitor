"""
tests/test_views.py — Testes de Perfil, Convites, Cadastro e Estufas
Coloque em: agromonitor/Backend/tests/test_views.py
"""
import json
import pytest
from unittest.mock import patch
from django.test import Client
from Cadastro.models import Usuario, UsuarioConvite, UsuarioToken


def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type="application/json")


# ---------------------------------------------------------------------------
# Perfil
# ---------------------------------------------------------------------------

class TestPerfilApi:

    def test_get_perfil_autenticado(self, client_owner, usuario_owner):
        resp = client_owner.get("/Cadastro/perfil/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["usuario"] == usuario_owner.usuario
        assert data["email"] == usuario_owner.email
        assert "role" in data

    def test_get_perfil_sem_auth_retorna_401(self, client):
        resp = client.get("/Cadastro/perfil/")
        assert resp.status_code == 401

    def test_patch_perfil_atualiza_nome(self, client_owner, usuario_owner):
        resp = client_owner.patch(
            "/Cadastro/perfil/",
            data=json.dumps({"nome": "fazendeiro_novo"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        usuario_owner.refresh_from_db()
        assert usuario_owner.usuario == "fazendeiro_novo"

    def test_patch_perfil_nome_duplicado_retorna_409(self, client_owner, usuario_supervisor):
        resp = client_owner.patch(
            "/Cadastro/perfil/",
            data=json.dumps({"nome": usuario_supervisor.usuario}),
            content_type="application/json",
        )
        assert resp.status_code == 409

    def test_patch_perfil_email_duplicado_retorna_409(self, client_owner, usuario_supervisor):
        resp = client_owner.patch(
            "/Cadastro/perfil/",
            data=json.dumps({"email": usuario_supervisor.email}),
            content_type="application/json",
        )
        assert resp.status_code == 409

    def test_patch_perfil_sem_campos_retorna_400(self, client_owner):
        resp = client_owner.patch(
            "/Cadastro/perfil/",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_delete_perfil_owner(self, client_owner, usuario_owner):
        pk = usuario_owner.pk
        resp = client_owner.delete("/Cadastro/perfil/")
        assert resp.status_code == 200
        assert not Usuario.objects.filter(pk=pk).exists()

    def test_delete_perfil_super_admin_retorna_403(self, client, usuario_super_admin, db):
        token = UsuarioToken.objects.create(usuario=usuario_super_admin)
        client.defaults["HTTP_AUTHORIZATION"] = f"Token {token.key}"
        resp = client.delete("/Cadastro/perfil/")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Convidar usuário
# ---------------------------------------------------------------------------

class TestConvidarUsuarioApi:

    @patch("Cadastro.views.send_mail")
    def test_owner_convida_employee(self, mock_mail, client_owner, usuario_owner):
        mock_mail.return_value = 1
        resp = post_json(client_owner, "/Cadastro/convidar/", {
            "usuario": "novoemp",
            "email": "novoemp@fazenda.com",
            "role": "employee",
        })
        assert resp.status_code == 201
        assert UsuarioConvite.objects.filter(usuario="novoemp").exists()

    @patch("Cadastro.views.send_mail")
    def test_owner_convida_supervisor(self, mock_mail, client_owner):
        mock_mail.return_value = 1
        resp = post_json(client_owner, "/Cadastro/convidar/", {
            "usuario": "novosuper",
            "email": "novosuper@fazenda.com",
            "role": "supervisor",
        })
        assert resp.status_code == 201

    def test_owner_nao_pode_convidar_owner(self, client_owner):
        resp = post_json(client_owner, "/Cadastro/convidar/", {
            "usuario": "novoowner",
            "email": "novoowner@fazenda.com",
            "role": "owner",
        })
        assert resp.status_code == 400

    def test_convidar_sem_autenticacao_retorna_401(self, client, db):
        resp = post_json(client, "/Cadastro/convidar/", {
            "usuario": "qualquer",
            "email": "qualquer@fazenda.com",
            "role": "employee",
        })
        assert resp.status_code == 401

    def test_convidar_campos_faltando_retorna_400(self, client_owner):
        resp = post_json(client_owner, "/Cadastro/convidar/", {
            "usuario": "incompleto",
        })
        assert resp.status_code == 400

    @patch("Cadastro.views.send_mail")
    def test_convidar_usuario_ja_existente_retorna_409(self, mock_mail, client_owner, usuario_supervisor):
        mock_mail.return_value = 1
        resp = post_json(client_owner, "/Cadastro/convidar/", {
            "usuario": usuario_supervisor.usuario,  # já existe
            "email": "outro@fazenda.com",
            "role": "employee",
        })
        assert resp.status_code == 409

    def test_employee_nao_pode_convidar_retorna_403(self, client_employee):
        resp = post_json(client_employee, "/Cadastro/convidar/", {
            "usuario": "novousr",
            "email": "novousr@fazenda.com",
            "role": "employee",
        })
        assert resp.status_code == 403

    def test_usuario_com_menos_de_3_chars_retorna_400(self, client_owner):
        resp = post_json(client_owner, "/Cadastro/convidar/", {
            "usuario": "ab",
            "email": "ab@fazenda.com",
            "role": "employee",
        })
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Completar cadastro
# ---------------------------------------------------------------------------

class TestCompletarCadastroApi:

    def test_completar_cadastro_valido(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="novocadastro",
            email="novocadastro@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        client = Client()
        resp = post_json(client, "/Cadastro/completar-cadastro/", {
            "token": str(convite.token),
            "senha": "Senha@123",
            "confirma_senha": "Senha@123",
        })
        assert resp.status_code == 201
        assert Usuario.objects.filter(usuario="novocadastro").exists()

    def test_completar_cadastro_token_invalido_retorna_404(self, db):
        client = Client()
        resp = post_json(client, "/Cadastro/completar-cadastro/", {
            "token": "token-inexistente",
            "senha": "Senha@123",
            "confirma_senha": "Senha@123",
        })
        assert resp.status_code == 404

    def test_completar_cadastro_senhas_diferentes_retorna_400(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="cadastroerro",
            email="cadastroerro@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        client = Client()
        resp = post_json(client, "/Cadastro/completar-cadastro/", {
            "token": str(convite.token),
            "senha": "Senha@123",
            "confirma_senha": "OutraSenha@123",
        })
        assert resp.status_code == 400

    def test_completar_cadastro_senha_curta_retorna_400(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="cadastrocurto",
            email="cadastrocurto@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        client = Client()
        resp = post_json(client, "/Cadastro/completar-cadastro/", {
            "token": str(convite.token),
            "senha": "123",
            "confirma_senha": "123",
        })
        assert resp.status_code == 400

    def test_completar_cadastro_marca_convite_utilizado(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="cadastromark",
            email="cadastromark@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        client = Client()
        post_json(client, "/Cadastro/completar-cadastro/", {
            "token": str(convite.token),
            "senha": "Senha@123",
            "confirma_senha": "Senha@123",
        })
        convite.refresh_from_db()
        assert convite.utilizado is True

    def test_completar_cadastro_campos_faltando_retorna_400(self, db):
        client = Client()
        resp = post_json(client, "/Cadastro/completar-cadastro/", {})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Estufas
# ---------------------------------------------------------------------------

class TestEstufasApi:

    def test_listar_estufas_owner_sem_estufas(self, client_owner):
        resp = client_owner.get("/Cadastro/estufas/")
        assert resp.status_code == 200
        assert resp.json()["estufas"] == []

    def test_criar_estufa_owner(self, client_owner):
        resp = post_json(client_owner, "/Cadastro/estufas/", {
            "nome": "Estufa Norte",
            "descricao": "Estufa de tomates",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["estufa"]["nome"] == "Estufa Norte"

    def test_criar_estufa_sem_nome_retorna_400(self, client_owner):
        resp = post_json(client_owner, "/Cadastro/estufas/", {
            "descricao": "Sem nome",
        })
        assert resp.status_code == 400

    def test_supervisor_nao_pode_criar_estufa(self, client_supervisor):
        resp = post_json(client_supervisor, "/Cadastro/estufas/", {
            "nome": "Estufa Supervisor",
        })
        assert resp.status_code == 403

    def test_listar_estufas_sem_auth_retorna_401(self, client):
        resp = client.get("/Cadastro/estufas/")
        assert resp.status_code == 401
