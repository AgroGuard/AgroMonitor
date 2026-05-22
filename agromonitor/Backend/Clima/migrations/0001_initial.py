from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LocalidadeClima',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='Nome da Localidade')),
                ('latitude', models.FloatField(verbose_name='Latitude')),
                ('longitude', models.FloatField(verbose_name='Longitude')),
                ('pais', models.CharField(blank=True, max_length=100, verbose_name='País')),
                ('estado', models.CharField(blank=True, max_length=100, verbose_name='Estado/Província')),
                ('ativa', models.BooleanField(default=True, verbose_name='Ativa')),
                ('fazenda_id', models.CharField(blank=True, max_length=100, verbose_name='ID da Fazenda')),
                ('criada_em', models.DateTimeField(auto_now_add=True, verbose_name='Criada em')),
                ('atualizada_em', models.DateTimeField(auto_now=True, verbose_name='Atualizada em')),
            ],
            options={
                'verbose_name': 'Localidade de Clima',
                'verbose_name_plural': 'Localidades de Clima',
                'ordering': ['nome'],
                'unique_together': {('latitude', 'longitude')},
            },
        ),
        migrations.CreateModel(
            name='PrevisaoTempo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_hora', models.DateTimeField(verbose_name='Data e Hora da Previsão')),
                ('temperatura_minima', models.FloatField(verbose_name='Temperatura Mínima (°C)')),
                ('temperatura_maxima', models.FloatField(verbose_name='Temperatura Máxima (°C)')),
                ('temperatura_atual', models.FloatField(verbose_name='Temperatura Atual (°C)')),
                ('sensacao_termica', models.FloatField(blank=True, null=True, verbose_name='Sensação Térmica (°C)')),
                ('umidade', models.IntegerField(verbose_name='Umidade (%)')),
                ('pressao', models.IntegerField(verbose_name='Pressão (hPa)')),
                ('velocidade_vento', models.FloatField(verbose_name='Velocidade do Vento (m/s)')),
                ('direcao_vento', models.IntegerField(blank=True, null=True, verbose_name='Direção do Vento (graus)')),
                ('cobertura_nuvem', models.IntegerField(verbose_name='Cobertura de Nuvem (%)')),
                ('chance_chuva', models.IntegerField(default=0, verbose_name='Chance de Chuva (%)')),
                ('precipitacao', models.FloatField(blank=True, null=True, verbose_name='Precipitação (mm)')),
                ('condicao_tempo', models.CharField(choices=[('limpo', 'Céu Limpo'), ('nublado', 'Nublado'), ('nuvem_leve', 'Poucas Nuvens'), ('chuvoso', 'Chuvoso'), ('tempestade', 'Tempestade'), ('neve', 'Neve'), ('neblina', 'Neblina')], max_length=20, verbose_name='Condição do Tempo')),
                ('descricao', models.CharField(blank=True, max_length=255, verbose_name='Descrição')),
                ('indice_uv', models.FloatField(blank=True, null=True, verbose_name='Índice UV')),
                ('visibilidade', models.IntegerField(blank=True, null=True, verbose_name='Visibilidade (m)')),
                ('fonte', models.CharField(default='openweathermap', max_length=50, verbose_name='Fonte de Dados')),
                ('data_requisicao', models.DateTimeField(auto_now_add=True, verbose_name='Data da Requisição')),
                ('localidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='previsoes', to='Clima.localidadeclima')),
            ],
            options={
                'verbose_name': 'Previsão de Tempo',
                'verbose_name_plural': 'Previsões de Tempo',
                'ordering': ['-data_hora'],
            },
        ),
        migrations.CreateModel(
            name='HistoricoClima',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(verbose_name='Data')),
                ('temperatura_minima', models.FloatField(verbose_name='Temperatura Mínima (°C)')),
                ('temperatura_maxima', models.FloatField(verbose_name='Temperatura Máxima (°C)')),
                ('temperatura_media', models.FloatField(verbose_name='Temperatura Média (°C)')),
                ('umidade_media', models.IntegerField(verbose_name='Umidade Média (%)')),
                ('precipitacao_total', models.FloatField(verbose_name='Precipitação Total (mm)')),
                ('velocidade_vento_media', models.FloatField(verbose_name='Velocidade Média do Vento (m/s)')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('localidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historicos', to='Clima.localidadeclima')),
            ],
            options={
                'verbose_name': 'Histórico de Clima',
                'verbose_name_plural': 'Históricos de Clima',
                'ordering': ['-data'],
                'unique_together': {('localidade', 'data')},
            },
        ),
        migrations.CreateModel(
            name='AlertaClima',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_alerta', models.CharField(choices=[('chuva_forte', 'Chuva Forte'), ('tempestade', 'Tempestade'), ('vento_forte', 'Vento Forte'), ('geada', 'Geada'), ('seca', 'Seca'), ('calor_extremo', 'Calor Extremo'), ('frio_extremo', 'Frio Extremo'), ('granizo', 'Granizo')], max_length=20, verbose_name='Tipo de Alerta')),
                ('severidade', models.CharField(choices=[('baixa', 'Baixa'), ('media', 'Média'), ('alta', 'Alta'), ('critica', 'Crítica')], max_length=10, verbose_name='Severidade')),
                ('descricao', models.TextField(verbose_name='Descrição')),
                ('recomendacoes', models.TextField(blank=True, verbose_name='Recomendações')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('data_inicio', models.DateTimeField(verbose_name='Data de Início')),
                ('data_fim', models.DateTimeField(blank=True, null=True, verbose_name='Data de Término')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('localidade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alertas', to='Clima.localidadeclima')),
                ('previsao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alertas', to='Clima.previsaotempo')),
            ],
            options={
                'verbose_name': 'Alerta de Clima',
                'verbose_name_plural': 'Alertas de Clima',
                'ordering': ['-data_inicio'],
            },
        ),
        migrations.AddIndex(
            model_name='previsaotempo',
            index=models.Index(fields=['localidade', '-data_hora'], name='Clima_previ_localid_c5a3f4_idx'),
        ),
        migrations.AddIndex(
            model_name='previsaotempo',
            index=models.Index(fields=['-data_hora'], name='Clima_previ_data_ho_c5a3f4_idx'),
        ),
    ]
