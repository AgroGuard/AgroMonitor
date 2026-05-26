from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('sensores', '0002_iot_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensordata',
            name='recebido_em',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
