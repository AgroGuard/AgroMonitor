from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Cadastro', '0010_usuariotoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='criado_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='usuarios_criados',
                to='Cadastro.usuario',
                verbose_name='Criado por'
            ),
        ),
    ]
