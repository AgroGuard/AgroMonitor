from django.test import TestCase
from django.utils import timezone
from .models import LocalidadeClima, PrevisaoTempo, AlertaClima, HistoricoClima


class LocalidadeClimaTestCase(TestCase):
    
    def setUp(self):
        self.localidade = LocalidadeClima.objects.create(
            nome='São Paulo',
            latitude=-23.5505,
            longitude=-46.6333,
            pais='Brasil',
            estado='SP'
        )
    
    def test_criar_localidade(self):
        self.assertEqual(self.localidade.nome, 'São Paulo')
        self.assertTrue(self.localidade.ativa)
    
    def test_localidade_str(self):
        expected_str = f"São Paulo (-23.5505, -46.6333)"
        self.assertEqual(str(self.localidade), expected_str)


class PrevisaoTempoTestCase(TestCase):
    
    def setUp(self):
        self.localidade = LocalidadeClima.objects.create(
            nome='Teste',
            latitude=0,
            longitude=0
        )
        self.previsao = PrevisaoTempo.objects.create(
            localidade=self.localidade,
            data_hora=timezone.now(),
            temperatura_minima=20,
            temperatura_maxima=30,
            temperatura_atual=25,
            umidade=70,
            pressao=1013,
            velocidade_vento=5,
            cobertura_nuvem=50,
            condicao_tempo='limpo'
        )
    
    def test_criar_previsao(self):
        self.assertEqual(self.previsao.temperatura_atual, 25)
        self.assertEqual(self.previsao.condicao_tempo, 'limpo')
    
    def test_previsao_str(self):
        expected = f"Teste - {self.previsao.data_hora} - limpo"
        self.assertEqual(str(self.previsao), expected)


class AlertaClimaTestCase(TestCase):
    
    def setUp(self):
        self.localidade = LocalidadeClima.objects.create(
            nome='Teste',
            latitude=0,
            longitude=0
        )
        self.alerta = AlertaClima.objects.create(
            localidade=self.localidade,
            tipo_alerta='chuva_forte',
            severidade='alta',
            descricao='Chuva forte prevista',
            data_inicio=timezone.now()
        )
    
    def test_criar_alerta(self):
        self.assertEqual(self.alerta.tipo_alerta, 'chuva_forte')
        self.assertTrue(self.alerta.ativo)
    
    def test_alerta_str(self):
        expected = f"Teste - chuva_forte (alta)"
        self.assertEqual(str(self.alerta), expected)
