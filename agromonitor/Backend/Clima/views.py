import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import LocalidadeClima, PrevisaoTempo, AlertaClima, HistoricoClima
from .serializers import (
    LocalidadeClimaSerializer, PrevisaoTempoSerializer, 
    AlertaClimaSerializer, HistoricoClimaSerializer
)
from .services import OpenWeatherMapService
import logging

logger = logging.getLogger(__name__)


class LocalidadeClimaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar localidades de clima"""
    
    queryset = LocalidadeClima.objects.all()
    serializer_class = LocalidadeClimaSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def atualizar_previsao(self, request, pk=None):
        """Atualiza a previsão de tempo para uma localidade específica"""
        localidade = self.get_object()
        
        try:
            service = OpenWeatherMapService()
            resultado = service.atualizar_previsao_localidade(localidade)
            
            return Response({
                'sucesso': resultado['sucesso'],
                'previsao_atual': PrevisaoTempoSerializer(resultado['previsao_atual']).data if resultado['previsao_atual'] else None,
                'alertas': AlertaClimaSerializer(resultado['alertas'], many=True).data,
                'mensagem': 'Previsão atualizada com sucesso' if resultado['sucesso'] else 'Erro ao atualizar previsão'
            })
        except Exception as e:
            logger.error(f"Erro ao atualizar previsão: {e}")
            return Response({
                'sucesso': False,
                'erro': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def atualizar_todas(self, request):
        """Atualiza previsões para todas as localidades ativas"""
        try:
            service = OpenWeatherMapService()
            resultados = service.atualizar_todas_localidades()
            
            total_sucessos = sum(1 for r in resultados if r['resultado']['sucesso'])
            total_erros = len(resultados) - total_sucessos
            
            return Response({
                'total_localidades': len(resultados),
                'sucessos': total_sucessos,
                'erros': total_erros,
                'detalhes': resultados
            })
        except Exception as e:
            logger.error(f"Erro ao atualizar todas localidades: {e}")
            return Response({
                'erro': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def previsoes_atuais(self, request, pk=None):
        """Retorna as previsões atuais e próximas 5 dias para uma localidade"""
        localidade = self.get_object()
        
        # Obter previsão atual (última)
        previsao_atual = localidade.previsoes.order_by('-data_hora').first()
        
        # Obter próximas 5 dias (a cada 3 horas)
        agora = timezone.now()
        previsoes_futuras = localidade.previsoes.filter(
            data_hora__gte=agora
        ).order_by('data_hora')[:40]  # 5 dias * 8 (a cada 3h)
        
        return Response({
            'localidade': LocalidadeClimaSerializer(localidade).data,
            'previsao_atual': PrevisaoTempoSerializer(previsao_atual).data if previsao_atual else None,
            'previsoes_proximos_dias': PrevisaoTempoSerializer(previsoes_futuras, many=True).data,
        })
    
    @action(detail=True, methods=['get'])
    def alertas(self, request, pk=None):
        """Retorna alertas ativos para uma localidade"""
        localidade = self.get_object()
        alertas = localidade.alertas.filter(ativo=True).order_by('-severidade', '-data_inicio')
        
        return Response({
            'localidade': LocalidadeClimaSerializer(localidade).data,
            'alertas': AlertaClimaSerializer(alertas, many=True).data,
            'total': alertas.count()
        })
    
    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        """Retorna histórico climático de uma localidade"""
        localidade = self.get_object()
        
        # Filtrar por período (padrão: últimos 30 dias)
        dias = request.query_params.get('dias', 30)
        try:
            dias = int(dias)
        except ValueError:
            dias = 30
        
        data_inicio = timezone.now().date() - timezone.timedelta(days=dias)
        historico = localidade.historicos.filter(data__gte=data_inicio).order_by('-data')
        
        return Response({
            'localidade': LocalidadeClimaSerializer(localidade).data,
            'periodo_dias': dias,
            'historico': HistoricoClimaSerializer(historico, many=True).data,
            'total': historico.count()
        })


class PrevisaoTempoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consultar previsões de tempo"""
    
    serializer_class = PrevisaoTempoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PrevisaoTempo.objects.all()
        
        # Filtrar por localidade
        localidade_id = self.request.query_params.get('localidade_id')
        if localidade_id:
            queryset = queryset.filter(localidade_id=localidade_id)
        
        # Filtrar por condição
        condicao = self.request.query_params.get('condicao')
        if condicao:
            queryset = queryset.filter(condicao_tempo=condicao)
        
        # Filtrar por período
        periodo = self.request.query_params.get('periodo')
        if periodo == 'hoje':
            hoje = timezone.now().date()
            queryset = queryset.filter(data_hora__date=hoje)
        elif periodo == 'semana':
            data_limite = timezone.now() - timezone.timedelta(days=7)
            queryset = queryset.filter(data_hora__gte=data_limite)
        
        return queryset.order_by('-data_hora')


class AlertaClimaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consultar alertas climáticos"""
    
    serializer_class = AlertaClimaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AlertaClima.objects.all()
        
        # Filtrar por localidade
        localidade_id = self.request.query_params.get('localidade_id')
        if localidade_id:
            queryset = queryset.filter(localidade_id=localidade_id)
        
        # Filtrar por tipo de alerta
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_alerta=tipo)
        
        # Filtrar por severidade
        severidade = self.request.query_params.get('severidade')
        if severidade:
            queryset = queryset.filter(severidade=severidade)
        
        # Mostrar apenas alertas ativos
        ativos = self.request.query_params.get('ativos', True)
        if ativos in ['true', 'True', '1', 'yes']:
            queryset = queryset.filter(ativo=True)
        
        return queryset.order_by('-severidade', '-data_inicio')
    
    @action(detail=True, methods=['post'])
    def desativar(self, request, pk=None):
        """Desativa um alerta"""
        alerta = self.get_object()
        alerta.ativo = False
        alerta.data_fim = timezone.now()
        alerta.save()
        
        return Response({
            'sucesso': True,
            'mensagem': 'Alerta desativado com sucesso',
            'alerta': AlertaClimaSerializer(alerta).data
        })


class HistoricoClimaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consultar histórico climático"""
    
    serializer_class = HistoricoClimaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = HistoricoClima.objects.all()
        
        # Filtrar por localidade
        localidade_id = self.request.query_params.get('localidade_id')
        if localidade_id:
            queryset = queryset.filter(localidade_id=localidade_id)
        
        # Filtrar por período
        dias = self.request.query_params.get('dias', 30)
        try:
            dias = int(dias)
        except ValueError:
            dias = 30
        
        data_inicio = timezone.now().date() - timezone.timedelta(days=dias)
        queryset = queryset.filter(data__gte=data_inicio)
        
        return queryset.order_by('-data')


# Views simples sem autenticação (para testes)
@require_http_methods(["GET"])
def clima_resumo_view(request):
    """Retorna resumo do clima de todas as localidades ativas"""
    try:
        localidades = LocalidadeClima.objects.filter(ativa=True)
        
        resumo = []
        for localidade in localidades:
            previsao_atual = localidade.previsoes.order_by('-data_hora').first()
            alertas = localidade.alertas.filter(ativo=True).count()
            
            resumo.append({
                'id': localidade.id,
                'nome': localidade.nome,
                'latitude': localidade.latitude,
                'longitude': localidade.longitude,
                'previsao_atual': {
                    'temperatura': previsao_atual.temperatura_atual if previsao_atual else None,
                    'condicao': previsao_atual.condicao_tempo if previsao_atual else None,
                    'descricao': previsao_atual.descricao if previsao_atual else None,
                    'umidade': previsao_atual.umidade if previsao_atual else None,
                    'velocidade_vento': previsao_atual.velocidade_vento if previsao_atual else None,
                    'chance_chuva': previsao_atual.chance_chuva if previsao_atual else None,
                } if previsao_atual else None,
                'total_alertas': alertas
            })
        
        return JsonResponse({
            'sucesso': True,
            'total_localidades': len(resumo),
            'localidades': resumo
        })
    except Exception as e:
        logger.error(f"Erro ao obter resumo de clima: {e}")
        return JsonResponse({
            'sucesso': False,
            'erro': str(e)
        }, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def sincronizar_clima_view(request):
    """Sincroniza dados de clima com a API OpenWeatherMap"""
    try:
        service = OpenWeatherMapService()
        resultados = service.atualizar_todas_localidades()
        
        total_sucessos = sum(1 for r in resultados if r['resultado']['sucesso'])
        
        return JsonResponse({
            'sucesso': True,
            'total_localidades': len(resultados),
            'sucessos': total_sucessos,
            'erros': len(resultados) - total_sucessos,
            'mensagem': f"Sincronizado com sucesso: {total_sucessos}/{len(resultados)} localidades"
        })
    except Exception as e:
        logger.error(f"Erro ao sincronizar clima: {e}")
        return JsonResponse({
            'sucesso': False,
            'erro': str(e)
        }, status=400)
