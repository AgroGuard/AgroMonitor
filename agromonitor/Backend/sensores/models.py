from django.db import models

class SensorData(models.Model):
    sensor_id = models.CharField(max_length=50)
    temperatura = models.FloatField()
    umidade = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sensor_id} - {self.timestamp}"