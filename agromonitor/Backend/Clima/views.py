import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import LocalidadeClima, PrevisaoTempo, AlertaClima, HistoricoClima, NotaUsuario
from .serializers import (
    LocalidadeClimaSerializer, PrevisaoTempoSerializer, 
    AlertaClimaSerializer, HistoricoClimaSerializer, NotaUsuarioSerializer
)
from .services import OpenWeatherMapService
import logging
from django.conf import settings

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


class NotaUsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar notas de usuário."""

    serializer_class = NotaUsuarioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return NotaUsuario.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    def destroy(self, request, *args, **kwargs):
        nota = self.get_object()
        if nota.usuario != request.user:
            return Response({'erro': 'Não autorizado.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


@require_http_methods(["GET"])
@csrf_exempt
def listar_regioes_view(request):
    """Lista regiões cadastradas para exibição no clima da dashboard."""
    try:
        regioes = LocalidadeClima.objects.filter(ativa=True).order_by('nome')
        dados = [
            {
                'id': item.id,
                'nome': item.nome,
                'cidade': item.nome,
                'estado': item.estado,
                'pais': item.pais,
                'clima_tag': getattr(item, 'clima_tag', ''),
                'latitude': item.latitude,
                'longitude': item.longitude,
                'fazenda_id': item.fazenda_id,
            }
            for item in regioes
        ]
        return JsonResponse({'sucesso': True, 'regioes': dados})
    except Exception as e:
        logger.error(f"Erro ao listar regiões: {e}")
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)



@csrf_exempt
def localidades_view(request):
    """Compat layer: aceita GET para listar localidades e POST para cadastrar.

    Isso garante compatibilidade com clientes que usam /api/localidades/ sem autenticação.
    """
    if request.method == 'GET':
        return listar_regioes_view(request)
    if request.method == 'POST':
        return cadastrar_regiao_view(request)
    return JsonResponse({'sucesso': False, 'erro': 'Método não permitido.'}, status=405)


@csrf_exempt
def previsoes_atuais_compat_view(request, pk):
    """Compat endpoint GET para retornar previsões atuais sem autenticação (apenas em DEBUG)."""
    if request.method != 'GET':
        return JsonResponse({'sucesso': False, 'erro': 'Método não permitido.'}, status=405)

    try:
        localidade = LocalidadeClima.objects.get(pk=pk)
    except LocalidadeClima.DoesNotExist:
        return JsonResponse({'sucesso': False, 'erro': 'Localidade não encontrada.'}, status=404)

    previsao_atual = localidade.previsoes.order_by('-data_hora').first()
    agora = timezone.now()
    previsoes_futuras = localidade.previsoes.filter(data_hora__gte=agora).order_by('data_hora')[:40]

    return JsonResponse({
        'localidade': LocalidadeClimaSerializer(localidade).data,
        'previsao_atual': PrevisaoTempoSerializer(previsao_atual).data if previsao_atual else None,
        'previsoes_proximos_dias': PrevisaoTempoSerializer(previsoes_futuras, many=True).data,
    })


@require_http_methods(["POST"])
@csrf_exempt
def atualizar_previsao_compat_view(request, pk):
    """Compat endpoint POST para atualizar previsão sem autenticação — habilitado somente em DEBUG."""
    if not settings.DEBUG:
        return JsonResponse({'sucesso': False, 'erro': 'Not allowed in production.'}, status=403)

    try:
        localidade = LocalidadeClima.objects.get(pk=pk)
    except LocalidadeClima.DoesNotExist:
        return JsonResponse({'sucesso': False, 'erro': 'Localidade não encontrada.'}, status=404)

    try:
        service = OpenWeatherMapService()
        resultado = service.atualizar_previsao_localidade(localidade)

        return JsonResponse({
            'sucesso': resultado.get('sucesso', False),
            'previsao_atual': PrevisaoTempoSerializer(resultado.get('previsao_atual')).data if resultado.get('previsao_atual') else None,
            'alertas': AlertaClimaSerializer(resultado.get('alertas', []), many=True).data,
            'mensagem': 'Previsão atualizada com sucesso' if resultado.get('sucesso') else 'Erro ao atualizar previsão'
        })
    except Exception as e:
        logger.error(f"Erro ao atualizar previsão (compat): {e}")
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def atualizar_todas_compat_view(request):
    """Compat endpoint POST para atualizar todas previsões sem autenticação — somente em DEBUG."""
    if not settings.DEBUG:
        return JsonResponse({'sucesso': False, 'erro': 'Not allowed in production.'}, status=403)

    try:
        service = OpenWeatherMapService()
        resultados = service.atualizar_todas_localidades()
        total_sucessos = sum(1 for r in resultados if r['resultado'].get('sucesso'))
        total_erros = len(resultados) - total_sucessos
        return JsonResponse({
            'total_localidades': len(resultados),
            'sucessos': total_sucessos,
            'erros': total_erros,
            'detalhes': resultados
        })
    except Exception as e:
        logger.error(f"Erro ao atualizar todas (compat): {e}")
        return JsonResponse({'erro': str(e)}, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def cadastrar_regiao_view(request):
    """Cadastra uma região/clima simples para a dashboard."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        nome = (data.get('nome') or '').strip()
        estado = (data.get('estado') or '').strip()
        pais = (data.get('pais') or 'Brasil').strip()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        fazenda_id = (data.get('fazenda_id') or 'fazenda-principal').strip()

        # Support new simplified flow: if latitude/longitude are not provided,
        # infer representative coordinates and a climate tag from the provided state.
        STATE_CLIMATE = {
            'AC': {'lat': -8.77, 'lon': -70.55, 'clima': 'Equatorial'},
            'AL': {'lat': -9.62, 'lon': -36.82, 'clima': 'Tropical'},
            'AP': {'lat': 1.41, 'lon': -51.77, 'clima': 'Equatorial'},
            'AM': {'lat': -3.13, 'lon': -60.02, 'clima': 'Equatorial'},
            'BA': {'lat': -12.97, 'lon': -38.50, 'clima': 'Tropical'},
            'CE': {'lat': -3.71, 'lon': -38.54, 'clima': 'Semiárido'},
            'DF': {'lat': -15.79, 'lon': -47.86, 'clima': 'Tropical de Altitude'},
            'ES': {'lat': -20.31, 'lon': -40.34, 'clima': 'Tropical'},
            'GO': {'lat': -16.64, 'lon': -49.31, 'clima': 'Tropical de Altitude'},
            'MA': {'lat': -2.53, 'lon': -44.30, 'clima': 'Equatorial'},
            'MT': {'lat': -12.64, 'lon': -55.42, 'clima': 'Tropical'},
            'MS': {'lat': -20.47, 'lon': -54.62, 'clima': 'Tropical'},
            'MG': {'lat': -19.92, 'lon': -43.94, 'clima': 'Tropical de Altitude'},
            'PA': {'lat': -1.45, 'lon': -48.49, 'clima': 'Equatorial'},
            'PB': {'lat': -7.12, 'lon': -34.86, 'clima': 'Tropical'},
            'PR': {'lat': -25.43, 'lon': -49.27, 'clima': 'Subtropical'},
            'PE': {'lat': -8.05, 'lon': -34.90, 'clima': 'Tropical'},
            'PI': {'lat': -5.09, 'lon': -42.80, 'clima': 'Semiárido'},
            'RJ': {'lat': -22.90, 'lon': -43.20, 'clima': 'Tropical'},
            'RN': {'lat': -5.22, 'lon': -36.52, 'clima': 'Semiárido'},
            'RS': {'lat': -30.03, 'lon': -51.23, 'clima': 'Subtropical'},
            'RO': {'lat': -8.76, 'lon': -63.90, 'clima': 'Equatorial'},
            'RR': {'lat': 2.82, 'lon': -60.67, 'clima': 'Equatorial'},
            'SC': {'lat': -27.59, 'lon': -48.55, 'clima': 'Subtropical'},
            'SP': {'lat': -23.55, 'lon': -46.63, 'clima': 'Tropical de Altitude'},
            'SE': {'lat': -10.90, 'lon': -37.07, 'clima': 'Tropical'},
            'TO': {'lat': -10.25, 'lon': -48.25, 'clima': 'Tropical'},
        }

        if (latitude in (None, '')) or (longitude in (None, '')):
            # Try to accept either state abbreviations or full names (case-insensitive)
            estado_key = estado.upper() if estado else ''
            # allow full state names by mapping common names to abbreviations
            NOME_TO_UF = {
                'ACRE': 'AC','ALAGOAS':'AL','AMAPA':'AP','AMAZONAS':'AM','BAHIA':'BA',
                'CEARA':'CE','DISTRITO FEDERAL':'DF','ESPIRITO SANTO':'ES','GOIAS':'GO',
                'MARANHAO':'MA','MATO GROSSO':'MT','MATO GROSSO DO SUL':'MS','MINAS GERAIS':'MG',
                'PARA':'PA','PARAIBA':'PB','PARANA':'PR','PERNAMBUCO':'PE','PIAUI':'PI',
                'RIO DE JANEIRO':'RJ','RIO GRANDE DO NORTE':'RN','RIO GRANDE DO SUL':'RS',
                'RONDONIA':'RO','RORAIMA':'RR','SANTA CATARINA':'SC','SAO PAULO':'SP',
                'SERGIPE':'SE','TOCANTINS':'TO'
            }
            if estado_key in STATE_CLIMATE:
                info = STATE_CLIMATE[estado_key]
            else:
                mapped = NOME_TO_UF.get(estado_key)
                info = STATE_CLIMATE.get(mapped) if mapped else None

            if not info:
                return JsonResponse({'sucesso': False, 'erro': 'Estado inválido ou sem mapeamento.'}, status=400)

            latitude = info['lat']
            longitude = info['lon']
            # Create a default name if none provided
            if not nome:
                nome = f"Região - {estado_key}"
            clima_tag = info.get('clima')
        else:
            clima_tag = None

        localidade = LocalidadeClima.objects.create(
            nome=nome,
            latitude=float(latitude),
            longitude=float(longitude),
            pais=pais,
            estado=estado,
            ativa=True,
            fazenda_id=fazenda_id,
            clima_tag=clima_tag if clima_tag else ''
        )

        return JsonResponse({
            'sucesso': True,
            'mensagem': 'Região cadastrada com sucesso.',
            'regiao': {
                'id': localidade.id,
                'nome': localidade.nome,
                'estado': localidade.estado,
                'pais': localidade.pais,
                'latitude': localidade.latitude,
                'longitude': localidade.longitude,
            },
        }, status=201)
    except Exception as e:
        logger.error(f"Erro ao cadastrar região: {e}")
        return JsonResponse({'sucesso': False, 'erro': str(e)}, status=400)


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
