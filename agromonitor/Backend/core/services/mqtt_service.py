import json
import os

import django
import paho.mqtt.client as mqtt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from sensores.models import SensorData

BROKER = os.getenv('MQTT_BROKER', 'localhost')
PORT = int(os.getenv('MQTT_PORT', 1883))
TOPIC = os.getenv('MQTT_TOPIC', 'estufa/sensores/#')


def on_connect(client, userdata, flags, rc):
    print("Conectado ao MQTT")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        SensorData.objects.create(
            sensor_id=data.get('sensor_id') or data.get('dispositivo_id'),
            temperatura=data.get('temperatura'),
            umidade=data.get('umidade'),
            luminosidade=data.get('luminosidade'),
            co2=data.get('co2'),
        )

        print('Dados salvos:', data)

    except Exception as exc:
        print('Erro ao processar mensagem MQTT:', exc)


def create_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    return client


def main():
    client = create_client()
    client.connect(BROKER, PORT, 60)
    print(f'Escutando {BROKER}:{PORT} em {TOPIC}')
    client.loop_forever()


if __name__ == '__main__':
    main()