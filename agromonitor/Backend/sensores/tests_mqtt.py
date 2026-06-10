import importlib
import os
import sys
import types


def test_mqtt_service_uses_core_settings(monkeypatch):
    """O serviço MQTT deve iniciar com as configurações reais do projeto."""
    monkeypatch.delenv('DJANGO_SETTINGS_MODULE', raising=False)
    sys.modules.pop('core.services.mqtt_service', None)

    captured = []

    import django

    def fake_setup():
        captured.append(os.environ.get('DJANGO_SETTINGS_MODULE'))

    monkeypatch.setattr(django, 'setup', fake_setup, raising=True)

    fake_sensor_module = types.ModuleType('sensores.models')
    fake_sensor_module.SensorData = object
    monkeypatch.setitem(sys.modules, 'sensores.models', fake_sensor_module)

    fake_client = types.SimpleNamespace(
        on_connect=None,
        on_message=None,
        connect=lambda *args, **kwargs: None,
        loop_forever=lambda: None,
    )

    import paho.mqtt.client as mqtt_client
    monkeypatch.setattr(mqtt_client, 'Client', lambda: fake_client, raising=True)

    importlib.import_module('core.services.mqtt_service')

    assert captured == ['core.settings']
