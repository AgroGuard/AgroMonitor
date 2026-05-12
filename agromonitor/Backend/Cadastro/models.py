import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Usuario(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('owner', 'Owner - Cliente'),
        ('supervisor', 'Supervisor'),
        ('employee', 'Employee'),
    ]

    # Nome de usuário
    usuario = models.CharField(max_length=15, unique=True)

    # Senha criptografada
    senha_hash = models.CharField(max_length=255)

    # Email pesquisável
    email = models.EmailField(unique=True, null=True, blank=True)

    # Email criptografado
    email_hash = models.CharField(max_length=255, unique=True)

    # Função/Role no sistema
    role = models.CharField('Função', max_length=20, choices=ROLE_CHOICES, default='owner')

    # Controle de tentativas
    tentativas_falhas = models.IntegerField(default=0)

    # Bloqueio da conta
    bloqueio = models.BooleanField(default=False)

    # Data de criação e último login
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    ultimo_login = models.DateTimeField('Último login', null=True, blank=True)

    def __str__(self):
        return self.usuario


class UsuarioConvite(models.Model):
    """Modelo para armazenar convites de cadastro via email"""
    usuario = models.CharField(max_length=15, unique=True)
    email = models.EmailField()
    role = models.CharField('Função', max_length=20, choices=Usuario.ROLE_CHOICES, default='employee')
    token = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='convites_criados')
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    utilizado = models.BooleanField(default=False)
    usuario_criado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='convite_origem')

    def __str__(self):
        return f'Convite para {self.usuario} ({self.email})'

    def save(self, *args, **kwargs):
        """Define a data de expiração como 7 dias após criação"""
        if not self.pk:
            self.expira_em = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def is_valido(self):
        """Verifica se o convite ainda é válido"""
        return not self.utilizado and timezone.now() < self.expira_em


class Tenant(models.Model):
    """Cliente / banco de dados do cliente registrado no sistema principal."""
    nome = models.CharField('Nome do cliente', max_length=150)
    slug = models.SlugField('Slug do cliente', max_length=150, unique=True)
    owner = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tenants'
    )
    db_name = models.CharField('Nome do banco', max_length=150, unique=True)
    db_user = models.CharField('Usuário do banco', max_length=100, default='postgres')
    db_password = models.CharField('Senha do banco', max_length=255, blank=True)
    db_host = models.CharField('Host do banco', max_length=100, default='localhost')
    db_port = models.CharField('Porta do banco', max_length=10, default='5432')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    provisionado = models.BooleanField('Provisionado', default=False)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'

    def __str__(self):
        return f'{self.nome} ({self.slug})'

    def get_connection_info(self):
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': self.db_name,
            'USER': self.db_user,
            'PASSWORD': self.db_password,
            'HOST': self.db_host,
            'PORT': self.db_port,
        }
