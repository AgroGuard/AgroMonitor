# Generated migration for RecuperacaoSenha model

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Cadastro', '0006_usuario_criado_em_usuario_ultimo_login'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecuperacaoSenha',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Email para recuperação')),
                ('token', models.CharField(default=uuid.uuid4, max_length=255, unique=True, verbose_name='Token único')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('expira_em', models.DateTimeField(verbose_name='Expira em')),
                ('utilizado', models.BooleanField(default=False, verbose_name='Utilizado')),
                ('data_utilizacao', models.DateTimeField(blank=True, null=True, verbose_name='Data de utilização')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recuperacoes', to='Cadastro.usuario')),
            ],
            options={
                'verbose_name': 'Recuperação de Senha',
                'verbose_name_plural': 'Recuperações de Senha',
                'ordering': ['-criado_em'],
            },
        ),
    ]
