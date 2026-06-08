import bcrypt
import json
from django.test import TestCase, override_settings
from django.core.exceptions import PermissionDenied

from BD_FAZENDA.models import Estufa
from .models import Usuario, UsuarioToken, RecuperacaoSenha


class UsuarioModelTests(TestCase):
    def test_super_admin_cannot_be_deleted(self):
        usuario = Usuario.objects.create(
            usuario='superuser',
            senha_hash='hash',
            email='super@example.com',
            email_hash='ehash',
            role='super_admin'
        )

        with self.assertRaises(PermissionDenied):
            usuario.delete()


class AuthTests(TestCase):
    def setUp(self):
        salt = bcrypt.gensalt()
        senha = 'senha123'
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
        email_hash = bcrypt.hashpw('user@example.com'.encode('utf-8'), salt).decode('utf-8')

        self.usuario = Usuario.objects.create(
            usuario='user1',
            senha_hash=senha_hash,
            email='user@example.com',
            email_hash=email_hash,
            role='owner'
        )
        supervisor_email_hash = bcrypt.hashpw('supervisor@example.com'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.supervisor = Usuario.objects.create(
            usuario='supervisor1',
            senha_hash=senha_hash,
            email='supervisor@example.com',
            email_hash=supervisor_email_hash,
            role='supervisor',
            criado_por=self.usuario
        )
        Estufa.objects.create(nome='Estufa Teste', descricao='Testando', owner=self.usuario)
        self.senha = senha

    def test_login_returns_token(self):
        response = self.client.post(
            '/api/login/',
            data=json.dumps({'email': self.usuario.email, 'password': self.senha}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('token', data)
        self.assertTrue(UsuarioToken.objects.filter(usuario=self.usuario, key=data['token']).exists())

    def test_protected_endpoint_accepts_token(self):
        response = self.client.post(
            '/api/login/',
            data=json.dumps({'email': self.usuario.email, 'password': self.senha}),
            content_type='application/json'
        )
        token = response.json().get('token')

        protected = self.client.get(
            '/api/estufas/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(protected.status_code, 200)
        data = protected.json()
        self.assertIn('estufas', data)

    def test_estufa_creation_assigns_owner_and_filters_by_owner(self):
        response = self.client.post(
            '/api/login/',
            data=json.dumps({'email': self.usuario.email, 'password': self.senha}),
            content_type='application/json'
        )
        token = response.json().get('token')

        create_response = self.client.post(
            '/api/estufas/',
            data=json.dumps({'nome': 'Nova Estufa', 'descricao': 'Criada pelo owner'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(create_response.status_code, 201)
        data = create_response.json()
        self.assertEqual(data['estufa']['nome'], 'Nova Estufa')

        list_response = self.client.get(
            '/api/estufas/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(list_response.status_code, 200)
        list_data = list_response.json()
        self.assertTrue(any(e['nome'] == 'Nova Estufa' for e in list_data['estufas']))

    def test_supervisor_can_see_owner_estufas_but_not_create(self):
        login_response = self.client.post(
            '/api/login/',
            data=json.dumps({'email': self.supervisor.email, 'password': self.senha}),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json().get('token')

        list_response = self.client.get(
            '/api/estufas/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(list_response.status_code, 200)
        data = list_response.json()
        self.assertIn('estufas', data)
        self.assertTrue(any(e['nome'] == 'Estufa Teste' for e in data['estufas']))

        create_response = self.client.post(
            '/api/estufas/',
            data=json.dumps({'nome': 'Tentativa Supervisor', 'descricao': 'Não deve criar'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(create_response.json().get('error'), 'Apenas owners podem cadastrar estufas.')

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_recovery_flow(self):
        # Solicitar recuperação
        response = self.client.post(
            '/api/recuperar/solicitar/',
            data=json.dumps({'email': self.usuario.email}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('message', data)

        recuperacao = RecuperacaoSenha.objects.filter(usuario=self.usuario, utilizado=False).first()
        self.assertIsNotNone(recuperacao)

        # Validar token
        response = self.client.get(f'/api/recuperar/validar/?token={recuperacao.token}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('valid'))

        # Confirmar recuperação
        nova_senha = 'novaSenha123'
        response = self.client.post(
            '/api/recuperar/confirmar/',
            data=json.dumps({
                'token': recuperacao.token,
                'nova_senha': nova_senha,
                'confirma_senha': nova_senha
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('message'), 'Senha alterada com sucesso!')

        recuperacao.refresh_from_db()
        self.assertTrue(recuperacao.utilizado)

        # Login com a nova senha
        login_response = self.client.post(
            '/api/login/',
            data=json.dumps({'email': self.usuario.email, 'password': nova_senha}),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('token', login_response.json())
