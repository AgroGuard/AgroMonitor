import pytest
from django.utils import timezone
from datetime import timedelta
from Clima.serializers import (
    LocalidadeClimaSerializer,
    PrevisaoTempoSerializer,
    AlertaClimaSerializer,
    HistoricoClimaSerializer,
    NotaUsuarioSerializer,
)
from Clima.models import LocalidadeClima, PrevisaoTempo, AlertaClima, HistoricoClima


@pytest.fixture
def localidade(db):
    return LocalidadeClima.objects.create(
        nome="Campinas",
        latitude=-22.9099,
        longitude=-47.0626,
        pais="BR",
        estado="SP",
        ativa=True,
        fazenda_id=1,
    )


@pytest.fixture
def previsao(db, localidade):
    return PrevisaoTempo.objects.create(
        localidade=localidade,
        data_hora=timezone.now(),
        temperatura_minima=18.0,
        temperatura_maxima=30.0,
        temperatura_atual=25.5,
        sensacao_termica=27.0,
        umidade=65,
        pressao=1013,
        velocidade_vento=12.0,
        chance_chuva=20.0,
        condicao_tempo="nublado",
        fonte="openweathermap",
    )




class TestLocalidadeClimaSerializer:

    def test_serializa_campos_obrigatorios(self, localidade):
        s = LocalidadeClimaSerializer(localidade)
        data = s.data
        assert data["nome"] == "Campinas"
        assert data["latitude"] == pytest.approx(-22.9099, rel=1e-3)
        assert data["longitude"] == pytest.approx(-47.0626, rel=1e-3)
        assert data["pais"] == "BR"
        assert data["ativa"] is True

    def test_campos_readonly_presentes(self, localidade):
        s = LocalidadeClimaSerializer(localidade)
        assert "id" in s.data
        assert "criada_em" in s.data
        assert "atualizada_em" in s.data

    def test_desserializa_dados_validos(self, db):
        data = {
            "nome": "São Paulo",
            "latitude": -23.5505,
            "longitude": -46.6333,
            "pais": "BR",
            "estado": "SP",
            "ativa": True,
            "fazenda_id": 2,
        }
        s = LocalidadeClimaSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_rejeita_dado_sem_nome(self, db):
        data = {
            "latitude": -23.5505,
            "longitude": -46.6333,
        }
        s = LocalidadeClimaSerializer(data=data)
        assert not s.is_valid()
        assert "nome" in s.errors


class TestPrevisaoTempoSerializer:

    def test_serializa_previsao(self, previsao):
        s = PrevisaoTempoSerializer(previsao)
        data = s.data
        assert data["temperatura_atual"] == pytest.approx(25.5)
        assert data["umidade"] == 65
        assert data["fonte"] == "openweathermap"

    def test_campo_localidade_nome_presente(self, previsao):
        s = PrevisaoTempoSerializer(previsao)
        assert s.data["localidade_nome"] == "Campinas"

    def test_campo_id_readonly(self, previsao):
        s = PrevisaoTempoSerializer(previsao)
        assert "id" in s.data



class TestAlertaClimaSerializer:

    def test_serializa_alerta(self, db, localidade, previsao):
        alerta = AlertaClima.objects.create(
            localidade=localidade,
            previsao=previsao,
            tipo_alerta="chuva_intensa",
            severidade="alta",
            descricao="Chuva intensa prevista",
            ativo=True,
            data_inicio=timezone.now(),
        )
        s = AlertaClimaSerializer(alerta)
        data = s.data
        assert data["tipo_alerta"] == "chuva_intensa"
        assert data["severidade"] == "alta"
        assert data["localidade_nome"] == "Campinas"

    def test_campo_previsao_data_presente(self, db, localidade, previsao):
        alerta = AlertaClima.objects.create(
            localidade=localidade,
            previsao=previsao,
            tipo_alerta="granizo",
            severidade="critica",
            descricao="Granizo",
            ativo=True,
            data_inicio=timezone.now(),
        )
        s = AlertaClimaSerializer(alerta)
        assert "previsao_data" in s.data
        assert s.data["previsao_data"] is not None

    def test_campo_previsao_data_none_quando_sem_previsao(self, db, localidade):
        alerta = AlertaClima.objects.create(
            localidade=localidade,
            previsao=None,
            tipo_alerta="vento_forte",
            severidade="media",
            descricao="Vento forte",
            ativo=True,
            data_inicio=timezone.now(),
        )
        s = AlertaClimaSerializer(alerta)
        assert s.data["previsao_data"] is None



class TestHistoricoClimaSerializer:

    def test_serializa_historico(self, db, localidade):
        historico = HistoricoClima.objects.create(
            localidade=localidade,
            data=timezone.now().date(),
            temperatura_minima=15.0,
            temperatura_maxima=28.0,
            temperatura_media=21.5,
            umidade_media=70.0,
            precipitacao_total=5.0,
        )
        s = HistoricoClimaSerializer(historico)
        data = s.data
        assert data["temperatura_media"] == pytest.approx(21.5)
        assert data["localidade_nome"] == "Campinas"

    def test_campos_obrigatorios_presentes(self, db, localidade):
        historico = HistoricoClima.objects.create(
            localidade=localidade,
            data=timezone.now().date(),
            temperatura_minima=10.0,
            temperatura_maxima=25.0,
            temperatura_media=17.5,
        )
        s = HistoricoClimaSerializer(historico)
        for campo in ["id", "localidade", "data", "temperatura_minima", "temperatura_maxima"]:
            assert campo in s.data



class TestNotaUsuarioSerializer:

    def test_desserializa_nota_valida(self):
        data = {"texto": "Verificar irrigação da estufa 2"}
        s = NotaUsuarioSerializer(data=data)
        assert s.is_valid(), s.errors

    def test_rejeita_nota_sem_texto(self):
        s = NotaUsuarioSerializer(data={})
        assert not s.is_valid()
        assert "texto" in s.errors
