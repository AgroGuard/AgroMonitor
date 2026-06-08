import requests
from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone
from django.conf import settings
from .models import PrevisaoTempo, LocalidadeClima, AlertaClima, HistoricoClima
import logging

logger = logging.getLogger(__name__)


class OpenWeatherMapService:
    """Serviço para integração com OpenWeatherMap API"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key=None):
        """
        Inicializa o serviço com a chave da API
        
        Args:
            api_key: Chave da API OpenWeatherMap (padrão: variável OPENWEATHER_API_KEY)
        """
        self.api_key = api_key or getattr(settings, 'OPENWEATHER_API_KEY', None)
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY não configurada em settings.py")
    
    def obter_previsao_atual(self, latitude, longitude):
        """
        Obtém a previsão do tempo atual para coordenadas específicas
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            
        Returns:
            dict: Dados da previsão atual
        """
        try:
            url = f"{self.BASE_URL}/weather"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'lang': 'pt_br'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter previsão atual: {e}")
            return None
    
    def obter_previsao_5_dias(self, latitude, longitude):
        """
        Obtém previsão de 5 dias (a cada 3 horas)
        
        Args:
            latitude: Latitude da localidade
            longitude: Longitude da localidade
            
        Returns:
            dict: Dados da previsão para 5 dias
        """
        try:
            url = f"{self.BASE_URL}/forecast"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'pt_br'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter previsão de 5 dias: {e}")
            return None
    
    def processar_previsao_atual(self, localidade, dados):
        """
        Processa dados da API e cria/atualiza objeto PrevisaoTempo
        
        Args:
            localidade: Objeto LocalidadeClima
            dados: Dados retornados da API OpenWeatherMap
            
        Returns:
            PrevisaoTempo: Objeto criado ou atualizado
        """
        if not dados:
            return None
        
        try:
            # Mapear condições do tempo
            condicao_map = {
                'Clear': 'limpo',
                'Clouds': 'nublado',
                'Rain': 'chuvoso',
                'Drizzle': 'chuvoso',
                'Thunderstorm': 'tempestade',
                'Snow': 'neve',
                'Mist': 'neblina',
                'Smoke': 'neblina',
                'Haze': 'neblina',
                'Dust': 'neblina',
                'Fog': 'neblina',
                'Sand': 'neblina',
                'Ash': 'neblina',
                'Squall': 'tempestade',
                'Tornado': 'tempestade',
            }
            
            main_weather = dados['weather'][0]['main']
            condicao = condicao_map.get(main_weather, 'limpo')
            
            data_hora = datetime.fromtimestamp(dados['dt'], tz=dt_timezone.utc)
            
            previsao, created = PrevisaoTempo.objects.update_or_create(
                localidade=localidade,
                data_hora=data_hora,
                defaults={
                    'temperatura_minima': dados['main'].get('temp_min', 0),
                    'temperatura_maxima': dados['main'].get('temp_max', 0),
                    'temperatura_atual': dados['main']['temp'],
                    'sensacao_termica': dados['main'].get('feels_like'),
                    'umidade': dados['main']['humidity'],
                    'pressao': dados['main']['pressure'],
                    'velocidade_vento': dados['wind']['speed'],
                    'direcao_vento': dados['wind'].get('deg'),
                    'cobertura_nuvem': dados['clouds']['all'],
                    'chance_chuva': dados.get('pop', 0) * 100 if 'pop' in dados else 0,
                    'precipitacao': dados.get('rain', {}).get('1h'),
                    'condicao_tempo': condicao,
                    'descricao': dados['weather'][0]['description'],
                    'indice_uv': None,  # Não vem no endpoint atual
                    'visibilidade': dados.get('visibility'),
                    'fonte': 'openweathermap',
                }
            )
            
            return previsao
        except Exception as e:
            logger.error(f"Erro ao processar previsão: {e}")
            return None
    
    def processar_previsao_5_dias(self, localidade, dados):
        """
        Processa dados de previsão de 5 dias e salva múltiplos registros
        
        Args:
            localidade: Objeto LocalidadeClima
            dados: Dados retornados da API OpenWeatherMap
            
        Returns:
            list: Lista de PrevisaoTempo criadas/atualizadas
        """
        if not dados:
            return []
        
        previsoes = []
        for item in dados.get('list', []):
            previsao = self.processar_previsao_atual(localidade, item)
            if previsao:
                previsoes.append(previsao)
        
        return previsoes
    
    def verificar_alertas(self, localidade, previsao):
        """
        Verifica previsões e cria alertas para condições extremas
        
        Args:
            localidade: Objeto LocalidadeClima
            previsao: Objeto PrevisaoTempo
        """
        try:
            alertas_criados = []
            
            # Alerta de chuva forte (>20mm/h)
            if previsao.precipitacao and previsao.precipitacao > 20:
                alerta, created = AlertaClima.objects.get_or_create(
                    localidade=localidade,
                    previsao=previsao,
                    tipo_alerta='chuva_forte',
                    data_inicio=previsao.data_hora,
                    defaults={
                        'severidade': 'alta' if previsao.precipitacao > 50 else 'media',
                        'descricao': f"Chuva forte prevista: {previsao.precipitacao}mm/h",
                        'recomendacoes': "Proteja plantas sensíveis. Verifique drenagem de água.",
                        'ativo': True,
                    }
                )
                if created:
                    alertas_criados.append(alerta)
            
            # Alerta de vento forte (>15 m/s)
            if previsao.velocidade_vento > 15:
                alerta, created = AlertaClima.objects.get_or_create(
                    localidade=localidade,
                    previsao=previsao,
                    tipo_alerta='vento_forte',
                    data_inicio=previsao.data_hora,
                    defaults={
                        'severidade': 'alta' if previsao.velocidade_vento > 20 else 'media',
                        'descricao': f"Vento forte previsto: {previsao.velocidade_vento} m/s",
                        'recomendacoes': "Reforce estruturas de suporte. Reduza irrigação por aspersão.",
                        'ativo': True,
                    }
                )
                if created:
                    alertas_criados.append(alerta)
            
            # Alerta de calor extremo (>35°C)
            if previsao.temperatura_maxima > 35:
                alerta, created = AlertaClima.objects.get_or_create(
                    localidade=localidade,
                    previsao=previsao,
                    tipo_alerta='calor_extremo',
                    data_inicio=previsao.data_hora,
                    defaults={
                        'severidade': 'alta' if previsao.temperatura_maxima > 40 else 'media',
                        'descricao': f"Calor extremo previsto: {previsao.temperatura_maxima}°C",
                        'recomendacoes': "Aumente frequência de irrigação. Monitore plantas sensíveis.",
                        'ativo': True,
                    }
                )
                if created:
                    alertas_criados.append(alerta)
            
            # Alerta de frio extremo (<5°C)
            if previsao.temperatura_minima < 5:
                alerta, created = AlertaClima.objects.get_or_create(
                    localidade=localidade,
                    previsao=previsao,
                    tipo_alerta='frio_extremo',
                    data_inicio=previsao.data_hora,
                    defaults={
                        'severidade': 'alta' if previsao.temperatura_minima < 0 else 'media',
                        'descricao': f"Frio extremo previsto: {previsao.temperatura_minima}°C",
                        'recomendacoes': "Proteja plantas sensíveis. Verifique sistemas de aquecimento.",
                        'ativo': True,
                    }
                )
                if created:
                    alertas_criados.append(alerta)
            
            # Alerta de geada (<0°C)
            if previsao.temperatura_minima < 0:
                alerta, created = AlertaClima.objects.get_or_create(
                    localidade=localidade,
                    previsao=previsao,
                    tipo_alerta='geada',
                    data_inicio=previsao.data_hora,
                    defaults={
                        'severidade': 'critica',
                        'descricao': f"Geada prevista: {previsao.temperatura_minima}°C",
                        'recomendacoes': "Ative aquecimento. Realize irrigação preventiva se necessário.",
                        'ativo': True,
                    }
                )
                if created:
                    alertas_criados.append(alerta)
            
            return alertas_criados
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {e}")
            return []
    
    def atualizar_previsao_localidade(self, localidade):
        """
        Atualiza previsão atual e de 5 dias para uma localidade
        
        Args:
            localidade: Objeto LocalidadeClima
            
        Returns:
            dict: Resultado da atualização
        """
        resultado = {
            'sucesso': False,
            'previsao_atual': None,
            'previsoes_5_dias': [],
            'alertas': [],
            'erro': None
        }
        
        try:
            # Obter previsão atual
            dados_atual = self.obter_previsao_atual(localidade.latitude, localidade.longitude)
            if dados_atual:
                previsao = self.processar_previsao_atual(localidade, dados_atual)
                if previsao:
                    resultado['previsao_atual'] = previsao
                    # Verificar alertas para previsão atual
                    alertas = self.verificar_alertas(localidade, previsao)
                    resultado['alertas'].extend(alertas)
            
            # Obter previsão de 5 dias
            dados_5_dias = self.obter_previsao_5_dias(localidade.latitude, localidade.longitude)
            if dados_5_dias:
                previsoes = self.processar_previsao_5_dias(localidade, dados_5_dias)
                resultado['previsoes_5_dias'] = previsoes
                # Verificar alertas para cada previsão
                for previsao in previsoes:
                    alertas = self.verificar_alertas(localidade, previsao)
                    resultado['alertas'].extend(alertas)
            
            resultado['sucesso'] = bool(resultado['previsao_atual'] or resultado['previsoes_5_dias'])
            
        except Exception as e:
            logger.error(f"Erro ao atualizar previsão para {localidade.nome}: {e}")
            resultado['erro'] = str(e)
        
        return resultado
    
    def atualizar_todas_localidades(self):
        """
        Atualiza previsões para todas as localidades ativas
        
        Returns:
            dict: Resultado da atualização
        """
        localidades = LocalidadeClima.objects.filter(ativa=True)
        resultados = []
        
        for localidade in localidades:
            resultado = self.atualizar_previsao_localidade(localidade)
            resultados.append({
                'localidade': localidade.nome,
                'resultado': resultado
            })
        
        return resultados
