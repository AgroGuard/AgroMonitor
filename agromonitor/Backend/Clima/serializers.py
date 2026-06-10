from rest_framework import serializers
from .models import LocalidadeClima, PrevisaoTempo, AlertaClima, HistoricoClima, NotaUsuario


class LocalidadeClimaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalidadeClima
        fields = [
            'id', 'nome', 'latitude', 'longitude', 'pais', 'estado',
            'clima_tag',
            'ativa', 'fazenda_id', 'criada_em', 'atualizada_em'
        ]
        read_only_fields = ['id', 'criada_em', 'atualizada_em']


class PrevisaoTempoSerializer(serializers.ModelSerializer):
    localidade_nome = serializers.CharField(source='localidade.nome', read_only=True)
    
    class Meta:
        model = PrevisaoTempo
        fields = [
            'id', 'localidade', 'localidade_nome', 'data_hora',
            'temperatura_minima', 'temperatura_maxima', 'temperatura_atual',
            'sensacao_termica', 'umidade', 'pressao',
            'velocidade_vento', 'direcao_vento', 'cobertura_nuvem',
            'chance_chuva', 'precipitacao', 'condicao_tempo', 'descricao',
            'indice_uv', 'visibilidade', 'fonte', 'data_requisicao'
        ]
        read_only_fields = ['id', 'data_requisicao']


class AlertaClimaSerializer(serializers.ModelSerializer):
    localidade_nome = serializers.CharField(source='localidade.nome', read_only=True)
    previsao_data = serializers.SerializerMethodField()
    
    class Meta:
        model = AlertaClima
        fields = [
            'id', 'localidade', 'localidade_nome', 'previsao', 'previsao_data',
            'tipo_alerta', 'severidade', 'descricao', 'recomendacoes',
            'ativo', 'data_inicio', 'data_fim', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']
    
    def get_previsao_data(self, obj):
        if obj.previsao:
            return obj.previsao.data_hora
        return None


class HistoricoClimaSerializer(serializers.ModelSerializer):
    localidade_nome = serializers.CharField(source='localidade.nome', read_only=True)
    
    class Meta:
        model = HistoricoClima
        fields = [
            'id', 'localidade', 'localidade_nome', 'data',
            'temperatura_minima', 'temperatura_maxima', 'temperatura_media',
            'umidade_media', 'precipitacao_total', 'velocidade_vento_media',
            'criado_em'
        ]
        read_only_fields = ['id', 'criado_em']


class NotaUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaUsuario
        fields = ['id', 'texto', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']
