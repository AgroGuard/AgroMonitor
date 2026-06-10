from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta, datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from urllib.parse import urlparse

from .models import SensorData, Dispositivo, ComandoAtuador, RegraAutomacao
from Monitor.models import AlertaSistema
from Monitor.views import gerar_alerta_automatico
import paho.mqtt.client as mqtt


# =============================
# DISPOSITIVOS IoT
# =============================

@csrf_exempt
@require_http_methods(["GET"])
@api_view(['GET'])
def listar_dispositivos(request):
    """Lista todos os dispositivos IoT"""
    try:
        tipo = request.GET.get('tipo')
        estufa = request.GET.get('estufa')
        online = request.GET.get('online')
        
        dispositivos = Dispositivo.objects.all()
        
        if tipo:
            dispositivos = dispositivos.filter(tipo=tipo)
        if estufa:
            dispositivos = dispositivos.filter(estufa=estufa)
        
        resultado = []
        for dispositivo in dispositivos:
            resultado.append({
                'id': dispositivo.id,
                'nome': dispositivo.nome,
                'dispositivo_id': dispositivo.dispositivo_id,
                'tipo': dispositivo.tipo,
                'estufa': dispositivo.estufa,
                'ativo': dispositivo.ativo,
                'online': dispositivo.online,
                'ultima_comunicacao': dispositivo.ultima_comunicacao.isoformat() if dispositivo.ultima_comunicacao else None,
                'bateria': dispositivo.bateria,
                'localizacao': dispositivo.localizacao,
            })
        
        return Response({
            'success': True,
            'total': len(resultado),
            'dispositivos': resultado
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@api_view(['POST'])
def enviar_comando_atuador(request):
    """Envia comando para um atuador"""
    try:
        data = json.loads(request.body.decode('utf-8')) if isinstance(request.body, bytes) else request.data
        
        dispositivo_id = data.get('dispositivo_id')
        comando = data.get('comando')
        parametros = data.get('parametros', {})
        
        if not dispositivo_id or not comando:
            return Response({'error': 'dispositivo_id e comando são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar dispositivo
        dispositivo = Dispositivo.objects.filter(dispositivo_id=dispositivo_id).first()
        if not dispositivo:
            return Response({'error': 'Dispositivo não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        if not dispositivo.ativo:
            return Response({'error': 'Dispositivo inativo'}, status=status.HTTP_400_BAD_REQUEST)

        usuario = getattr(request, 'user', None)
        if comando == 'configurar_parametros' and (not usuario or getattr(usuario, 'is_anonymous', True) or getattr(usuario, 'role', None) == 'employee'):
            return Response(
                {'error': 'Usuário não autorizado a alterar parâmetros da estufa.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Criar comando
        cmd = ComandoAtuador.objects.create(
            dispositivo=dispositivo,
            comando=comando,
            parametros=parametros
        )
        
        # Tentar enviar via MQTT
        try:
            enviar_comando_mqtt(dispositivo, comando, parametros)
            cmd.marcar_como_enviado()
        except Exception as mqtt_error:
            cmd.marcar_como_erro(str(mqtt_error))
            return Response({
                'success': False,
                'error': f'Erro ao enviar comando: {str(mqtt_error)}',
                'comando_id': cmd.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'message': 'Comando enviado com sucesso',
            'comando_id': cmd.id,
            'dispositivo': dispositivo.nome
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@api_view(['POST'])
def controlar_bomba(request):
    """Controla bomba de irrigação - LIGAR ou DESLIGAR"""
    try:
        data = json.loads(request.body.decode('utf-8')) if isinstance(request.body, bytes) else request.data
        
        dispositivo_id = data.get('dispositivo_id')
        estado = data.get('estado')  # 'ligar' ou 'desligar'
        
        if not dispositivo_id or estado not in ['ligar', 'desligar']:
            return Response({'error': 'dispositivo_id e estado (ligar/desligar) são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)
        
        comando = 'ligar_bomba' if estado == 'ligar' else 'desligar_bomba'
        
        # Usar endpoint genérico
        return enviar_comando_atuador_response(dispositivo_id, comando, {})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@api_view(['POST'])
def controlar_ventilador(request):
    """Controla ventilador - LIGAR ou DESLIGAR"""
    try:
        data = json.loads(request.body.decode('utf-8')) if isinstance(request.body, bytes) else request.data
        
        dispositivo_id = data.get('dispositivo_id')
        estado = data.get('estado')
        velocidade = data.get('velocidade', 100)  # 0-100
        
        if not dispositivo_id or estado not in ['ligar', 'desligar']:
            return Response({'error': 'dispositivo_id e estado são obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)
        
        comando = 'ligar_ventilador' if estado == 'ligar' else 'desligar_ventilador'
        parametros = {'velocidade': velocidade} if estado == 'ligar' else {}
        
        return enviar_comando_atuador_response(dispositivo_id, comando, parametros)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def enviar_comando_atuador_response(dispositivo_id, comando, parametros):
    """Helper para enviar comando e retornar resposta"""
    dispositivo = Dispositivo.objects.filter(dispositivo_id=dispositivo_id).first()
    if not dispositivo:
        return Response({'error': 'Dispositivo não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    cmd = ComandoAtuador.objects.create(
        dispositivo=dispositivo,
        comando=comando,
        parametros=parametros
    )
    
    try:
        enviar_comando_mqtt(dispositivo, comando, parametros)
        cmd.marcar_como_enviado()
        
        return Response({
            'success': True,
            'message': 'Comando executado',
            'comando_id': cmd.id
        }, status=status.HTTP_200_OK)
    except Exception as e:
        cmd.marcar_como_erro(str(e))
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _resolver_configuracao_mqtt(tenant=None):
    """Resolve broker MQTT a partir da URL completa ou dos campos antigos."""
    import os

    url_config = os.getenv('MQTT_BROKER_URL') or (tenant.mqtt_broker if tenant and tenant.mqtt_broker else '')

    if url_config:
        parsed = urlparse(url_config)
        if parsed.hostname:
            broker = parsed.hostname
            port = parsed.port or (8883 if parsed.scheme in ('mqtts', 'ssl') else 1883)
            username = parsed.username
            password = parsed.password
            return broker, port, username, password

    broker = os.getenv('MQTT_BROKER', 'localhost')
    port = int(os.getenv('MQTT_PORT', 1883))
    return broker, port, None, None


def enviar_comando_mqtt(dispositivo, comando, parametros):
    """Envia comando via MQTT"""
    tenant = getattr(dispositivo, 'tenant', None)
    BROKER, PORT, USERNAME, PASSWORD = _resolver_configuracao_mqtt(tenant)
    PREFIXO = tenant.mqtt_topic_prefix if tenant and tenant.mqtt_topic_prefix else 'estufa'
    TOPIC_COMANDO = f"{PREFIXO}/comando/{dispositivo.dispositivo_id}"

    client = mqtt.Client()
    if USERNAME:
        client.username_pw_set(USERNAME, PASSWORD)
    client.connect(BROKER, PORT, 60)
    
    payload = json.dumps({
        'comando': comando,
        'parametros': parametros,
        'timestamp': timezone.now().isoformat()
    })
    
    client.publish(TOPIC_COMANDO, payload, qos=1)
    client.disconnect()


# =============================
# HISTÓRICO E ESTATÍSTICAS
# =============================

@csrf_exempt
@require_http_methods(["GET"])
@api_view(['GET'])
def historico_sensores(request):
    """Retorna histórico de leituras de sensores"""
    try:
        sensor_id = request.GET.get('sensor_id')
        dispositivo_id = request.GET.get('dispositivo_id')
        dias = int(request.GET.get('dias', 7))
        limite = int(request.GET.get('limite', 100))
        
        data_inicio = timezone.now() - timedelta(days=dias)
        dados = SensorData.objects.filter(timestamp__gte=data_inicio)
        
        if sensor_id:
            dados = dados.filter(sensor_id=sensor_id)
        if dispositivo_id:
            dispositivo = Dispositivo.objects.filter(dispositivo_id=dispositivo_id).first()
            if dispositivo:
                dados = dados.filter(dispositivo=dispositivo)
        
        dados = dados.order_by('-timestamp')[:limite]
        
        resultado = []
        for leitura in dados:
            resultado.append({
                'id': leitura.id,
                'sensor_id': leitura.sensor_id,
                'dispositivo_id': leitura.dispositivo.dispositivo_id,
                'dispositivo_nome': leitura.dispositivo.nome,
                'temperatura': leitura.temperatura,
                'umidade': leitura.umidade,
                'luminosidade': leitura.luminosidade,
                'co2': leitura.co2,
                'timestamp': leitura.timestamp.isoformat(),
            })
        
        return Response({
            'success': True,
            'total': len(resultado),
            'dados': resultado
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@require_http_methods(["GET"])
@api_view(['GET'])
def stats_sensores(request):
    """Retorna estatísticas agregadas dos sensores"""
    try:
        dispositivo_id = request.GET.get('dispositivo_id')
        dias = int(request.GET.get('dias', 7))
        
        data_inicio = timezone.now() - timedelta(days=dias)
        dados = SensorData.objects.filter(timestamp__gte=data_inicio)
        
        if dispositivo_id:
            dispositivo = Dispositivo.objects.filter(dispositivo_id=dispositivo_id).first()
            if dispositivo:
                dados = dados.filter(dispositivo=dispositivo)
        
        if not dados.exists():
            return Response({
                'success': False,
                'error': 'Nenhum dado encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        temps = [d.temperatura for d in dados if d.temperatura]
        umids = [d.umidade for d in dados if d.umidade]
        lums = [d.luminosidade for d in dados if d.luminosidade]
        co2s = [d.co2 for d in dados if d.co2]
        
        stats = {}
        
        if temps:
            stats['temperatura'] = {
                'minima': min(temps),
                'maxima': max(temps),
                'media': sum(temps) / len(temps)
            }
        
        if umids:
            stats['umidade'] = {
                'minima': min(umids),
                'maxima': max(umids),
                'media': sum(umids) / len(umids)
            }
        
        if lums:
            stats['luminosidade'] = {
                'minima': min(lums),
                'maxima': max(lums),
                'media': sum(lums) / len(lums)
            }
        
        if co2s:
            stats['co2'] = {
                'minima': min(co2s),
                'maxima': max(co2s),
                'media': sum(co2s) / len(co2s)
            }
        
        return Response({
            'success': True,
            'periodo': {'data_inicio': data_inicio.isoformat(), 'dias': dias},
            'stats': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
