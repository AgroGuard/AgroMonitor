from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BD_FAZENDA', '0001_initial'),
        ('Cadastro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='estufa',
            name='owner',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='estufas',
                to='Cadastro.usuario',
                verbose_name='Owner'
            ),
        ),
    ]
