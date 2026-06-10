import json
from unittest.mock import patch

from django.test import TestCase, Client
from django.utils import timezone
from django.conf import settings
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


class ClimaApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.localidade = LocalidadeClima.objects.create(
            nome='Região Teste',
            latitude=-23.0,
            longitude=-46.0,
            pais='Brasil',
            estado='SP'
        )

    def test_listar_regioes_retorna_regiao_ativa(self):
        response = self.client.get('/api/clima/api/regioes/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['sucesso'])
        self.assertEqual(len(data['regioes']), 1)
        self.assertEqual(data['regioes'][0]['nome'], 'Região Teste')

    def test_cadastrar_regiao_cria_e_retorna_com_sucesso(self):
        payload = {
            'nome': 'Nova Região',
            'latitude': -22.9,
            'longitude': -46.1,
            'estado': 'SP',
            'pais': 'Brasil',
            'fazenda_id': 'fazenda-principal'
        }
        response = self.client.post(
            '/api/clima/api/regioes/cadastrar/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['sucesso'])
        self.assertEqual(data['regiao']['nome'], 'Nova Região')
        self.assertEqual(LocalidadeClima.objects.filter(nome='Nova Região').count(), 1)

    def test_resumo_clima_retorna_previsao_atual_nula_quando_nao_tem_previsao(self):
        response = self.client.get('/api/clima/api/resumo/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['sucesso'])
        self.assertEqual(data['total_localidades'], 1)
        self.assertIsNone(data['localidades'][0]['previsao_atual'])

    @patch('Clima.views.OpenWeatherMapService')
    def test_sincronizar_clima_retorna_sucesso_quando_servico_trabalha(self, mock_service_class):
        mock_service = mock_service_class.return_value
        mock_service.atualizar_todas_localidades.return_value = [
            {'localidade': 'Região Teste', 'resultado': {'sucesso': True}}
        ]

        response = self.client.post('/api/clima/api/sincronizar/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['sucesso'])
        self.assertEqual(data['sucessos'], 1)
        self.assertEqual(data['erros'], 0)
