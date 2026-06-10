

import os
import pytest
from django.test import Client

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BD_FAZENDA.settings')

# Don't call django.setup() here - pytest-django handles it
from Cadastro.models import Usuario
@pytest.fixture
def db():
    """Fixture para database (pytest-django)"""
    pass


@pytest.fixture
def client():
    """Fixture para cliente HTTP de testes"""
    return Client()


@pytest.fixture
def admin_user(db):
    """Cria usuário admin para testes"""
    import bcrypt
    senha_hash = bcrypt.hashpw(b'testadmin123', bcrypt.gensalt(12)).decode('utf-8')
    usuario = Usuario.objects.create(
        usuario='admin_test',
        email='admin_test@test.com',
        email_hash='admin_test@test.com_hash',
        senha_hash=senha_hash,
        role='super_admin',
        bloqueio=False,
    )
    return usuario


@pytest.fixture
def owner_user(db):
    """Cria usuário owner para testes"""
    import bcrypt
    senha_hash = bcrypt.hashpw(b'testowner123', bcrypt.gensalt(12)).decode('utf-8')
    usuario = Usuario.objects.create(
        usuario='owner_test',
        email='owner_test@test.com',
        email_hash='owner_test@test.com_hash',
        senha_hash=senha_hash,
        role='owner',
        bloqueio=False,
    )
    return usuario


@pytest.fixture
def supervisor_user(db, owner_user):
    """Cria usuário supervisor para testes"""
    import bcrypt
    senha_hash = bcrypt.hashpw(b'testsuper123', bcrypt.gensalt(12)).decode('utf-8')
    usuario = Usuario.objects.create(
        usuario='supervisor_test',
        email='supervisor_test@test.com',
        email_hash='supervisor_test@test.com_hash',
        senha_hash=senha_hash,
        role='supervisor',
        criado_por=owner_user,
        bloqueio=False,
    )
    return usuario


@pytest.fixture
def autenticado_admin(client, admin_user):
    """Cliente HTTP autenticado como admin"""
    from Cadastro.models import UsuarioToken
    token = UsuarioToken.objects.create(usuario=admin_user)
    client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
    return client


@pytest.fixture
def autenticado_owner(client, owner_user):
    """Cliente HTTP autenticado como owner"""
    from Cadastro.models import UsuarioToken
    token = UsuarioToken.objects.create(usuario=owner_user)
    client.defaults['HTTP_AUTHORIZATION'] = f'Token {token.key}'
    return client
