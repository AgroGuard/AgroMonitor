import uuid
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import PermissionDenied
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

    # Foto de perfil
    foto = models.FileField(upload_to='profile_photos/', null=True, blank=True)

    # Função/Role no sistema
    role = models.CharField('Função', max_length=20, choices=ROLE_CHOICES, default='owner')

    # Owner que criou este usuário (aplicável para supervisor/employee)
    criado_por = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_criados',
        verbose_name='Criado por'
    )

    # Controle de tentativas
    tentativas_falhas = models.IntegerField(default=0)

    # Bloqueio da conta
    bloqueio = models.BooleanField(default=False)

    # Data de criação e último login
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    ultimo_login = models.DateTimeField('Último login', null=True, blank=True)

    def __str__(self):
        return self.usuario

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def delete(self, *args, **kwargs):
        if self.role == 'super_admin':
            raise PermissionDenied('Exclusão de super admin não permitida.')
        super().delete(*args, **kwargs)


@receiver(pre_delete, sender=Usuario)
def prevent_super_admin_delete(sender, instance, **kwargs):
    if instance.role == 'super_admin':
        raise PermissionDenied('Exclusão de super admin não permitida.')


class UsuarioToken(models.Model):
    """Modelo para armazenar tokens de autenticação de usuários."""
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    key = models.CharField('Chave do token', max_length=64, unique=True, default=uuid.uuid4)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Token de Usuário'
        verbose_name_plural = 'Tokens de Usuários'

    def __str__(self):
        return f'{self.usuario.usuario} - {self.key}'


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
        """Define a data de expiração como 30 dias após criação"""
        if not self.pk:
            self.expira_em = timezone.now() + timedelta(days=30)
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
    mqtt_broker = models.CharField('Broker MQTT', max_length=150, blank=True, default='')
    mqtt_port = models.PositiveIntegerField('Porta MQTT', default=1883)
    mqtt_topic_prefix = models.CharField('Prefixo de tópicos MQTT', max_length=100, blank=True, default='')
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


class RecuperacaoSenha(models.Model):
    """Modelo para armazenar tokens de recuperação de senha"""
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='recuperacoes')
    email = models.EmailField('Email para recuperação')
    token = models.CharField('Token único', max_length=255, unique=True, default=uuid.uuid4)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    expira_em = models.DateTimeField('Expira em')
    utilizado = models.BooleanField('Utilizado', default=False)
    data_utilizacao = models.DateTimeField('Data de utilização', null=True, blank=True)

    class Meta:
        verbose_name = 'Recuperação de Senha'
        verbose_name_plural = 'Recuperações de Senha'
        ordering = ['-criado_em']

    def __str__(self):
        return f'Reset {self.usuario.usuario} - {self.criado_em.date()}'

    def save(self, *args, **kwargs):
        """Define a expiração como 1 hora após criação"""
        if not self.pk:
            self.expira_em = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    def is_valido(self):
        """Verifica se o token ainda é válido"""
        return not self.utilizado and timezone.now() < self.expira_em

    def marcar_como_utilizado(self):
        """Marca o token como utilizado"""
        self.utilizado = True
        self.data_utilizacao = timezone.now()
        self.save()
