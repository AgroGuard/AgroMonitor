from django.db import models
from django.utils import timezone
from datetime import timedelta


class EstatisticaPlataforma(models.Model):
    """Modelo para armazenar estatísticas gerais da plataforma"""
    data = models.DateField('Data', unique=True)
    total_usuarios = models.IntegerField('Total de usuários', default=0)
    total_owners = models.IntegerField('Total de owners', default=0)
    total_supervisores = models.IntegerField('Total de supervisores', default=0)
    total_funcionarios = models.IntegerField('Total de funcionários', default=0)
    total_estufas = models.IntegerField('Total de estufas', default=0)
    total_relatorios = models.IntegerField('Total de relatórios', default=0)
    usuarios_ativos_hoje = models.IntegerField('Usuários ativos hoje', default=0)
    novos_usuarios_hoje = models.IntegerField('Novos usuários hoje', default=0)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Estatística da Plataforma'
        verbose_name_plural = 'Estatísticas da Plataforma'
        ordering = ['-data']

    def __str__(self):
        return f'Estatísticas do dia {self.data}'


class AtividadeUsuario(models.Model):
    """Modelo para rastrear atividades dos usuários"""
    usuario_id = models.IntegerField('ID do usuário')
    usuario_nome = models.CharField('Nome do usuário', max_length=150)
    usuario_email = models.EmailField('Email do usuário')
    tipo_atividade = models.CharField('Tipo de atividade', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    data_hora = models.DateTimeField('Data e hora', auto_now_add=True)
    ip_address = models.GenericIPAddressField('Endereço IP', null=True, blank=True)

    class Meta:
        verbose_name = 'Atividade do Usuário'
        verbose_name_plural = 'Atividades dos Usuários'
        ordering = ['-data_hora']

    def __str__(self):
        return f'{self.usuario_nome} - {self.tipo_atividade} ({self.data_hora.date()})'


class AlertaSistema(models.Model):
    """Modelo para alertas e notificações do sistema"""
    NIVEL_CHOICES = [
        ('info', 'Informação'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
        ('critical', 'Crítico'),
    ]

    titulo = models.CharField('Título', max_length=200)
    mensagem = models.TextField('Mensagem')
    nivel = models.CharField('Nível', max_length=20, choices=NIVEL_CHOICES, default='info')
    resolvido = models.BooleanField('Resolvido', default=False)
    data_criacao = models.DateTimeField('Data de criação', auto_now_add=True)
    data_resolucao = models.DateTimeField('Data de resolução', null=True, blank=True)
    usuario_relacionado = models.IntegerField('ID do usuário relacionado', null=True, blank=True)

    class Meta:
        verbose_name = 'Alerta do Sistema'
        verbose_name_plural = 'Alertas do Sistema'
        ordering = ['-data_criacao']

    def __str__(self):
        return f'{self.nivel.upper()}: {self.titulo}'

    def resolver(self):
        """Marca o alerta como resolvido"""
        self.resolvido = True
        self.data_resolucao = timezone.now()
        self.save()


class MetricasTempoReal(models.Model):
    """Modelo para métricas em tempo real da plataforma"""
    chave = models.CharField('Chave da métrica', max_length=100, unique=True)
    valor = models.IntegerField('Valor')
    unidade = models.CharField('Unidade', max_length=50, blank=True)
    descricao = models.TextField('Descrição', blank=True)
    ultima_atualizacao = models.DateTimeField('Última atualização', auto_now=True)

    class Meta:
        verbose_name = 'Métrica em Tempo Real'
        verbose_name_plural = 'Métricas em Tempo Real'

    def __str__(self):
        return f'{self.chave}: {self.valor} {self.unidade}'
