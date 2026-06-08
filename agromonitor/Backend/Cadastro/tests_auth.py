import pytest
import json
import bcrypt
from django.test import Client
from Cadastro.models import Usuario, UsuarioToken
from Cadastro.views import login_api

pytestmark = pytest.mark.django_db


class TestAuthentication:
    """Testes para autenticação"""

    def test_login_sucesso(self, client, owner_user):
        """Testa login bem-sucedido"""
        response = client.post(
            '/api/cadastro/login/',
            data=json.dumps({
                'email': 'owner_test@test.com',
                'password': 'testowner123'
            }),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.json()
        assert 'token' in data
        assert data['usuario'] == 'owner_test'

    def test_login_senha_errada(self, client, owner_user):
        """Testa login com senha incorreta"""
        response = client.post(
            '/api/cadastro/login/',
            data=json.dumps({
                'email': 'owner_test@test.com',
                'password': 'senhaerrada'
            }),
            content_type='application/json'
        )
        assert response.status_code == 401

    def test_login_usuario_nao_existe(self, client):
        """Testa login de usuário inexistente"""
        response = client.post(
            '/api/cadastro/login/',
            data=json.dumps({
                'email': 'naoexiste@test.com',
                'password': 'qualquerssenha'
            }),
            content_type='application/json'
        )
        assert response.status_code == 401

    def test_logout(self, autenticado_owner, owner_user):
        """Testa logout"""
        response = autenticado_owner.post('/api/cadastro/logout/')
        assert response.status_code == 200
        data = response.json()
        assert 'Logout realizado' in data.get('message', '')

    def test_perfil_usuario_autenticado(self, autenticado_owner, owner_user):
        """Testa obtenção de perfil do usuário autenticado"""
        response = autenticado_owner.get('/api/cadastro/perfil/')
        assert response.status_code == 200
        data = response.json()
        assert data['usuario'] == 'owner_test'
        assert data['email'] == 'owner_test@test.com'
        assert data['role'] == 'owner'

    def test_perfil_nao_autenticado(self, client):
        """Testa acesso a perfil sem autenticação"""
        response = client.get('/api/cadastro/perfil/')
        assert response.status_code == 401

    def test_bloqueio_superadmin_delete(self, autenticado_admin, admin_user):
        """Testa que super admin não pode deletar sua conta"""
        response = autenticado_admin.delete('/api/cadastro/perfil/')
        assert response.status_code == 403
        assert 'super-admin' in response.json().get('error', '').lower()
        # Verificar que usuário continua no BD
        assert Usuario.objects.filter(id=admin_user.id).exists()


class TestCadastroUsuario:
    """Testes para cadastro de usuários"""

    def test_criar_usuario_como_owner(self, autenticado_owner, owner_user, db):
        """Testa criação de usuário por owner"""
        response = autenticado_owner.post(
            '/api/cadastro/convidar/',
            data=json.dumps({
                'usuario': 'novousuario',
                'email': 'novo@test.com',
                'role': 'employee'
            }),
            content_type='application/json'
        )
        # Status pode ser 201 ou 200 dependendo da implementação
        assert response.status_code in [200, 201]
        # Verificar que convite foi criado
        from Cadastro.models import UsuarioConvite
        assert UsuarioConvite.objects.filter(usuario='novousuario').exists()

    def test_token_autenticacao(self, owner_user):
        """Testa geração e uso de token"""
        token = UsuarioToken.objects.create(usuario=owner_user)
        assert token.key is not None
        assert token.usuario == owner_user
        # Verificar que token foi criado
        assert UsuarioToken.objects.filter(usuario=owner_user).exists()
