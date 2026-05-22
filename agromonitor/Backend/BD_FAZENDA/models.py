from datetime import timedelta
import uuid
from django.db import models
from django.utils import timezone

class Estufa(models.Model):
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True, null=True)

    def __str__(self):
        return self.nome

class Usuario(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Dono da fazenda'),
        ('supervisor', 'Supervisor'),
        ('employee', 'Funcionário'),
    ]

    nome = models.CharField('Nome', max_length=150)
    email = models.EmailField('Email', unique=True)
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    role = models.CharField('Função', max_length=20, choices=ROLE_CHOICES, default='employee')
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    # Quem criou este usuário (sempre um owner)
    criado_por = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_criados')

    def __str__(self):
        return self.nome

    def pode_criar_usuarios(self):
        """Verifica se este usuário pode criar outros usuários"""
        return self.role == 'owner' and self.ativo

    def pode_criar_role(self, role):
        """Verifica se este usuário pode criar usuários com determinado role"""
        if not self.pode_criar_usuarios():
            return False

        # Owner pode criar supervisor e employee
        if self.role == 'owner':
            return role in ['supervisor', 'employee']

        return False


class UsuarioConvite(models.Model):
    """Modelo para armazenar convites de cadastro via email no banco do cliente"""
    nome = models.CharField('Nome completo', max_length=150)
    usuario = models.CharField('Nome de usuário', max_length=15, unique=True)
    email = models.EmailField('Email')
    role = models.CharField('Função pretendida', max_length=20, choices=Usuario.ROLE_CHOICES)
    token = models.CharField('Token', max_length=255, unique=True, default=uuid.uuid4)
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='convites_criados')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    expira_em = models.DateTimeField('Expira em')
    utilizado = models.BooleanField('Utilizado', default=False)
    usuario_criado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='convite_origem')

    def __str__(self):
        return f'Convite para {self.usuario} ({self.email}) - {self.role}'

    def save(self, *args, **kwargs):
        """Define a expiração como 30 minutos após criação"""
        if not self.pk:
            self.expira_em = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)

    def is_valido(self):
        """Verifica se o convite ainda é válido"""
        return not self.utilizado and timezone.now() < self.expira_em


class RelatorioSensor(models.Model):
    estufa = models.ForeignKey(Estufa, on_delete=models.CASCADE, related_name='relatorios')
    arquivo_csv = models.FileField('Relatório CSV', upload_to='relatorios/')
    data_ultimo_relatorio = models.DateTimeField('Data do último relatório')
    data_relatorio_mais_antigo = models.DateTimeField('Data do relatório mais antigo')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    def __str__(self):
        return f'Relatório {self.estufa.nome} - último {self.data_ultimo_relatorio.date()}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Limpa relatórios com + de 2 anos da estufa
        limite = timezone.now() - timedelta(days=365 * 2)
        relatorios_antigos = self.estufa.relatorios.filter(
            data_relatorio_mais_antigo__lt=limite
        ).exclude(pk=self.pk)
        relatorios_antigos.delete()