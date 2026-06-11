"""
tests/test_recuperacao_senha.py — Testes de Recuperação de Senha
Coloque em: agromonitor/Backend/tests/test_recuperacao_senha.py
"""
import json
import pytest
from unittest.mock import patch
from django.test import Client
from django.utils import timezone
from datetime import timedelta
from Cadastro.models import RecuperacaoSenha


def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type="application/json")


class TestSolicitarRecuperacaoSenha:

    @patch("Cadastro.views.send_mail")
    def test_solicitar_com_email_existente(self, mock_mail, client, usuario_owner):
        mock_mail.return_value = 1
        resp = post_json(client, "/Cadastro/recuperar/solicitar/", {
            "email": usuario_owner.email,
        })
        assert resp.status_code == 200
        assert RecuperacaoSenha.objects.filter(usuario=usuario_owner).exists()

    def test_solicitar_email_inexistente_retorna_200(self, client, db):
        """Não deve revelar se o email existe (segurança)."""
        resp = post_json(client, "/Cadastro/recuperar/solicitar/", {
            "email": "naoexiste@fazenda.com",
        })
        assert resp.status_code == 200
        assert "receberá" in resp.json()["message"]

    def test_solicitar_sem_email_retorna_400(self, client, db):
        resp = post_json(client, "/Cadastro/recuperar/solicitar/", {})
        assert resp.status_code == 400

    def test_solicitar_conta_bloqueada_retorna_403(self, client, usuario_owner):
        usuario_owner.bloqueio = True
        usuario_owner.save()
        resp = post_json(client, "/Cadastro/recuperar/solicitar/", {
            "email": usuario_owner.email,
        })
        assert resp.status_code == 403

    @patch("Cadastro.views.send_mail")
    def test_solicitar_limpa_tokens_antigos(self, mock_mail, client, usuario_owner):
        mock_mail.return_value = 1
        # Cria token antigo
        RecuperacaoSenha.objects.create(usuario=usuario_owner, email=usuario_owner.email)
        count_antes = RecuperacaoSenha.objects.filter(usuario=usuario_owner).count()
        assert count_antes == 1

        # Solicita novamente
        post_json(client, "/Cadastro/recuperar/solicitar/", {
            "email": usuario_owner.email,
        })
        # O antigo deve ter sido deletado e um novo criado
        assert RecuperacaoSenha.objects.filter(usuario=usuario_owner).count() == 1

    @patch("Cadastro.views.send_mail")
    def test_solicitar_por_nome_usuario(self, mock_mail, client, usuario_owner):
        mock_mail.return_value = 1
        resp = post_json(client, "/Cadastro/recuperar/solicitar/", {
            "usuario": usuario_owner.usuario,
        })
        assert resp.status_code == 200


class TestValidarTokenRecuperacao:

    def test_validar_token_valido(self, client, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        resp = client.get(f"/Cadastro/recuperar/validar/?token={rec.token}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert data["usuario"] == usuario_owner.usuario

    def test_validar_token_inexistente_retorna_404(self, client, db):
        resp = client.get("/Cadastro/recuperar/validar/?token=token-invalido-xyz")
        assert resp.status_code == 404

    def test_validar_token_expirado_retorna_410(self, client, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        rec.expira_em = timezone.now() - timedelta(hours=2)
        rec.save()
        resp = client.get(f"/Cadastro/recuperar/validar/?token={rec.token}")
        assert resp.status_code == 410

    def test_validar_sem_token_retorna_400(self, client, db):
        resp = client.get("/Cadastro/recuperar/validar/")
        assert resp.status_code == 400


class TestConfirmarRecuperacaoSenha:

    def test_confirmar_com_token_valido(self, client, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        resp = post_json(client, "/Cadastro/recuperar/confirmar/", {
            "token": str(rec.token),
            "nova_senha": "NovaSenha@123",
            "confirma_senha": "NovaSenha@123",
        })
        assert resp.status_code == 200
        assert resp.json()["usuario"] == usuario_owner.usuario

    def test_confirmar_troca_senha_no_banco(self, client, usuario_owner):
        import bcrypt
        senha_hash_antes = usuario_owner.senha_hash
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        post_json(client, "/Cadastro/recuperar/confirmar/", {
            "token": str(rec.token),
            "nova_senha": "NovaSenha@456",
            "confirma_senha": "NovaSenha@456",
        })
        usuario_owner.refresh_from_db()
        assert usuario_owner.senha_hash != senha_hash_antes
        assert bcrypt.checkpw("NovaSenha@456".encode(), usuario_owner.senha_hash.encode())

    def test_confirmar_marca_token_como_utilizado(self, client, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        post_json(client, "/Cadastro/recuperar/confirmar/", {
            "token": str(rec.token),
            "nova_senha": "NovaSenha@789",
            "confirma_senha": "NovaSenha@789",
        })
        rec.refresh_from_db()
        assert rec.utilizado is True

    def test_confirmar_desbloqueia_conta(self, client, usuario_owner):
        usuario_owner.bloqueio = True
        usuario_owner.save()
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        post_json(client, "/Cadastro/recuperar/confirmar/", {
            "token": str(rec.token),
            "nova_senha": "NovaSenha@999",
            "confirma_senha": "NovaSenha@999",
        })
        usuario_owner.refresh_from_db()
        assert usuario_owner.bloqueio is False

    def test_confirmar_senhas_diferentes_retorna_400(self, client, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        resp = post_json(client, "/Cadastro/recuperar/confirmar/", {
            "token": str(rec.token),
            "nova_senha": "Senha@123",
            "confirma_senha": "Senha@456",
        })
        assert resp.status_code == 400

    def test_confirmar_senha_curta_retorna_400(self, client, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        resp = post_json(client, "/Cadastro/recuperar/confirmar/", {
            "token": str(rec.token),
            "nova_senha": "123",
            "confirma_senha": "123",
        })
        assert resp.status_code == 400

    def test_confirmar_token_expirado_retorna_410(self, client, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        rec.expira_em = timezone.now() - timedelta(hours=2)
        rec.save()
        resp = post_json(client, "/Cadastro/recuperar/confirmar/", {
            "token": str(rec.token),
            "nova_senha": "NovaSenha@123",
            "confirma_senha": "NovaSenha@123",
        })
        assert resp.status_code == 410

    def test_confirmar_token_inexistente_retorna_404(self, client, db):
        resp = post_json(client, "/Cadastro/recuperar/confirmar/", {
            "token": "token-que-nao-existe",
            "nova_senha": "NovaSenha@123",
            "confirma_senha": "NovaSenha@123",
        })
        assert resp.status_code == 404

    def test_confirmar_campos_faltando_retorna_400(self, client, db):
        resp = post_json(client, "/Cadastro/recuperar/confirmar/", {})
        assert resp.status_code == 400
