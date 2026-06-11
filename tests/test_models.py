import pytest
import bcrypt
import uuid
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from datetime import timedelta
from Cadastro.models import Usuario, UsuarioToken, UsuarioConvite, RecuperacaoSenha, Tenant


def make_hash(valor: str) -> str:
    return bcrypt.hashpw(valor.encode(), bcrypt.gensalt()).decode()



class TestUsuarioModel:

    def test_criar_usuario_owner(self, db):
        u = Usuario.objects.create(
            usuario="joao",
            email="joao@fazenda.com",
            email_hash=make_hash("joao@fazenda.com"),
            senha_hash=make_hash("senha123"),
            role="owner",
        )
        assert u.pk is not None
        assert u.role == "owner"
        assert u.bloqueio is False
        assert u.tentativas_falhas == 0

    def test_str_usuario(self, db):
        u = Usuario.objects.create(
            usuario="maria",
            email="maria@fazenda.com",
            email_hash=make_hash("maria@fazenda.com"),
            senha_hash=make_hash("senha123"),
        )
        assert str(u) == "maria"

    def test_is_authenticated_sempre_true(self, usuario_owner):
        assert usuario_owner.is_authenticated is True

    def test_is_anonymous_sempre_false(self, usuario_owner):
        assert usuario_owner.is_anonymous is False

    def test_usuario_com_criado_por(self, usuario_owner, usuario_supervisor):
        assert usuario_supervisor.criado_por == usuario_owner

    def test_nao_permite_deletar_super_admin(self, usuario_super_admin):
        with pytest.raises(PermissionDenied):
            usuario_super_admin.delete()

    def test_permite_deletar_usuario_comum(self, usuario_owner):
        pk = usuario_owner.pk
        usuario_owner.delete()
        assert not Usuario.objects.filter(pk=pk).exists()

    def test_roles_validas(self, db):
        roles = ["super_admin", "admin", "owner", "supervisor", "employee"]
        for i, role in enumerate(roles):
            u = Usuario.objects.create(
                usuario=f"user_{i}",
                email=f"user_{i}@teste.com",
                email_hash=make_hash(f"user_{i}@teste.com"),
                senha_hash=make_hash("senha"),
                role=role,
            )
            assert u.role == role

    def test_email_unico(self, db, usuario_owner):
        with pytest.raises(Exception):
            Usuario.objects.create(
                usuario="outro",
                email=usuario_owner.email,  # já existe
                email_hash=make_hash("outro@teste.com"),
                senha_hash=make_hash("senha"),
            )

    def test_usuario_unico(self, db, usuario_owner):
        with pytest.raises(Exception):
            Usuario.objects.create(
                usuario=usuario_owner.usuario,  # já existe
                email="novo@teste.com",
                email_hash=make_hash("novo@teste.com"),
                senha_hash=make_hash("senha"),
            )



class TestUsuarioTokenModel:

    def test_criar_token(self, db, usuario_owner):
        token = UsuarioToken.objects.create(usuario=usuario_owner)
        assert token.pk is not None
        assert token.key is not None

    def test_str_token(self, db, usuario_owner):
        token = UsuarioToken.objects.create(usuario=usuario_owner)
        assert usuario_owner.usuario in str(token)

    def test_token_deletado_ao_deletar_usuario(self, db, usuario_owner):
        token = UsuarioToken.objects.create(usuario=usuario_owner)
        token_key = token.key
        usuario_owner.delete()
        assert not UsuarioToken.objects.filter(key=token_key).exists()

    def test_key_unica_por_padrao(self, db, usuario_owner):
        t1 = UsuarioToken.objects.create(usuario=usuario_owner)
        UsuarioToken.objects.filter(pk=t1.pk).delete()
        t2 = UsuarioToken.objects.create(usuario=usuario_owner)
        assert t1.key != t2.key



class TestUsuarioConviteModel:

    def test_criar_convite(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="novofuncionario",
            email="novo@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        assert convite.pk is not None
        assert convite.utilizado is False
        assert convite.expira_em is not None

    def test_convite_expira_em_30_dias(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="novofunc",
            email="novofunc@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        delta = convite.expira_em - convite.criado_em
        assert 29 <= delta.days <= 30

    def test_convite_valido_recem_criado(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="funcvalido",
            email="funcvalido@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        assert convite.is_valido() is True

    def test_convite_invalido_quando_utilizado(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="funcutil",
            email="funcutil@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        convite.utilizado = True
        convite.save()
        assert convite.is_valido() is False

    def test_convite_invalido_quando_expirado(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="funcexp",
            email="funcexp@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        convite.expira_em = timezone.now() - timedelta(days=1)
        convite.save()
        assert convite.is_valido() is False

    def test_str_convite(self, db, usuario_owner):
        convite = UsuarioConvite.objects.create(
            usuario="funcstr",
            email="funcstr@fazenda.com",
            role="employee",
            criado_por=usuario_owner,
        )
        assert "funcstr" in str(convite)



class TestRecuperacaoSenhaModel:

    def test_criar_recuperacao(self, db, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        assert rec.pk is not None
        assert rec.utilizado is False
        assert rec.expira_em is not None

    def test_expira_em_1_hora(self, db, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        delta = rec.expira_em - rec.criado_em
        # entre 59 e 61 minutos (margem de segurança)
        assert 3540 <= delta.seconds <= 3660

    def test_token_valido_recem_criado(self, db, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        assert rec.is_valido() is True

    def test_token_invalido_quando_utilizado(self, db, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        rec.marcar_como_utilizado()
        assert rec.is_valido() is False

    def test_marcar_como_utilizado_salva_data(self, db, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        rec.marcar_como_utilizado()
        rec.refresh_from_db()
        assert rec.utilizado is True
        assert rec.data_utilizacao is not None

    def test_token_invalido_quando_expirado(self, db, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        rec.expira_em = timezone.now() - timedelta(hours=2)
        rec.save()
        assert rec.is_valido() is False

    def test_str_recuperacao(self, db, usuario_owner):
        rec = RecuperacaoSenha.objects.create(
            usuario=usuario_owner,
            email=usuario_owner.email,
        )
        assert usuario_owner.usuario in str(rec)


class TestTenantModel:

    def test_criar_tenant(self, db, usuario_owner):
        tenant = Tenant.objects.create(
            nome="Fazenda Boa Vista",
            slug="fazenda-boa-vista",
            owner=usuario_owner,
            db_name="fazenda_boa_vista_db",
        )
        assert tenant.pk is not None
        assert tenant.ativo is True
        assert tenant.provisionado is False

    def test_str_tenant(self, db, usuario_owner):
        tenant = Tenant.objects.create(
            nome="Fazenda Teste",
            slug="fazenda-teste",
            owner=usuario_owner,
            db_name="fazenda_teste_db",
        )
        assert "Fazenda Teste" in str(tenant)
        assert "fazenda-teste" in str(tenant)

    def test_get_connection_info(self, db, usuario_owner):
        tenant = Tenant.objects.create(
            nome="Fazenda Conn",
            slug="fazenda-conn",
            owner=usuario_owner,
            db_name="fazenda_conn_db",
            db_user="fazenda_user",
            db_host="localhost",
            db_port="5432",
        )
        info = tenant.get_connection_info()
        assert info["NAME"] == "fazenda_conn_db"
        assert info["USER"] == "fazenda_user"
        assert info["ENGINE"] == "django.db.backends.postgresql"

    def test_slug_unico(self, db, usuario_owner):
        Tenant.objects.create(
            nome="Tenant A",
            slug="slug-unico",
            owner=usuario_owner,
            db_name="db_a",
        )
        with pytest.raises(Exception):
            Tenant.objects.create(
                nome="Tenant B",
                slug="slug-unico",  # duplicado
                owner=usuario_owner,
                db_name="db_b",
            )
