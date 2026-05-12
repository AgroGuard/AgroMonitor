from django.core.management.base import BaseCommand
from django.utils import timezone
from Cadastro.models import Usuario
from Monitor.models import EstatisticaPlataforma


class Command(BaseCommand):
    help = 'Atualiza as estatísticas diárias da plataforma'

    def handle(self, *args, **options):
        hoje = timezone.now().date()

        self.stdout.write(f'Atualizando estatísticas para {hoje}...')

        # Verificar se já existe estatística para hoje
        if EstatisticaPlataforma.objects.filter(data=hoje).exists():
            self.stdout.write(self.style.WARNING('Estatísticas já existem para hoje'))
            return

        # Calcular estatísticas
        total_usuarios = Usuario.objects.count()
        total_owners = Usuario.objects.filter(role='owner').count()
        total_supervisores = Usuario.objects.filter(role='supervisor').count()
        total_funcionarios = Usuario.objects.filter(role='employee').count()

        # Usuários ativos hoje
        usuarios_ativos = Usuario.objects.filter(ultimo_login__date=hoje).count()

        # Novos usuários hoje
        novos_usuarios = Usuario.objects.filter(criado_em__date=hoje).count()

        # Criar registro de estatística
        estatistica = EstatisticaPlataforma.objects.create(
            data=hoje,
            total_usuarios=total_usuarios,
            total_owners=total_owners,
            total_supervisores=total_supervisores,
            total_funcionarios=total_funcionarios,
            total_estufas=0,  # Implementar quando houver modelo
            total_relatorios=0,  # Implementar quando houver modelo
            usuarios_ativos_hoje=usuarios_ativos,
            novos_usuarios_hoje=novos_usuarios,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Estatísticas atualizadas: {total_usuarios} usuários, '
                f'{total_owners} owners, {usuarios_ativos} ativos'
            )
        )