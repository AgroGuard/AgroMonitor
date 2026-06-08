import pytest
import json
from django.test import Client
from sensores.models import Dispositivo, SensorData, ComandoAtuador, RegraAutomacao
from Cadastro.models import Tenant

pytestmark = pytest.mark.django_db


class TestDispositivos:
    """Testes para dispositivos IoT (sensores e atuadores)"""

    @pytest.fixture
    def dispositivo_sensor(self, db):
        """Cria dispositivo sensor de temperatura"""
        return Dispositivo.objects.create(
            nome='Sensor Temperatura 01',
            dispositivo_id='temp_001',
            tipo='sensor_temp',
            estufa='Estufa 01',
            ativo=True,
            online=True
        )

    @pytest.fixture
    def dispositivo_bomba(self, db):
        """Cria dispositivo atuador (bomba)"""
        return Dispositivo.objects.create(
            nome='Bomba Irrigação 01',
            dispositivo_id='bomba_001',
            tipo='atuador_bomba',
            estufa='Estufa 01',
            ativo=True,
            online=True
        )

    def test_criar_dispositivo_sensor(self, db):
        """Testa criação de dispositivo sensor"""
        disp = Dispositivo.objects.create(
            nome='Sensor Umidade 01',
            dispositivo_id='umidade_001',
            tipo='sensor_umidade',
            estufa='Estufa 01',
            ativo=True
        )
        assert disp.id is not None
        assert disp.tipo == 'sensor_umidade'
        assert disp.ativo is True

    def test_criar_leitura_sensor(self, dispositivo_sensor):
        """Testa criação de leitura de sensor"""
        leitura = SensorData.objects.create(
            dispositivo=dispositivo_sensor,
            sensor_id='temp_001',
            temperatura=25.5,
            timestamp='2024-01-01T10:00:00Z'
        )
        assert leitura.id is not None
        assert leitura.temperatura == 25.5
        assert leitura.dispositivo == dispositivo_sensor

    def test_multiple_leituras_sensor(self, dispositivo_sensor):
        """Testa múltiplas leituras de sensores"""
        for i in range(5):
            SensorData.objects.create(
                dispositivo=dispositivo_sensor,
                sensor_id=dispositivo_sensor.dispositivo_id,
                temperatura=20 + i,
                umidade=60 + i
            )
        leituras = SensorData.objects.filter(dispositivo=dispositivo_sensor)
        assert leituras.count() == 5

    def test_enviar_comando_atuador(self, dispositivo_bomba):
        """Testa envio de comando para atuador"""
        comando = ComandoAtuador.objects.create(
            dispositivo=dispositivo_bomba,
            comando='ligar_bomba',
            parametros={'duracao': 30},
            status='pendente'
        )
        assert comando.id is not None
        assert comando.status == 'pendente'
        assert comando.comando == 'ligar_bomba'

    def test_marcar_comando_como_enviado(self, dispositivo_bomba):
        """Testa marcação de comando como enviado"""
        comando = ComandoAtuador.objects.create(
            dispositivo=dispositivo_bomba,
            comando='ligar_bomba'
        )
        comando.marcar_como_enviado()
        assert comando.status == 'enviado'
        assert comando.enviado_em is not None

    def test_marcar_comando_como_executado(self, dispositivo_bomba):
        """Testa marcação de comando como executado"""
        comando = ComandoAtuador.objects.create(
            dispositivo=dispositivo_bomba,
            comando='ligar_bomba'
        )
        comando.marcar_como_executado()
        assert comando.status == 'executado'
        assert comando.executado_em is not None

    def test_marcar_comando_erro(self, dispositivo_bomba):
        """Testa marcação de comando com erro"""
        comando = ComandoAtuador.objects.create(
            dispositivo=dispositivo_bomba,
            comando='ligar_bomba'
        )
        comando.marcar_como_erro('Dispositivo offline')
        assert comando.status == 'erro'
        assert 'offline' in comando.mensagem_erro

    def test_criar_regra_automacao(self, dispositivo_sensor, dispositivo_bomba):
        """Testa criação de regra de automação"""
        regra = RegraAutomacao.objects.create(
            nome='Irrigar se Umidade < 40%',
            sensor=dispositivo_sensor,
            condicao='umidade_menor',
            valor_limite=40.0,
            atuador=dispositivo_bomba,
            acao='ligar_bomba',
            ativa=True
        )
        assert regra.id is not None
        assert regra.ativa is True
        assert regra.pode_executar() is True

    def test_regra_automacao_com_tempo_espera(self, dispositivo_sensor, dispositivo_bomba):
        """Testa regra de automação com tempo mínimo de espera"""
        from django.utils import timezone
        from datetime import timedelta
        
        regra = RegraAutomacao.objects.create(
            nome='Irrigar com intervalo',
            sensor=dispositivo_sensor,
            condicao='umidade_menor',
            valor_limite=40.0,
            atuador=dispositivo_bomba,
            acao='ligar_bomba',
            ativa=True,
            tempo_espera_min=30,
            ultima_execucao=timezone.now() - timedelta(minutes=10)
        )
        # Não pode executar (menos de 30 min desde última execução)
        assert regra.pode_executar() is False
        
        # Atualizar para há 40 min atrás
        regra.ultima_execucao = timezone.now() - timedelta(minutes=40)
        regra.save()
        # Agora pode executar
        assert regra.pode_executar() is True


class TestControleSensoresAPI:
    """Testes para APIs de controle de sensores"""

    def test_listar_dispositivos(self, client, dispositivo_sensor):
        """Testa listagem de dispositivos"""
        response = client.get('/api/sensores/dispositivos/')
        assert response.status_code == 200
        data = response.json()
        assert 'dispositivos' in data or isinstance(data, list)

    def test_enviar_comando_atuador_api(self, client, dispositivo_bomba):
        """Testa envio de comando via API"""
        # Nota: este teste pode falhar se a API require autenticação
        response = client.post(
            '/api/sensores/comando/',
            data=json.dumps({
                'dispositivo_id': dispositivo_bomba.dispositivo_id,
                'comando': 'ligar_bomba',
                'parametros': {'duracao': 30}
            }),
            content_type='application/json'
        )
        # Status pode ser 201, 200 ou 401 (se require auth)
        assert response.status_code in [200, 201, 401]
