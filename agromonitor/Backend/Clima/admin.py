from django.contrib import admin
from .models import LocalidadeClima, PrevisaoTempo, AlertaClima, HistoricoClima


@admin.register(LocalidadeClima)
class LocalidadeClimaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'latitude', 'longitude', 'pais', 'estado', 'ativa', 'criada_em')
    list_filter = ('ativa', 'pais', 'criada_em')
    search_fields = ('nome', 'pais', 'estado', 'fazenda_id')
    readonly_fields = ('criada_em', 'atualizada_em')


@admin.register(PrevisaoTempo)
class PrevisaoTempoAdmin(admin.ModelAdmin):
    list_display = ('localidade', 'data_hora', 'temperatura_atual', 'condicao_tempo', 'umidade', 'chance_chuva')
    list_filter = ('condicao_tempo', 'data_hora', 'localidade')
    search_fields = ('localidade__nome', 'descricao')
    readonly_fields = ('data_requisicao',)
    fieldsets = (
        ('Localidade', {'fields': ('localidade',)}),
        ('Temperatura', {'fields': ('temperatura_minima', 'temperatura_maxima', 'temperatura_atual', 'sensacao_termica')}),
        ('Umidade e Pressão', {'fields': ('umidade', 'pressao')}),
        ('Vento', {'fields': ('velocidade_vento', 'direcao_vento')}),
        ('Condições', {'fields': ('condicao_tempo', 'descricao', 'cobertura_nuvem', 'chance_chuva', 'precipitacao')}),
        ('Outros', {'fields': ('indice_uv', 'visibilidade', 'fonte', 'data_hora', 'data_requisicao')}),
    )


@admin.register(AlertaClima)
class AlertaClimaAdmin(admin.ModelAdmin):
    list_display = ('localidade', 'tipo_alerta', 'severidade', 'ativo', 'data_inicio')
    list_filter = ('tipo_alerta', 'severidade', 'ativo', 'data_inicio')
    search_fields = ('localidade__nome', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(HistoricoClima)
class HistoricoClimaAdmin(admin.ModelAdmin):
    list_display = ('localidade', 'data', 'temperatura_maxima', 'temperatura_minima', 'precipitacao_total')
    list_filter = ('localidade', 'data')
    search_fields = ('localidade__nome',)
    readonly_fields = ('criado_em',)
