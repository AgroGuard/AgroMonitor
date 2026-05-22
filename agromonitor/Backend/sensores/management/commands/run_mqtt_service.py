from django.core.management.base import BaseCommand
import os
import json
import django
from django.utils import timezone
from sensores.models import Dispositivo, SensorData, RegraAutomacao, ComandoAtuador
from Monitor.models import AlertaSistema
import paho.mqtt.client as mqtt
import time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Inicia o serviço MQTT para receber dados de sensores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--broker',
            type=str,
            default='localhost',
            help='Endereço do broker MQTT'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=1883,
            help='Porta do broker MQTT'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Ativar modo debug'
        )

    def handle(self, *args, **options):
        broker = os.getenv('MQTT_BROKER', options['broker'])
        port = int(os.getenv('MQTT_PORT', options['port']))
        debug = options['debug']

        self.stdout.write(f"Iniciando serviço MQTT...")
        self.stdout.write(f"Broker: {broker}:{port}")
        
        mqtt_service = MQTTService(broker, port, debug)
        mqtt_service.start()


class MQTTService:
    """Serviço MQTT para receber dados de sensores e controlar atuadores"""

    def __init__(self, broker='localhost', port=1883, debug=False):
        self.broker = broker
        self.port = port
        self.debug = debug
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, userdata, flags, rc):
        """Callback quando conecta ao broker"""
        if rc == 0:
            print(f"[✓] Conectado ao MQTT broker ({self.broker}:{self.port})")
            # Se inscrever em todos os tópicos de sensores
            client.subscribe("estufa/sensores/#")
            client.subscribe("estufa/comando/response/#")
            client.subscribe("estufa/status/#")
        else:
            print(f"[✗] Erro ao conectar: código {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback quando desconecta do broker"""
        if rc != 0:
            print(f"[!] Desconexão inesperada. Reconectando...")
            time.sleep(5)
            client.reconnect()

    def on_message(self, client, userdata, msg):
        """Callback quando recebe mensagem MQTT"""
        try:
            if self.debug:
                print(f"[MQTT] Tópico: {msg.topic}")
                print(f"[MQTT] Payload: {msg.payload.decode()}")

            # Processar mensagens de sensores
            if msg.topic.startswith("estufa/sensores/"):
                self.processar_leitura_sensor(msg)
            
            # Processar respostas de comandos
            elif msg.topic.startswith("estufa/comando/response/"):
                self.processar_resposta_comando(msg)
            
            # Processar status dos dispositivos
            elif msg.topic.startswith("estufa/status/"):
                self.processar_status_dispositivo(msg)

        except Exception as e:
            print(f"[✗] Erro ao processar mensagem: {e}")

    def processar_leitura_sensor(self, msg):
        """Processa leitura de sensor"""
        try:
            data = json.loads(msg.payload.decode())
            dispositivo_id = data.get('sensor_id') or data.get('dispositivo_id')
            
            if not dispositivo_id:
                print("[!] Dispositivo ID não encontrado na mensagem")
                return

            # Buscar ou criar dispositivo
            dispositivo, criado = Dispositivo.objects.get_or_create(
                dispositivo_id=dispositivo_id,
                defaults={
                    'nome': f'Sensor {dispositivo_id}',
                    'tipo': 'sensor_temp',
                }
            )

            # Atualizar status online
            dispositivo.online = True
            dispositivo.ultima_comunicacao = timezone.now()
            dispositivo.bateria = data.get('bateria')
            dispositivo.save()

            # Criar leitura
            leitura = SensorData.objects.create(
                dispositivo=dispositivo,
                sensor_id=dispositivo_id,
                temperatura=data.get('temperatura'),
                umidade=data.get('umidade'),
                luminosidade=data.get('luminosidade'),
                co2=data.get('co2'),
            )

            print(f"[✓] Leitura gravada: {dispositivo.nome} - Temp: {leitura.temperatura}°C, Umidade: {leitura.umidade}%")

            # Verificar regras de automação
            self.verificar_regras_automacao(dispositivo, leitura)

            # Verificar alertas críticos
            self.verificar_alertas_criticos(dispositivo, leitura)

        except json.JSONDecodeError:
            print("[!] Erro ao decodificar JSON da mensagem MQTT")
        except Exception as e:
            print(f"[✗] Erro ao processar leitura de sensor: {e}")

    def processar_resposta_comando(self, msg):
        """Processa resposta de comando executado"""
        try:
            data = json.loads(msg.payload.decode())
            dispositivo_id = data.get('dispositivo_id')
            comando_id = data.get('comando_id')
            sucesso = data.get('sucesso', False)

            if comando_id:
                comando = ComandoAtuador.objects.filter(id=comando_id).first()
                if comando:
                    if sucesso:
                        comando.marcar_como_executado()
                        print(f"[✓] Comando executado: {comando.dispositivo.nome}")
                    else:
                        erro = data.get('erro', 'Erro desconhecido')
                        comando.marcar_como_erro(erro)
                        print(f"[✗] Comando falhou: {erro}")

        except json.JSONDecodeError:
            print("[!] Erro ao decodificar resposta de comando")
        except Exception as e:
            print(f"[✗] Erro ao processar resposta de comando: {e}")

    def processar_status_dispositivo(self, msg):
        """Processa status de dispositivo (online/offline)"""
        try:
            data = json.loads(msg.payload.decode())
            dispositivo_id = data.get('dispositivo_id')
            online = data.get('online', True)

            dispositivo = Dispositivo.objects.filter(dispositivo_id=dispositivo_id).first()
            if dispositivo:
                dispositivo.online = online
                dispositivo.ultima_comunicacao = timezone.now()
                dispositivo.save()
                status_str = "online" if online else "offline"
                print(f"[●] Status: {dispositivo.nome} - {status_str}")

        except Exception as e:
            print(f"[✗] Erro ao processar status: {e}")

    def verificar_regras_automacao(self, dispositivo, leitura):
        """Verifica e executa regras de automação"""
        try:
            regras = RegraAutomacao.objects.filter(
                sensor=dispositivo,
                ativa=True
            )

            for regra in regras:
                if not regra.pode_executar():
                    continue

                deve_executar = False
                valor = None

                # Determinar o valor baseado na condição
                if 'temperatura' in regra.condicao:
                    valor = leitura.temperatura
                elif 'umidade' in regra.condicao:
                    valor = leitura.umidade
                elif 'luminosidade' in regra.condicao:
                    valor = leitura.luminosidade

                # Verificar se condição foi atendida
                if valor is not None:
                    if 'maior' in regra.condicao:
                        deve_executar = valor > regra.valor_limite
                    elif 'menor' in regra.condicao:
                        deve_executar = valor < regra.valor_limite

                # Executar ação se condição atendida
                if deve_executar:
                    self.executar_acao_automacao(regra)

        except Exception as e:
            print(f"[✗] Erro ao verificar regras: {e}")

    def executar_acao_automacao(self, regra):
        """Executa ação de automação"""
        try:
            if regra.acao == 'alerta':
                AlertaSistema.objects.get_or_create(
                    titulo=f"Automação: {regra.nome}",
                    defaults={
                        'mensagem': regra.descricao,
                        'nivel': 'warning',
                        'resolvido': False,
                    }
                )
            else:
                # Enviar comando para atuador
                if regra.atuador:
                    ComandoAtuador.objects.create(
                        dispositivo=regra.atuador,
                        comando=regra.acao,
                        parametros={}
                    )

            regra.ultima_execucao = timezone.now()
            regra.save()
            print(f"[✓] Ação automática executada: {regra.nome}")

        except Exception as e:
            print(f"[✗] Erro ao executar ação: {e}")

    def verificar_alertas_criticos(self, dispositivo, leitura):
        """Verifica e gera alertas para condições críticas"""
        try:
            # Alerta de temperatura muito alta
            if leitura.temperatura and leitura.temperatura > 40:
                AlertaSistema.objects.get_or_create(
                    titulo=f"🔴 TEMPERATURA CRÍTICA em {dispositivo.nome}",
                    defaults={
                        'mensagem': f"Temperatura de {leitura.temperatura}°C detectada. Valor crítico!",
                        'nivel': 'critical',
                        'resolvido': False,
                    }
                )

            # Alerta de temperatura muito baixa
            elif leitura.temperatura and leitura.temperatura < 5:
                AlertaSistema.objects.get_or_create(
                    titulo=f"🔵 TEMPERATURA MUITO BAIXA em {dispositivo.nome}",
                    defaults={
                        'mensagem': f"Temperatura de {leitura.temperatura}°C detectada. Muito baixa!",
                        'nivel': 'warning',
                        'resolvido': False,
                    }
                )

            # Alerta de umidade muito alta
            if leitura.umidade and leitura.umidade > 95:
                AlertaSistema.objects.get_or_create(
                    titulo=f"💧 UMIDADE CRÍTICA em {dispositivo.nome}",
                    defaults={
                        'mensagem': f"Umidade de {leitura.umidade}% detectada. Risco de mofo!",
                        'nivel': 'warning',
                        'resolvido': False,
                    }
                )

        except Exception as e:
            print(f"[!] Erro ao gerar alerta crítico: {e}")

    def start(self):
        """Inicia o serviço MQTT"""
        try:
            self.client.connect(self.broker, self.port, 60)
            print("[*] Iniciando loop de mensagens...")
            self.client.loop_forever()
        except Exception as e:
            print(f"[✗] Erro ao iniciar serviço: {e}")
            print("[*] Tentando reconectar em 5 segundos...")
            time.sleep(5)
            self.start()
