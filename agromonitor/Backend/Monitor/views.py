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

        # Estatísticas gerais
        total_usuarios = Usuario.objects.count()
        total_owners = Usuario.objects.filter(role='owner').count()
        total_supervisores = Usuario.objects.filter(role='supervisor').count()
        total_funcionarios = Usuario.objects.filter(role='employee').count()

        # Usuários ativos hoje (login feito hoje)
        usuarios_ativos_hoje = Usuario.objects.filter(ultimo_login__date=hoje).count()

        # Usuários em uso no momento (últimos 15 minutos)
        agora = timezone.now()
        usuarios_ativos_no_momento = Usuario.objects.filter(ultimo_login__gte=agora - timedelta(minutes=15)).count()

        # Usuários que utilizaram a plataforma no mês atual
        inicio_mes = hoje.replace(day=1)
        usuarios_ativos_no_mes = Usuario.objects.filter(ultimo_login__date__gte=inicio_mes).count()

        # Novos usuários hoje
        novos_usuarios_hoje = Usuario.objects.filter(criado_em__date=hoje).count()

        # Estatísticas de crescimento (últimos 30 dias)
        periodo_30dias = hoje - timedelta(days=30)
        usuarios_30dias = Usuario.objects.filter(criado_em__date__gte=periodo_30dias).count()

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

        # Adicionar métricas calculadas para super admin
        dados['usuarios_ativos_no_momento'] = usuarios_ativos_no_momento
        dados['usuarios_ativos_no_mes'] = usuarios_ativos_no_mes
        dados['crescimento_usuarios_30dias'] = usuarios_30dias

        # Buscar atividades recentes de usuários não-super admin
        super_admin_usernames = list(Usuario.objects.filter(role='super_admin').values_list('usuario', flat=True))
        atividades_recentes = AtividadeUsuario.objects.exclude(usuario_nome__in=super_admin_usernames).order_by('-data_hora')[:20]
        dados['atividades_recentes'] = [
            {
                'usuario': atividade.usuario_nome,
                'atividade': atividade.tipo_atividade,
                'data': atividade.data_hora.strftime('%d/%m/%Y %H:%M'),
                'descricao': atividade.descricao[:120] if atividade.descricao else ''
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


# =============================
# ALERTAS
# =============================

@require_http_methods(["GET"])
def listar_alertas(request):
    """Lista todos os alertas (ativos ou resolvidos)"""
    try:
        filtro_resolvido = request.GET.get('resolvido', 'false').lower() == 'true'
        limite = int(request.GET.get('limite', 20))
        
        alertas = AlertaSistema.objects.filter(resolvido=filtro_resolvido).order_by('-data_criacao')[:limite]
        
        dados = [
            {
                'id': alerta.id,
                'titulo': alerta.titulo,
                'mensagem': alerta.mensagem,
                'nivel': alerta.nivel,
                'resolvido': alerta.resolvido,
                'data_criacao': alerta.data_criacao.isoformat(),
                'data_resolucao': alerta.data_resolucao.isoformat() if alerta.data_resolucao else None,
                'usuario_relacionado': alerta.usuario_relacionado,
            }
            for alerta in alertas
        ]
        
        return JsonResponse({
            'success': True,
            'total': len(dados),
            'alertas': dados
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def resolver_alerta(request):
    """Marca um alerta como resolvido"""
    try:
        import json
        data = json.loads(request.body.decode('utf-8'))
        alerta_id = data.get('alerta_id')
        
        if not alerta_id:
            return JsonResponse({'error': 'alerta_id é obrigatório'}, status=400)
        
        alerta = AlertaSistema.objects.get(id=alerta_id)
        alerta.resolver()
        
        return JsonResponse({
            'success': True,
            'message': 'Alerta resolvido com sucesso',
            'alerta': {
                'id': alerta.id,
                'titulo': alerta.titulo,
                'resolvido': alerta.resolvido,
                'data_resolucao': alerta.data_resolucao.isoformat() if alerta.data_resolucao else None,
            }
        })
        
    except AlertaSistema.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Alerta não encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def gerar_alerta_automatico(titulo, mensagem, nivel='info', usuario_id=None):
    """
    Função auxiliar para gerar alertas automáticos
    Evita duplicatas verificando se o alerta já existe
    """
    alerta_existente = AlertaSistema.objects.filter(
        titulo=titulo,
        resolvido=False
    ).first()
    
    if not alerta_existente:
        AlertaSistema.objects.create(
            titulo=titulo,
            mensagem=mensagem,
            nivel=nivel,
            resolvido=False,
            usuario_relacionado=usuario_id
        )
        return True
    
    return False
