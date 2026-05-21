# 🧪 Guia de Teste - Sistema MQTT & IoT

## 📋 Checklist de Testes

### 1. Backend Setup ✅

- [x] Django migrações aplicadas
- [x] Modelos criados (Dispositivo, ComandoAtuador, RegraAutomacao)
- [x] Endpoints de API implementados
- [x] Admin interface configurado
- [x] MQTT management command criado

### 2. Frontend Setup ✅

- [x] Componente DeviceControl criado
- [x] CSS stylesheet pronto
- [x] Rota `/dispositivos` adicionada
- [x] Link no Sidebar adicionado

---

## 🚀 Como Testar Localmente

### Pré-requisitos

```bash
# Backend
cd Backend
pip install -r requirements.txt
python manage.py migrate

# Frontend
cd ../frontend
npm install
```

### Teste 1: API Endpoints

```bash
# Terminal 1: Rodar Django dev server
cd Backend
python manage.py runserver

# Terminal 2: Testar endpoints
curl http://localhost:8000/api/sensores/dispositivos/

# Criar dispositivo de teste via admin
# http://localhost:8000/admin
```

### Teste 2: Dashboard Frontend

```bash
# Terminal 3: Rodar React
cd frontend
npm start

# Acessar http://localhost:3000/dispositivos
```

### Teste 3: MQTT Service (Simulado)

Sem um broker MQTT real, o serviço vai falhar ao conectar. Para testes:

#### Opção A: Usar Mosquitto Local

```bash
# Instalar Mosquitto (Windows)
# Baixar: https://mosquitto.org/download/

# Ou via WSL
sudo apt-get install mosquitto mosquitto-clients

# Iniciar
mosquitto -c /etc/mosquitto/mosquitto.conf

# Em outro terminal, testar
mosquitto_pub -h localhost -t "estufa/sensores/sensor_001" -m '{"sensor_id":"sensor_001","temperatura":25.5,"umidade":65}'

# Verificar se foi recebido
mosquitto_sub -h localhost -t "estufa/sensores/#"
```

#### Opção B: Usar HiveMQ Cloud (Production-like)

```bash
# Criar conta em https://console.hivemq.cloud
# Copiar credenciais

# Terminal 1: Rodar MQTT service
cd Backend
MQTT_BROKER=seu-cluster.hivemq.com MQTT_PORT=8883 \
  python manage.py run_mqtt_service --debug

# Terminal 2: Testar publicação
mosquitto_pub -h seu-cluster.hivemq.com -p 8883 \
  -u seu_usuario -P sua_senha \
  -t "estufa/sensores/esp32_001" \
  -m '{"sensor_id":"esp32_001","temperatura":28,"umidade":70,"bateria":95}'
```

### Teste 4: Simulação Completa ESP32

Sem um ESP32 real, você pode simular com Python:

```python
# arquivo: simulate_esp32.py
import paho.mqtt.client as mqtt
import json
import time
import random

client = mqtt.Client()
client.connect("localhost", 1883, 60)

for i in range(100):  # 100 leituras
    temp = 20 + random.uniform(-5, 10)
    umidade = 50 + random.uniform(-20, 30)
    
    payload = {
        "sensor_id": "esp32_estufa_001",
        "dispositivo_id": "esp32_estufa_001",
        "temperatura": round(temp, 2),
        "umidade": round(umidade, 2),
        "luminosidade": random.randint(200, 800),
        "co2": random.randint(400, 1000),
        "bateria": random.randint(50, 100)
    }
    
    client.publish("estufa/sensores/esp32_estufa_001", json.dumps(payload))
    print(f"[{i}] Enviado: {payload}")
    time.sleep(5)

client.disconnect()
```

Executar:
```bash
cd Backend
python ../simulate_esp32.py
```

---

## 📊 Dados de Teste

### Dispositivos Pré-Cadastrados (via admin)

```
Nome: Sensor Temperatura Sala A
ID MQTT: sensor_temp_sala_a
Tipo: sensor_temp
Estufa: Estufa A
Localização: Canto Nordeste

---

Nome: Bomba de Irrigação
ID MQTT: atuador_bomba_a
Tipo: atuador_bomba
Estufa: Estufa A
Localização: Piso Sul

---

Nome: Ventilador Principal
ID MQTT: atuador_ventilador_a
Tipo: atuador_ventilador
Estufa: Estufa A
Localização: Centro Superior
```

### Dados de Teste para Leitura

```json
{
  "sensor_id": "sensor_temp_sala_a",
  "dispositivo_id": "sensor_temp_sala_a",
  "temperatura": 26.5,
  "umidade": 68.3,
  "luminosidade": 450,
  "co2": 820,
  "bateria": 87
}
```

### Dados de Teste para Comando

```json
{
  "dispositivo_id": "atuador_bomba_a",
  "comando": "ligar_bomba",
  "parametros": {}
}
```

---

## 🔍 Testes no Django Admin

1. Acessar http://localhost:8000/admin
2. Login com credenciais
3. Testar criar Dispositivo
4. Testar criar RegraAutomacao
5. Testar visualizar SensorData após MQTT receber dados

---

## ✅ Checklist de Validação

- [ ] Dispositivos aparecem em `/api/sensores/dispositivos/`
- [ ] Dashboard carrega sem erros
- [ ] Botões de controle funcionam
- [ ] Status online/offline atualiza a cada 5s
- [ ] Filtros funcionam
- [ ] Admin permite criar/editar dispositivos
- [ ] MQTT service se conecta sem erros (quando broker disponível)
- [ ] Dados de sensores são salvos em SensorData
- [ ] Comandos são salvos em ComandoAtuador

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'paho'"
```bash
pip install paho-mqtt
```

### MQTT: "Address already in use"
```bash
# Kill processo anterior
lsof -ti:1883 | xargs kill -9
```

### Dashboard não conecta à API
- Verificar CORS headers no Django
- Verificar token de autenticação
- Ver console do navegador para erros

### Dados não salvam em SensorData
- Verificar se MQTT service está rodando
- Verificar logs: `python manage.py run_mqtt_service --debug`
- Verificar formato JSON das mensagens

---

## 📈 Próximas Melhorias

1. ✅ Testes unitários para views
2. ✅ Testes de integração MQTT
3. ✅ WebSocket para atualizações em tempo real
4. ✅ Gráficos de sensor histórico
5. ✅ Agendador de tarefas (Celery)

---

## 💡 Dicas

- Usar `--debug` flag para mais verbose logging
- Monitor logs em tempo real: `tail -f /var/log/agromonitor.log`
- Usar admin para cadastrar dados manualmente
- Simular ESP32 para testes sem hardware real

