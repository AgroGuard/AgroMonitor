import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seu_projeto.settings')
django.setup()

from sensores.models import SensorData
from app.models import SensorData

import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
TOPIC = "estufa/sensores"

def on_connect(client, userdata, flags, rc):
    print("Conectado ao MQTT")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        SensorData.objects.create(
            sensor_id=data.get("sensor_id"),
            temperatura=data.get("temperatura"),
            umidade=data.get("umidade"),
        )

        print("Dados salvos:", data)

    except Exception as e:
        print("Erro:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()