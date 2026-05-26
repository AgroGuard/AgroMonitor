from django.db import models
from django.utils import timezone


class LocalidadeClima(models.Model):
    """Modelo para armazenar localidades e suas coordenadas para previsão do tempo"""
    
    nome = models.CharField('Nome da Localidade', max_length=200)
    latitude = models.FloatField('Latitude')
    longitude = models.FloatField('Longitude')
    pais = models.CharField('País', max_length=100, blank=True)
    estado = models.CharField('Estado/Província', max_length=100, blank=True)
    
    # Configuração
    ativa = models.BooleanField('Ativa', default=True)
    fazenda_id = models.CharField('ID da Fazenda', max_length=100, blank=True)
    
    # Timestamps
    criada_em = models.DateTimeField('Criada em', auto_now_add=True)
    atualizada_em = models.DateTimeField('Atualizada em', auto_now=True)
    
    class Meta:
        verbose_name = 'Localidade de Clima'
        verbose_name_plural = 'Localidades de Clima'
        ordering = ['nome']
        unique_together = ('latitude', 'longitude')
    
    def __str__(self):
        return f"{self.nome} ({self.latitude}, {self.longitude})"


class PrevisaoTempo(models.Model):
    """Modelo para armazenar previsões de tempo"""
    
    CONDICAO_CHOICES = [
        ('limpo', 'Céu Limpo'),
        ('nublado', 'Nublado'),
        ('nuvem_leve', 'Poucas Nuvens'),
        ('chuvoso', 'Chuvoso'),
        ('tempestade', 'Tempestade'),
        ('neve', 'Neve'),
        ('neblina', 'Neblina'),
    ]
    
    localidade = models.ForeignKey(LocalidadeClima, on_delete=models.CASCADE, related_name='previsoes')
    
    # Dados da previsão
    data_hora = models.DateTimeField('Data e Hora da Previsão')
    temperatura_minima = models.FloatField('Temperatura Mínima (°C)')
    temperatura_maxima = models.FloatField('Temperatura Máxima (°C)')
    temperatura_atual = models.FloatField('Temperatura Atual (°C)')
    sensacao_termica = models.FloatField('Sensação Térmica (°C)', null=True, blank=True)
    
    umidade = models.IntegerField('Umidade (%)')
    pressao = models.IntegerField('Pressão (hPa)')
    velocidade_vento = models.FloatField('Velocidade do Vento (m/s)')
    direcao_vento = models.IntegerField('Direção do Vento (graus)', null=True, blank=True)
    
    cobertura_nuvem = models.IntegerField('Cobertura de Nuvem (%)')
    chance_chuva = models.IntegerField('Chance de Chuva (%)', default=0)
    precipitacao = models.FloatField('Precipitação (mm)', null=True, blank=True)
    
    condicao_tempo = models.CharField('Condição do Tempo', max_length=20, choices=CONDICAO_CHOICES)
    descricao = models.CharField('Descrição', max_length=255, blank=True)
    
    indice_uv = models.FloatField('Índice UV', null=True, blank=True)
    visibilidade = models.IntegerField('Visibilidade (m)', null=True, blank=True)
    
    # Metadados
    fonte = models.CharField('Fonte de Dados', max_length=50, default='openweathermap')
    data_requisicao = models.DateTimeField('Data da Requisição', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Previsão de Tempo'
        verbose_name_plural = 'Previsões de Tempo'
        ordering = ['-data_hora']
        indexes = [
            models.Index(fields=['localidade', '-data_hora']),
            models.Index(fields=['-data_hora']),
        ]
    
    def __str__(self):
        return f"{self.localidade.nome} - {self.data_hora} - {self.condicao_tempo}"


class AlertaClima(models.Model):
    """Modelo para armazenar alertas de condições climáticas extremas"""
    
    TIPO_ALERTA_CHOICES = [
        ('chuva_forte', 'Chuva Forte'),
        ('tempestade', 'Tempestade'),
        ('vento_forte', 'Vento Forte'),
        ('geada', 'Geada'),
        ('seca', 'Seca'),
        ('calor_extremo', 'Calor Extremo'),
        ('frio_extremo', 'Frio Extremo'),
        ('granizo', 'Granizo'),
    ]
    
    SEVERIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    localidade = models.ForeignKey(LocalidadeClima, on_delete=models.CASCADE, related_name='alertas')
    previsao = models.ForeignKey(PrevisaoTempo, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas')
    
    tipo_alerta = models.CharField('Tipo de Alerta', max_length=20, choices=TIPO_ALERTA_CHOICES)
    severidade = models.CharField('Severidade', max_length=10, choices=SEVERIDADE_CHOICES)
    
    descricao = models.TextField('Descrição')
    recomendacoes = models.TextField('Recomendações', blank=True)
    
    ativo = models.BooleanField('Ativo', default=True)
    data_inicio = models.DateTimeField('Data de Início')
    data_fim = models.DateTimeField('Data de Término', null=True, blank=True)
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Alerta de Clima'
        verbose_name_plural = 'Alertas de Clima'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"{self.localidade.nome} - {self.tipo_alerta} ({self.severidade})"


class HistoricoClima(models.Model):
    """Modelo para armazenar dados históricos do clima"""
    
    localidade = models.ForeignKey(LocalidadeClima, on_delete=models.CASCADE, related_name='historicos')
    
    data = models.DateField('Data')
    temperatura_minima = models.FloatField('Temperatura Mínima (°C)')
    temperatura_maxima = models.FloatField('Temperatura Máxima (°C)')
    temperatura_media = models.FloatField('Temperatura Média (°C)')
    
    umidade_media = models.IntegerField('Umidade Média (%)')
    precipitacao_total = models.FloatField('Precipitação Total (mm)')
    velocidade_vento_media = models.FloatField('Velocidade Média do Vento (m/s)')
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Histórico de Clima'
        verbose_name_plural = 'Históricos de Clima'
        ordering = ['-data']
        unique_together = ('localidade', 'data')
    
    def __str__(self):
        return f"{self.localidade.nome} - {self.data}"
