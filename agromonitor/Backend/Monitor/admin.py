from django.contrib import admin
from .models import EstatisticaPlataforma, AtividadeUsuario, AlertaSistema, MetricasTempoReal


@admin.register(EstatisticaPlataforma)
class EstatisticaPlataformaAdmin(admin.ModelAdmin):
    list_display = ['data', 'total_usuarios', 'total_owners', 'usuarios_ativos_hoje', 'novos_usuarios_hoje']
    list_filter = ['data']
    readonly_fields = ['criado_em']
    ordering = ['-data']


@admin.register(AtividadeUsuario)
class AtividadeUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario_nome', 'tipo_atividade', 'data_hora', 'ip_address']
    list_filter = ['tipo_atividade', 'data_hora']
    search_fields = ['usuario_nome', 'usuario_email', 'tipo_atividade']
    readonly_fields = ['data_hora']


@admin.register(AlertaSistema)
class AlertaSistemaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'nivel', 'resolvido', 'data_criacao', 'usuario_relacionado']
    list_filter = ['nivel', 'resolvido', 'data_criacao']
    search_fields = ['titulo', 'mensagem']
    readonly_fields = ['data_criacao', 'data_resolucao']
    actions = ['marcar_como_resolvido']

    def marcar_como_resolvido(self, request, queryset):
        for alerta in queryset:
            alerta.resolver()
        self.message_user(request, f'{queryset.count()} alerta(s) marcado(s) como resolvido(s).')
    marcar_como_resolvido.short_description = 'Marcar alertas selecionados como resolvidos'


@admin.register(MetricasTempoReal)
class MetricasTempoRealAdmin(admin.ModelAdmin):
    list_display = ['chave', 'valor', 'unidade', 'ultima_atualizacao']
    search_fields = ['chave', 'descricao']
    readonly_fields = ['ultima_atualizacao']
