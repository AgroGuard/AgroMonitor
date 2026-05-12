import json
from datetime import timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from Cadastro.models import Usuario
from .models import EstatisticaPlataforma, AtividadeUsuario, AlertaSistema, MetricasTempoReal


def dashboard_view(request):
    """View principal da dashboard"""
    # Verificar se usuário é admin/super admin
    # Por enquanto, permite acesso a todos (depois implementar verificação)

    context = {
        'titulo': 'Dashboard AgroMonitor',
        'data_atual': timezone.now().date(),
    }

    return render(request, 'dashboard.html', context)


@require_http_methods(["GET"])
def dashboard_stats_api(request):
    """API que retorna estatísticas da plataforma"""
    try:
        hoje = timezone.now().date()
        ontem = hoje - timedelta(days=1)
        semana_passada = hoje - timedelta(days=7)

        # Estatísticas gerais
        total_usuarios = Usuario.objects.count()
        total_owners = Usuario.objects.filter(role='owner').count()
        total_supervisores = Usuario.objects.filter(role='supervisor').count()
        total_funcionarios = Usuario.objects.filter(role='employee').count()

        # Usuários ativos hoje (login feito hoje)
        usuarios_ativos_hoje = Usuario.objects.filter(ultimo_login__date=hoje).count()

        # Novos usuários hoje
        novos_usuarios_hoje = Usuario.objects.filter(criado_em__date=hoje).count()

        # Estatísticas de crescimento (últimos 7 dias)
        usuarios_semana_passada = Usuario.objects.filter(criado_em__date__lt=semana_passada).count()

        # Buscar estatísticas armazenadas (se existirem)
        estatistica_hoje = EstatisticaPlataforma.objects.filter(data=hoje).first()
        if estatistica_hoje:
            dados = {
                'total_usuarios': estatistica_hoje.total_usuarios,
                'total_owners': estatistica_hoje.total_owners,
                'total_supervisores': estatistica_hoje.total_supervisores,
                'total_funcionarios': estatistica_hoje.total_funcionarios,
                'total_estufas': estatistica_hoje.total_estufas,
                'total_relatorios': estatistica_hoje.total_relatorios,
                'usuarios_ativos_hoje': estatistica_hoje.usuarios_ativos_hoje,
                'novos_usuarios_hoje': estatistica_hoje.novos_usuarios_hoje,
            }
        else:
            # Dados estimados se não houver estatísticas armazenadas
            dados = {
                'total_usuarios': total_usuarios,
                'total_owners': total_owners,
                'total_supervisores': total_supervisores,
                'total_funcionarios': total_funcionarios,
                'total_estufas': 0,  # Implementar quando houver modelo de estufa
                'total_relatorios': 0,  # Implementar quando houver modelo de relatório
                'usuarios_ativos_hoje': usuarios_ativos_hoje,
                'novos_usuarios_hoje': novos_usuarios_hoje,
            }

        # Adicionar métricas de crescimento
        dados['crescimento_usuarios_7dias'] = dados['total_usuarios'] - usuarios_semana_passada

        # Buscar atividades recentes
        atividades_recentes = AtividadeUsuario.objects.all()[:10]
        dados['atividades_recentes'] = [
            {
                'usuario': atividade.usuario_nome,
                'atividade': atividade.tipo_atividade,
                'data': atividade.data_hora.strftime('%d/%m/%Y %H:%M'),
                'descricao': atividade.descricao[:100] if atividade.descricao else ''
            }
            for atividade in atividades_recentes
        ]

        # Buscar alertas ativos
        alertas_ativos = AlertaSistema.objects.filter(resolvido=False)[:5]
        dados['alertas_ativos'] = [
            {
                'titulo': alerta.titulo,
                'nivel': alerta.nivel,
                'data': alerta.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'mensagem': alerta.mensagem[:200] if alerta.mensagem else ''
            }
            for alerta in alertas_ativos
        ]

        # Buscar métricas em tempo real
        metricas_tempo_real = MetricasTempoReal.objects.all()
        dados['metricas_tempo_real'] = {
            metrica.chave: {
                'valor': metrica.valor,
                'unidade': metrica.unidade,
                'ultima_atualizacao': metrica.ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S')
            }
            for metrica in metricas_tempo_real
        }

        return JsonResponse({
            'success': True,
            'data': dados,
            'timestamp': timezone.now().isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def atualizar_estatisticas_diarias():
    """Função para atualizar estatísticas diárias (pode ser chamada por cron job)"""
    hoje = timezone.now().date()

    # Verificar se já existe estatística para hoje
    if EstatisticaPlataforma.objects.filter(data=hoje).exists():
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
    EstatisticaPlataforma.objects.create(
        data=hoje,
        total_usuarios=total_usuarios,
        total_owners=total_owners,
        total_supervisores=total_supervisores,
        total_funcionarios=total_funcionarios,
        total_estufas=0,  # Implementar
        total_relatorios=0,  # Implementar
        usuarios_ativos_hoje=usuarios_ativos,
        novos_usuarios_hoje=novos_usuarios,
    )
