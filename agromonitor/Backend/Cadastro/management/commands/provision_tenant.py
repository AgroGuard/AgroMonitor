import bcrypt
from django.conf import settings
from django.core.management import call_command
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
        parser.add_argument('--owner-id', required=False, help='ID do owner existente no sistema principal')
        parser.add_argument('--owner-usuario', required=False, help='Username do owner a ser criado no sistema principal')
        parser.add_argument('--owner-email', required=False, help='Email do owner')
        parser.add_argument('--owner-password', required=False, help='Senha do owner')
        parser.add_argument('--db-name', required=False, help='Nome do banco Postgres a ser criado')
        parser.add_argument('--db-user', required=False, help='Usuário do banco que terá acesso ao tenant database')
        parser.add_argument('--db-password', required=False, help='Senha do usuário do banco')
        parser.add_argument('--db-host', required=False, default=settings.POSTGRES_ADMIN['HOST'], help='Host do servidor Postgres')
        parser.add_argument('--db-port', required=False, default=settings.POSTGRES_ADMIN['PORT'], help='Porta do servidor Postgres')
        parser.add_argument('--run-migrations', action='store_true', help='Executa as migrations no tenant database após sua criação')

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

        owner_id = options.get('owner_id')
        owner = None

        if owner_id:
            owner = Usuario.objects.filter(pk=owner_id).first()
            if not owner:
                raise CommandError(f'Owner com id {owner_id} não encontrado.')
            if owner.role != 'owner':
                raise CommandError('O usuário informado em --owner-id não é um owner.')
            owner_usuario = owner.usuario
            owner_email = owner.email
            owner_password = options.get('owner_password') or 'tenant-provisioning'
        else:
            if not options.get('owner_usuario') or not options.get('owner_email') or not options.get('owner_password'):
                raise CommandError('owner-usuario, owner-email e owner-password são obrigatórios quando --owner-id não for informado.')
            owner_usuario = options['owner_usuario'].strip()
            owner_email = options['owner_email'].strip()
            owner_password = options['owner_password']
        db_name = options['db_name'] or slug.replace('-', '_')
        db_user = options['db_user'] or admin_config['USER']
        db_password = options['db_password'] or admin_config['PASSWORD']
        db_host = options['db_host']
        db_port = options['db_port']
        run_migrations = options['run_migrations']
        db_alias = f'tenant_{slug.replace("-", "_")}'

        if owner_id:
            if Usuario.objects.filter(usuario=owner_usuario).exists() and Usuario.objects.filter(usuario=owner_usuario).first().pk != owner.id:
                raise CommandError(f'Já existe um usuário com o nome de usuário {owner_usuario}.')
            if owner_email and Usuario.objects.filter(email=owner_email).exists() and Usuario.objects.filter(email=owner_email).first().pk != owner.id:
                raise CommandError(f'Já existe um usuário com o email {owner_email}.')
        else:
            if Usuario.objects.filter(usuario=owner_usuario).exists():
                raise CommandError(f'Já existe um usuário com o nome de usuário {owner_usuario}.')
            if Usuario.objects.filter(email=owner_email).exists():
                raise CommandError(f'Já existe um usuário com o email {owner_email}.')
        if Tenant.objects.filter(owner=owner).exists():
            raise CommandError(f'Já existe um tenant provisionado para o owner {owner_usuario}.')
        if Tenant.objects.filter(slug=slug).exists():
            raise CommandError(f'Já existe um tenant com slug {slug}.')
        if Tenant.objects.filter(db_name=db_name).exists():
            raise CommandError(f'Já existe um tenant com nome de banco {db_name}.')
        if db_user != admin_config['USER'] and not options['db_password']:
            raise CommandError('Senha do usuário do banco é obrigatória quando db_user não é o usuário admin.')

        self.stdout.write('Conectando ao servidor Postgres para provisionar o tenant...')
        self._create_database(admin_config, db_name, db_user, db_password)

        if not owner:
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

        if run_migrations:
            settings.DATABASES[db_alias] = tenant.get_connection_info()
            self.stdout.write(f'Executando migrações no banco do tenant ({db_alias})...')
            try:
                call_command('migrate', database=db_alias, interactive=False, verbosity=options.get('verbosity', 1))
            except Exception as exc:
                tenant.provisionado = False
                tenant.save(update_fields=['provisionado'])
                raise CommandError(f'Erro ao executar as migrations no tenant: {exc}')
            finally:
                from django.db import connections
                connections[db_alias].close()

        tenant.provisionado = True
        tenant.save(update_fields=['provisionado'])

        self.stdout.write(self.style.SUCCESS(f'Tenant "{tenant_name}" provisionado com sucesso.'))
        self.stdout.write(self.style.SUCCESS(f'Database criado: {db_name}'))
        self.stdout.write(self.style.SUCCESS(f'Owner criado: {owner_usuario}'))
        if run_migrations:
            self.stdout.write(self.style.SUCCESS('Migrations executadas no tenant.'))

    def _create_database(self, admin_config, db_name, db_user, db_password):
        conn = psycopg2.connect(
            dbname=admin_config['NAME'],
            user=admin_config['USER'],
            password=admin_config['PASSWORD'],
            host=admin_config['HOST'],
            port=admin_config['PORT'],
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        self._ensure_db_user(cur, db_user, db_password, admin_config['USER'])

        cur.execute(sql.SQL('SELECT 1 FROM pg_database WHERE datname = %s'), [db_name])
        if cur.fetchone():
            cur.close()
            conn.close()
            raise CommandError(f'Banco de dados {db_name} já existe no servidor.')

        cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(db_name)))
        cur.execute(
            sql.SQL('GRANT ALL PRIVILEGES ON DATABASE {} TO {}').format(
                sql.Identifier(db_name),
                sql.Identifier(db_user)
            )
        )
        cur.close()
        conn.close()

    def _ensure_db_user(self, cur, db_user, db_password, admin_user):
        if db_user == admin_user:
            return

        cur.execute(sql.SQL('SELECT 1 FROM pg_roles WHERE rolname = %s'), [db_user])
        if cur.fetchone():
            cur.execute(
                sql.SQL('ALTER ROLE {} WITH LOGIN PASSWORD %s').format(sql.Identifier(db_user)),
                [db_password]
            )
        else:
            cur.execute(
                sql.SQL('CREATE ROLE {} WITH LOGIN PASSWORD %s').format(sql.Identifier(db_user)),
                [db_password]
            )
