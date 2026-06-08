from django.db import models
from django.utils import timezone
from datetime import timedelta

from Cadastro.models import Tenant

class Dispositivo(models.Model):
    """Modelo para armazenar dispositivos IoT (sensores e atuadores)"""
    TIPO_CHOICES = [
        ('sensor_temp', 'Sensor de Temperatura'),
        ('sensor_umidade', 'Sensor de Umidade'),
        ('sensor_luz', 'Sensor de Luminosidade'),
        ('sensor_co2', 'Sensor de CO2'),
        ('atuador_bomba', 'Bomba de Irrigação'),
        ('atuador_ventilador', 'Ventilador'),
        ('atuador_luz', 'Sistema de Iluminação'),
    ]

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispositivos',
        verbose_name='Tenant/Owner'
    )
    nome = models.CharField('Nome do dispositivo', max_length=100)
    dispositivo_id = models.CharField('ID MQTT', max_length=50, unique=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    estufa = models.CharField('Estufa', max_length=100, blank=True)
    
    # Status
    ativo = models.BooleanField('Ativo', default=True)
    online = models.BooleanField('Online', default=False)
    ultima_comunicacao = models.DateTimeField('Última comunicação', null=True, blank=True)
    
    # Metadados
    localizacao = models.CharField('Localização', max_length=200, blank=True)
    bateria = models.IntegerField('Bateria %', null=True, blank=True)
    firmware_version = models.CharField('Versão Firmware', max_length=50, blank=True)
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Dispositivo IoT'
        verbose_name_plural = 'Dispositivos IoT'
        ordering = ['estufa', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.dispositivo_id})"

    def esta_offline(self):
        """Verifica se dispositivo está offline (sem comunicação há 5 min)"""
        if not self.ultima_comunicacao:
            return True
        tempo_limite = timezone.now() - timedelta(minutes=5)
        return self.ultima_comunicacao < tempo_limite


class SensorData(models.Model):
    """Modelo para armazenar leituras de sensores"""
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='leituras')
    sensor_id = models.CharField(max_length=50)
    
    temperatura = models.FloatField(null=True, blank=True)
    umidade = models.FloatField(null=True, blank=True)
    luminosidade = models.FloatField(null=True, blank=True)
    co2 = models.FloatField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    recebido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Leitura de Sensor'
        verbose_name_plural = 'Leituras de Sensores'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor_id', '-timestamp']),
            models.Index(fields=['dispositivo', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.sensor_id} - {self.timestamp}"


class ComandoAtuador(models.Model):
    """Modelo para armazenar comandos enviados para atuadores"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('enviado', 'Enviado'),
        ('executado', 'Executado'),
        ('erro', 'Erro'),
    ]

    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='comandos')
    comando = models.CharField('Comando', max_length=100)
    parametros = models.JSONField('Parâmetros', default=dict)
    
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')
    mensagem_erro = models.TextField('Mensagem de erro', blank=True)
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    enviado_em = models.DateTimeField('Enviado em', null=True, blank=True)
    executado_em = models.DateTimeField('Executado em', null=True, blank=True)

    class Meta:
        verbose_name = 'Comando de Atuador'
        verbose_name_plural = 'Comandos de Atuadores'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.dispositivo.nome}: {self.comando} ({self.status})"

    def marcar_como_enviado(self):
        """Marca comando como enviado"""
        self.status = 'enviado'
        self.enviado_em = timezone.now()
        self.save()

    def marcar_como_executado(self):
        """Marca comando como executado"""
        self.status = 'executado'
        self.executado_em = timezone.now()
        self.save()

    def marcar_como_erro(self, mensagem):
        """Marca comando com erro"""
        self.status = 'erro'
        self.mensagem_erro = mensagem
        self.save()


class RegraAutomacao(models.Model):
    """Modelo para regras de automação"""
    CONDICAO_CHOICES = [
        ('temperatura_maior', 'Temperatura >'),
        ('temperatura_menor', 'Temperatura <'),
        ('umidade_maior', 'Umidade >'),
        ('umidade_menor', 'Umidade <'),
        ('luminosidade_maior', 'Luminosidade >'),
        ('luminosidade_menor', 'Luminosidade <'),
    ]

    ACAO_CHOICES = [
        ('ligar_bomba', 'Ligar Bomba'),
        ('desligar_bomba', 'Desligar Bomba'),
        ('ligar_ventilador', 'Ligar Ventilador'),
        ('desligar_ventilador', 'Desligar Ventilador'),
        ('ligar_luz', 'Ligar Luz'),
        ('desligar_luz', 'Desligar Luz'),
        ('alerta', 'Gerar Alerta'),
    ]

    nome = models.CharField('Nome da regra', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    
    # Condição
    sensor = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='regras_sensor')
    condicao = models.CharField('Condição', max_length=20, choices=CONDICAO_CHOICES)
    valor_limite = models.FloatField('Valor limite')
    
    # Ação
    atuador = models.ForeignKey(Dispositivo, on_delete=models.CASCADE, related_name='regras_atuador', null=True, blank=True)
    acao = models.CharField('Ação', max_length=20, choices=ACAO_CHOICES)
    
    # Controle
    ativa = models.BooleanField('Ativa', default=True)
    tempo_espera_min = models.IntegerField('Tempo de espera mínimo (min)', default=0)
    ultima_execucao = models.DateTimeField('Última execução', null=True, blank=True)
    
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Regra de Automação'
        verbose_name_plural = 'Regras de Automação'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome}: {self.sensor.nome} {self.condicao} {self.valor_limite}"

    def pode_executar(self):
        """Verifica se regra pode ser executada (respeitando tempo de espera)"""
        if not self.ativa:
            return False
        
        if not self.ultima_execucao:
            return True
        
        tempo_decorrido = (timezone.now() - self.ultima_execucao).total_seconds() / 60
        return tempo_decorrido >= self.tempo_espera_min