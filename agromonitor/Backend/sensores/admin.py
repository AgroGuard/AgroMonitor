from django.contrib import admin
from .models import Dispositivo, SensorData, ComandoAtuador, RegraAutomacao


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'dispositivo_id', 'tipo', 'estufa', 'online', 'bateria', 'ultima_comunicacao')
    list_filter = ('tipo', 'estufa', 'ativo', 'online', 'criado_em')
    search_fields = ('nome', 'dispositivo_id', 'estufa')
    readonly_fields = ('criado_em', 'atualizado_em', 'ultima_comunicacao')
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'dispositivo_id', 'tipo')
        }),
        ('Localização', {
            'fields': ('estufa', 'localizacao')
        }),
        ('Status', {
            'fields': ('ativo', 'online', 'ultima_comunicacao', 'bateria')
        }),
        ('Firmware', {
            'fields': ('firmware_version',)
        }),
        ('Timestamps', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('sensor_id', 'dispositivo', 'temperatura', 'umidade', 'timestamp')
    list_filter = ('dispositivo', 'timestamp')
    search_fields = ('sensor_id', 'dispositivo__nome')
    readonly_fields = ('timestamp', 'recebido_em')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Dispositivo', {
            'fields': ('dispositivo', 'sensor_id')
        }),
        ('Leituras', {
            'fields': ('temperatura', 'umidade', 'luminosidade', 'co2')
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'recebido_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ComandoAtuador)
class ComandoAtuadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'dispositivo', 'comando', 'status', 'criado_em', 'executado_em')
    list_filter = ('status', 'dispositivo', 'criado_em')
    search_fields = ('dispositivo__nome', 'comando')
    readonly_fields = ('criado_em', 'enviado_em', 'executado_em')
    
    fieldsets = (
        ('Dispositivo', {
            'fields': ('dispositivo',)
        }),
        ('Comando', {
            'fields': ('comando', 'parametros')
        }),
        ('Status', {
            'fields': ('status', 'mensagem_erro')
        }),
        ('Timeline', {
            'fields': ('criado_em', 'enviado_em', 'executado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RegraAutomacao)
class RegraAutomacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sensor', 'condicao', 'valor_limite', 'acao', 'ativa', 'ultima_execucao')
    list_filter = ('ativa', 'condicao', 'acao', 'criado_em')
    search_fields = ('nome', 'descricao', 'sensor__nome', 'atuador__nome')
    readonly_fields = ('criado_em', 'atualizado_em', 'ultima_execucao')
    
    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'descricao')
        }),
        ('Condição (Se...)', {
            'fields': ('sensor', 'condicao', 'valor_limite'),
            'description': 'Define a condição que dispara a regra'
        }),
        ('Ação (Então...)', {
            'fields': ('atuador', 'acao'),
            'description': 'Define a ação a executar quando a condição é atendida'
        }),
        ('Controle', {
            'fields': ('ativa', 'tempo_espera_min'),
            'description': 'Ativa/desativa a regra e define intervalo mínimo entre execuções'
        }),
        ('Histórico', {
            'fields': ('ultima_execucao', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

