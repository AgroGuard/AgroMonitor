"""
conftest.py — Fixtures globais do AgroMonitor
Coloque em: agromonitor/Backend/conftest.py
"""
import bcrypt
import uuid
import pytest
from django.test import Client
from Cadastro.models import Usuario, UsuarioToken, UsuarioConvite


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_senha_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def make_email_hash(email: str) -> str:
    return bcrypt.hashpw(email.encode(), bcrypt.gensalt()).decode()


# ---------------------------------------------------------------------------
# Fixtures de usuários
# ---------------------------------------------------------------------------

@pytest.fixture
def senha_padrao():
    return "Senha@123"


@pytest.fixture
def usuario_owner(db, senha_padrao):
    """Usuário com role=owner (cliente principal)."""
    return Usuario.objects.create(
        usuario="fazendeiro1",
        email="fazendeiro@agromonitor.com",
        email_hash=make_email_hash("fazendeiro@agromonitor.com"),
        senha_hash=make_senha_hash(senha_padrao),
        role="owner",
    )


@pytest.fixture
def usuario_supervisor(db, senha_padrao, usuario_owner):
    """Usuário supervisor criado pelo owner."""
    return Usuario.objects.create(
        usuario="supervisor1",
        email="supervisor@agromonitor.com",
        email_hash=make_email_hash("supervisor@agromonitor.com"),
        senha_hash=make_senha_hash(senha_padrao),
        role="supervisor",
        criado_por=usuario_owner,
    )


@pytest.fixture
def usuario_employee(db, senha_padrao, usuario_owner):
    """Usuário employee criado pelo owner."""
    return Usuario.objects.create(
        usuario="employee1",
        email="employee@agromonitor.com",
        email_hash=make_email_hash("employee@agromonitor.com"),
        senha_hash=make_senha_hash(senha_padrao),
        role="employee",
        criado_por=usuario_owner,
    )


@pytest.fixture
def usuario_admin(db, senha_padrao):
    """Usuário com role=admin."""
    return Usuario.objects.create(
        usuario="admin1",
        email="admin@agromonitor.com",
        email_hash=make_email_hash("admin@agromonitor.com"),
        senha_hash=make_senha_hash(senha_padrao),
        role="admin",
    )


@pytest.fixture
def usuario_super_admin(db, senha_padrao):
    """Usuário com role=super_admin."""
    return Usuario.objects.create(
        usuario="superadmin1",
        email="superadmin@agromonitor.com",
        email_hash=make_email_hash("superadmin@agromonitor.com"),
        senha_hash=make_senha_hash(senha_padrao),
        role="super_admin",
    )


@pytest.fixture
def token_owner(db, usuario_owner):
    """Token de autenticação para o owner."""
    return UsuarioToken.objects.create(usuario=usuario_owner)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def client_owner(client, token_owner):
    """Client HTTP com header Authorization do owner."""
    client.defaults["HTTP_AUTHORIZATION"] = f"Token {token_owner.key}"
    return client


@pytest.fixture
def client_supervisor(client, db, usuario_supervisor):
    token = UsuarioToken.objects.create(usuario=usuario_supervisor)
    client.defaults["HTTP_AUTHORIZATION"] = f"Token {token.key}"
    return client


@pytest.fixture
def client_employee(client, db, usuario_employee):
    token = UsuarioToken.objects.create(usuario=usuario_employee)
    client.defaults["HTTP_AUTHORIZATION"] = f"Token {token.key}"
    return client
