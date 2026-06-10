import pytest
from django.test import Client
from Clima.models import LocalidadeClima, PrevisaoTempo, AlertaClima
from Clima.services import OpenWeatherMapService

pytestmark = pytest.mark.django_db


class TestClima:
    """Testes para funcionalidade de clima"""

    @pytest.fixture
    def localidade(self):
        """Cria localidade de teste"""
        return LocalidadeClima.objects.create(
            nome='São Paulo',
            latitude=-23.5505,
            longitude=-46.6333,
            estado='SP',
            pais='Brasil',
            ativa=True
        )

    def test_criar_localidade_clima(self, db):
        """Testa criação de localidade de clima"""
        localidade = LocalidadeClima.objects.create(
            nome='Rio de Janeiro',
            latitude=-22.9068,
            longitude=-43.1729,
            estado='RJ',
            pais='Brasil',
            ativa=True
        )
        assert localidade.id is not None
        assert localidade.nome == 'Rio de Janeiro'
        assert localidade.ativa is True

    def test_listar_localidades_ativas(self, localidade):
        """Testa listagem de localidades ativas"""
        LocalidadeClima.objects.create(
            nome='Inativa',
            latitude=0,
            longitude=0,
            ativa=False
        )
        ativas = LocalidadeClima.objects.filter(ativa=True)
        assert ativas.count() == 1
        assert ativas.first().nome == 'São Paulo'

    def test_criar_previsao_tempo(self, localidade):
        """Testa criação de previsão de tempo"""
        from django.utils import timezone
        previsao = PrevisaoTempo.objects.create(
            localidade=localidade,
            data_hora=timezone.now(),
            temperatura_atual=25.5,
            umidade=70,
            condicao_tempo='limpo',
            descricao='Céu limpo',
            fonte='openweathermap'
        )
        assert previsao.id is not None
        assert previsao.temperatura_atual == 25.5
        assert previsao.umidade == 70

    def test_alerta_calor_extremo(self, localidade):
        """Testa criação de alerta de calor extremo"""
        from django.utils import timezone
        previsao = PrevisaoTempo.objects.create(
            localidade=localidade,
            data_hora=timezone.now(),
            temperatura_maxima=38.0,
            temperatura_minima=30.0,
            temperatura_atual=38.0,
            umidade=60,
            condicao_tempo='limpo',
            descricao='Calor extremo',
            fonte='test'
        )
        alerta = AlertaClima.objects.create(
            localidade=localidade,
            previsao=previsao,
            tipo_alerta='calor_extremo',
            severidade='alta',
            descricao='Calor extremo previsto: 38.0°C',
            ativo=True
        )
        assert alerta.id is not None
        assert alerta.tipo_alerta == 'calor_extremo'
        assert alerta.severidade == 'alta'

    def test_alerta_chuva_forte(self, localidade):
        """Testa criação de alerta de chuva forte"""
        from django.utils import timezone
        previsao = PrevisaoTempo.objects.create(
            localidade=localidade,
            data_hora=timezone.now(),
            precipitacao=25.0,
            temperatura_atual=20.0,
            umidade=90,
            condicao_tempo='chuvoso',
            descricao='Chuva forte',
            fonte='test'
        )
        alerta = AlertaClima.objects.create(
            localidade=localidade,
            previsao=previsao,
            tipo_alerta='chuva_forte',
            severidade='media',
            descricao='Chuva forte prevista: 25.0mm/h',
            ativo=True
        )
        assert alerta.tipo_alerta == 'chuva_forte'

    def test_desativar_alerta(self, localidade):
        """Testa desativação de alerta"""
        from django.utils import timezone
        previsao = PrevisaoTempo.objects.create(
            localidade=localidade,
            data_hora=timezone.now(),
            temperatura_atual=20.0,
            umidade=70,
            condicao_tempo='limpo',
            fonte='test'
        )
        alerta = AlertaClima.objects.create(
            localidade=localidade,
            previsao=previsao,
            tipo_alerta='teste',
            ativo=True
        )
        alerta.ativo = False
        alerta.data_fim = timezone.now()
        alerta.save()
        
        alerta_atualizado = AlertaClima.objects.get(id=alerta.id)
        assert alerta_atualizado.ativo is False
        assert alerta_atualizado.data_fim is not None
