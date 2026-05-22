# Generated migration for new IoT models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sensores', '0001_initial'),
    ]

    operations = [
        # Criar modelo Dispositivo
        migrations.CreateModel(
            name='Dispositivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome do dispositivo')),
                ('dispositivo_id', models.CharField(max_length=50, unique=True, verbose_name='ID MQTT')),
                ('tipo', models.CharField(choices=[('sensor_temp', 'Sensor de Temperatura'), ('sensor_umidade', 'Sensor de Umidade'), ('sensor_luz', 'Sensor de Luminosidade'), ('sensor_co2', 'Sensor de CO2'), ('atuador_bomba', 'Bomba de Irrigação'), ('atuador_ventilador', 'Ventilador'), ('atuador_luz', 'Sistema de Iluminação')], max_length=20, verbose_name='Tipo')),
                ('estufa', models.CharField(blank=True, max_length=100, verbose_name='Estufa')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('online', models.BooleanField(default=False, verbose_name='Online')),
                ('ultima_comunicacao', models.DateTimeField(blank=True, null=True, verbose_name='Última comunicação')),
                ('localizacao', models.CharField(blank=True, max_length=200, verbose_name='Localização')),
                ('bateria', models.IntegerField(blank=True, null=True, verbose_name='Bateria %')),
                ('firmware_version', models.CharField(blank=True, max_length=50, verbose_name='Versão Firmware')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
            ],
            options={
                'verbose_name': 'Dispositivo IoT',
                'verbose_name_plural': 'Dispositivos IoT',
                'ordering': ['estufa', 'nome'],
            },
        ),

        # Atualizar modelo SensorData
        migrations.AddField(
            model_name='sensordata',
            name='dispositivo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='leituras', to='sensores.dispositivo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sensordata',
            name='luminosidade',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='co2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sensordata',
            name='recebido_em',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='temperatura',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sensordata',
            name='umidade',
            field=models.FloatField(blank=True, null=True),
        ),
        
        # Criar modelo ComandoAtuador
        migrations.CreateModel(
            name='ComandoAtuador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comando', models.CharField(max_length=100, verbose_name='Comando')),
                ('parametros', models.JSONField(default=dict, verbose_name='Parâmetros')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('enviado', 'Enviado'), ('executado', 'Executado'), ('erro', 'Erro')], default='pendente', max_length=20, verbose_name='Status')),
                ('mensagem_erro', models.TextField(blank=True, verbose_name='Mensagem de erro')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('enviado_em', models.DateTimeField(blank=True, null=True, verbose_name='Enviado em')),
                ('executado_em', models.DateTimeField(blank=True, null=True, verbose_name='Executado em')),
                ('dispositivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comandos', to='sensores.dispositivo')),
            ],
            options={
                'verbose_name': 'Comando de Atuador',
                'verbose_name_plural': 'Comandos de Atuadores',
                'ordering': ['-criado_em'],
            },
        ),

        # Criar modelo RegraAutomacao
        migrations.CreateModel(
            name='RegraAutomacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='Nome da regra')),
                ('descricao', models.TextField(blank=True, verbose_name='Descrição')),
                ('condicao', models.CharField(choices=[('temperatura_maior', 'Temperatura >'), ('temperatura_menor', 'Temperatura <'), ('umidade_maior', 'Umidade >'), ('umidade_menor', 'Umidade <'), ('luminosidade_maior', 'Luminosidade >'), ('luminosidade_menor', 'Luminosidade <')], max_length=20, verbose_name='Condição')),
                ('valor_limite', models.FloatField(verbose_name='Valor limite')),
                ('acao', models.CharField(choices=[('ligar_bomba', 'Ligar Bomba'), ('desligar_bomba', 'Desligar Bomba'), ('ligar_ventilador', 'Ligar Ventilador'), ('desligar_ventilador', 'Desligar Ventilador'), ('ligar_luz', 'Ligar Luz'), ('desligar_luz', 'Desligar Luz'), ('alerta', 'Gerar Alerta')], max_length=20, verbose_name='Ação')),
                ('ativa', models.BooleanField(default=True, verbose_name='Ativa')),
                ('tempo_espera_min', models.IntegerField(default=0, verbose_name='Tempo de espera mínimo (min)')),
                ('ultima_execucao', models.DateTimeField(blank=True, null=True, verbose_name='Última execução')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='regras_sensor', to='sensores.dispositivo')),
                ('atuador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='regras_atuador', to='sensores.dispositivo')),
            ],
            options={
                'verbose_name': 'Regra de Automação',
                'verbose_name_plural': 'Regras de Automação',
                'ordering': ['-criado_em'],
            },
        ),

        # Adicionar índices
        migrations.AddIndex(
            model_name='sensordata',
            index=models.Index(fields=['sensor_id', '-timestamp'], name='sensores_se_sensor__14c3d3_idx'),
        ),
        migrations.AddIndex(
            model_name='sensordata',
            index=models.Index(fields=['dispositivo', '-timestamp'], name='sensores_se_disposi_d7e8f9_idx'),
        ),
    ]
