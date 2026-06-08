import uuid
import webbrowser

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from Cadastro.models import Usuario, UsuarioConvite


class Command(BaseCommand):
    help = 'Gera um convite/token de teste e abre a URL de conclusão no navegador.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            required=True,
            help='Nome de usuário do convite (campo usuario do convite).'
        )
        parser.add_argument(
            '--email',
            required=True,
            help='Email do convite.'
        )
        parser.add_argument(
            '--role',
            required=False,
            default='employee',
            choices=[choice[0] for choice in Usuario.ROLE_CHOICES],
            help='Função/role do novo usuário convidado.'
        )
        parser.add_argument(
            '--creator',
            required=False,
            help='Nome de usuário que cria o convite. Se omitido, usa primeiro super_admin/admin/owner disponível.'
        )
        parser.add_argument(
            '--open',
            action='store_true',
            help='Abre a URL de completar cadastro no navegador padrão após criar o convite.'
        )

    def handle(self, *args, **options):
        username = options['username'].strip()
        email = options['email'].strip()
        role = options['role']
        creator_username = options['creator']
        open_browser = options['open']

        if len(username) < 3 or len(username) > 15:
            raise CommandError('Usuário deve ter entre 3 e 15 caracteres.')

        if Usuario.objects.filter(usuario=username).exists():
            raise CommandError(f'Já existe um usuário com o nome de usuário {username}.')

        if Usuario.objects.filter(email=email).exists():
            raise CommandError(f'Já existe um usuário com o email {email}.')

        if creator_username:
            creator = Usuario.objects.filter(usuario=creator_username).first()
            if not creator:
                raise CommandError(f'Criador não encontrado: {creator_username}.')
        else:
            creator = Usuario.objects.filter(role__in=['super_admin', 'admin', 'owner']).order_by('role').first()
            if not creator:
                raise CommandError(
                    'Nenhum usuário criador disponível. Crie um usuário super_admin/admin/owner ou use --creator para especificar um nome de usuário existente.'
                )

        if creator.role == 'owner' and role not in ['supervisor', 'employee']:
            raise CommandError('Usuários owner podem convidar apenas supervisor ou employee.')
        if creator.role in ['super_admin', 'admin'] and role != 'owner':
            raise CommandError('Usuários admin/super_admin podem convidar apenas owner.')
        if creator.role not in ['owner', 'admin', 'super_admin']:
            raise CommandError('O criador deve ter role owner, admin ou super_admin.')

        convite = UsuarioConvite.objects.create(
            usuario=username,
            email=email,
            role=role,
            criado_por=creator
        )

        link_cadastro = f'{settings.FRONTEND_URL}/completar-cadastro/{convite.token}'

        self.stdout.write(self.style.SUCCESS('Convite de teste criado com sucesso.'))
        self.stdout.write(f'Usuário do convite: {convite.usuario}')
        self.stdout.write(f'Email do convite: {convite.email}')
        self.stdout.write(f'Role do convite: {convite.role}')
        self.stdout.write(f'Token: {convite.token}')
        self.stdout.write(f'URL de conclusão: {link_cadastro}')

        if open_browser:
            try:
                webbrowser.open_new_tab(link_cadastro)
                self.stdout.write(self.style.SUCCESS('Abrindo a URL no navegador padrão...'))
            except Exception as exc:
                raise CommandError(f'Não foi possível abrir o navegador: {exc}')
