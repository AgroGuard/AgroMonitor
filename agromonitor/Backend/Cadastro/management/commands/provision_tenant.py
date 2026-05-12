import bcrypt
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    psycopg2 = None

from Cadastro.models import Usuario, Tenant


class Command(BaseCommand):
    help = 'Provisions a new tenant database and registers the tenant in the main system.'

    def add_arguments(self, parser):
        parser.add_argument('--tenant-name', required=True, help='Nome do cliente/tenant')
        parser.add_argument('--slug', required=False, help='Slug único do tenant. Se omitido, será gerado do nome.')
        parser.add_argument('--owner-usuario', required=True, help='Username do owner a ser criado no sistema principal')
        parser.add_argument('--owner-email', required=True, help='Email do owner')
        parser.add_argument('--owner-password', required=True, help='Senha do owner')
        parser.add_argument('--db-name', required=False, help='Nome do banco Postgres a ser criado')
        parser.add_argument('--db-user', required=False, help='Usuário do banco que terá acesso ao tenant database')
        parser.add_argument('--db-password', required=False, help='Senha do usuário do banco')
        parser.add_argument('--db-host', required=False, default=settings.POSTGRES_ADMIN['HOST'], help='Host do servidor Postgres')
        parser.add_argument('--db-port', required=False, default=settings.POSTGRES_ADMIN['PORT'], help='Porta do servidor Postgres')

    def handle(self, *args, **options):
        if psycopg2 is None:
            raise CommandError('psycopg2 não está instalado. Instale-o antes de usar este comando.')

        admin_config = getattr(settings, 'POSTGRES_ADMIN', None)
        if not admin_config:
            raise CommandError('POSTGRES_ADMIN não configurado em settings.py')

        tenant_name = options['tenant_name'].strip()
        slug = options['slug'] or slugify(tenant_name)
        if not slug:
            raise CommandError('Não foi possível gerar um slug válido para o tenant.')

        owner_usuario = options['owner_usuario'].strip()
        owner_email = options['owner_email'].strip()
        owner_password = options['owner_password']
        db_name = options['db_name'] or slug.replace('-', '_')
        db_user = options['db_user'] or admin_config['USER']
        db_password = options['db_password'] or admin_config['PASSWORD']
        db_host = options['db_host']
        db_port = options['db_port']

        if Usuario.objects.filter(usuario=owner_usuario).exists():
            raise CommandError(f'Já existe um usuário com o nome de usuário {owner_usuario}.')
        if Usuario.objects.filter(email=owner_email).exists():
            raise CommandError(f'Já existe um usuário com o email {owner_email}.')
        if Tenant.objects.filter(slug=slug).exists():
            raise CommandError(f'Já existe um tenant com slug {slug}.')
        if Tenant.objects.filter(db_name=db_name).exists():
            raise CommandError(f'Já existe um tenant com nome de banco {db_name}.')

        # Cria usuário owner no sistema principal
        salt = bcrypt.gensalt()
        senha_hash = bcrypt.hashpw(owner_password.encode('utf-8'), salt).decode('utf-8')
        email_hash = bcrypt.hashpw(owner_email.encode('utf-8'), salt).decode('utf-8')

        owner = Usuario.objects.create(
            usuario=owner_usuario,
            senha_hash=senha_hash,
            email=owner_email,
            email_hash=email_hash,
            role='owner'
        )

        tenant = Tenant.objects.create(
            nome=tenant_name,
            slug=slug,
            owner=owner,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password,
            db_host=db_host,
            db_port=db_port,
            provisionado=False,
            ativo=True,
        )

        # Cria o banco de dados no servidor Postgres
        self.stdout.write('Conectando ao servidor Postgres para criar o banco...')
        self._create_database(admin_config, db_name)
        tenant.provisionado = True
        tenant.save()

        self.stdout.write(self.style.SUCCESS(f'Tenant "{tenant_name}" provisionado com sucesso.'))
        self.stdout.write(self.style.SUCCESS(f'Database criado: {db_name}'))
        self.stdout.write(self.style.SUCCESS(f'Owner criado: {owner_usuario}'))

    def _create_database(self, admin_config, db_name):
        conn = psycopg2.connect(
            dbname=admin_config['NAME'],
            user=admin_config['USER'],
            password=admin_config['PASSWORD'],
            host=admin_config['HOST'],
            port=admin_config['PORT'],
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute(sql.SQL('SELECT 1 FROM pg_database WHERE datname = %s'), [db_name])
        if cur.fetchone():
            cur.close()
            conn.close()
            raise CommandError(f'Banco de dados {db_name} já existe no servidor.')

        cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))
        cur.close()
        conn.close()