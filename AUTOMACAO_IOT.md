# Sistema de Automação & IoT - AgroMonitor

## 🎯 Visão Geral

Sistema completo de IoT para automação de estufas com suporte a:
- ✅ Sensores de temperatura, umidade, luz, CO2
- ✅ Atuadores (bomba, ventilador, iluminação)
- ✅ Regras de automação customizáveis
- ✅ MQTT para comunicação em tempo real
- ✅ Monitoramento e alertas críticos

---

## 📦 Modelos de Dados

### 1. **Dispositivo**
Representa qualquer sensor ou atuador conectado

```python
class Dispositivo:
    nome: str                    # Nome do dispositivo
    dispositivo_id: str          # ID MQTT único
    tipo: str                    # sensor_temp, atuador_bomba, etc
    estufa: str                  # Nome da estufa
    ativo: bool                  # Se está ativo
    online: bool                 # Se está online
    ultima_comunicacao: datetime # Última vez que foi visto
    bateria: int                 # % de bateria
```

### 2. **SensorData**
Armazena leituras dos sensores

```python
class SensorData:
    dispositivo: FK(Dispositivo)
    temperatura: float
    umidade: float
    luminosidade: float
    co2: float
    timestamp: datetime
```

### 3. **ComandoAtuador**
Registra comandos enviados para atuadores

```python
class ComandoAtuador:
    dispositivo: FK(Dispositivo)
    comando: str                 # ligar_bomba, desligar_ventilador, etc
    parametros: dict             # {"velocidade": 100}
    status: str                  # pendente, enviado, executado, erro
```

### 4. **RegraAutomacao**
Define regras de automação (if-then)

```python
class RegraAutomacao:
    sensor: FK(Dispositivo)      # Sensor que dispara
    condicao: str                # temperatura_maior, umidade_menor, etc
    valor_limite: float          # 35, 60, etc
    atuador: FK(Dispositivo)     # Atuador a controlar
    acao: str                    # ligar_bomba, desligar_ventilador, etc
    tempo_espera_min: int        # Tempo mínimo entre execuções
```

---

## 📡 Fluxo MQTT

### Tópicos

```
estufa/sensores/#          ← ESP32 envia dados
estufa/comando/response/#  ← ESP32 responde a comandos
estufa/status/#            ← ESP32 envia status (online/offline)
```

### Formato de Mensagem - Sensor

```json
{
  "sensor_id": "sensor_001",
  "dispositivo_id": "esp32_sala_a",
  "temperatura": 25.5,
  "umidade": 65.3,
  "luminosidade": 450,
  "co2": 850,
  "bateria": 95,
  "timestamp": "2026-05-20T10:30:00Z"
}
```

### Formato de Mensagem - Comando

```json
{
  "comando": "ligar_bomba",
  "parametros": {
    "duracao": 300
  },
  "timestamp": "2026-05-20T10:30:00Z"
}
```

### Formato de Resposta - Comando

```json
{
  "dispositivo_id": "esp32_sala_a",
  "comando_id": 123,
  "sucesso": true,
  "mensagem": "Bomba ligada com sucesso"
}
```

---

## 🔌 Exemplo - Código ESP32 (Arduino)

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// Configurações WiFi
const char* ssid = "SEU_SSID";
const char* password = "SUA_SENHA";

// Configurações MQTT
const char* mqtt_broker = "192.168.1.100";  // IP do servidor
const int mqtt_port = 1883;
const char* dispositivo_id = "esp32_estufa_001";

// Sensores
#define DPIN_DHT 4
DHT dht(DPIN_DHT, DHT22);

// Atuadores
#define PIN_BOMBA 12
#define PIN_VENTILADOR 13

// Cliente MQTT
WiFiClient wifiClient;
PubSubClient client(wifiClient);

void setup() {
    Serial.begin(115200);
    
    // Configurar pinos
    pinMode(PIN_BOMBA, OUTPUT);
    pinMode(PIN_VENTILADOR, OUTPUT);
    digitalWrite(PIN_BOMBA, LOW);
    digitalWrite(PIN_VENTILADOR, LOW);
    
    // Iniciar sensor DHT
    dht.begin();
    
    // Conectar WiFi
    conectarWiFi();
    
    // Configurar MQTT
    client.setServer(mqtt_broker, mqtt_port);
    client.setCallback(callbackMQTT);
}

void conectarWiFi() {
    Serial.print("Conectando a WiFi: ");
    Serial.println(ssid);
    
    WiFi.begin(ssid, password);
    
    int tentativas = 0;
    while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
        delay(500);
        Serial.print(".");
        tentativas++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✓ WiFi conectado!");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\n✗ Falha ao conectar WiFi");
    }
}

void loop() {
    // Reconectar MQTT se desconectado
    if (!client.connected()) {
        conectarMQTT();
    }
    client.loop();
    
    // Ler sensores a cada 10 segundos
    static unsigned long ultimaLeitura = 0;
    if (millis() - ultimaLeitura > 10000) {
        lerESenviarSensores();
        ultimaLeitura = millis();
    }
}

void conectarMQTT() {
    Serial.print("Conectando MQTT...");
    
    if (client.connect(dispositivo_id)) {
        Serial.println("✓ Conectado!");
        
        // Se inscrever em tópicos de comando
        String topico_comando = String("estufa/comando/") + dispositivo_id + "/#";
        client.subscribe(topico_comando.c_str());
        
        // Enviar status online
        String topico_status = String("estufa/status/") + dispositivo_id;
        client.publish(topico_status.c_str(), 
                      "{\"dispositivo_id\": \"" + String(dispositivo_id) + "\", \"online\": true}");
    } else {
        Serial.print("✗ Erro: ");
        Serial.println(client.state());
        delay(5000);
    }
}

void lerESenviarSensores() {
    // Ler DHT22
    float temp = dht.readTemperature();
    float umidade = dht.readHumidity();
    
    if (isnan(temp) || isnan(umidade)) {
        Serial.println("Erro ao ler sensor DHT!");
        return;
    }
    
    // Criar JSON
    DynamicJsonDocument doc(256);
    doc["sensor_id"] = dispositivo_id;
    doc["dispositivo_id"] = dispositivo_id;
    doc["temperatura"] = temp;
    doc["umidade"] = umidade;
    doc["bateria"] = 95;  // Simulado
    
    // Publicar
    String topico = String("estufa/sensores/") + dispositivo_id;
    String payload;
    serializeJson(doc, payload);
    
    client.publish(topico.c_str(), payload.c_str());
    
    Serial.print("Publicado: T=");
    Serial.print(temp);
    Serial.print("°C H=");
    Serial.print(umidade);
    Serial.println("%");
}

void callbackMQTT(char* topico, byte* payload, unsigned int length) {
    // Parse JSON
    DynamicJsonDocument doc(256);
    deserializeJson(doc, payload, length);
    
    String comando = doc["comando"];
    
    Serial.print("Comando recebido: ");
    Serial.println(comando);
    
    if (comando == "ligar_bomba") {
        digitalWrite(PIN_BOMBA, HIGH);
        enviarResposta(true, "Bomba ligada");
    } 
    else if (comando == "desligar_bomba") {
        digitalWrite(PIN_BOMBA, LOW);
        enviarResposta(true, "Bomba desligada");
    }
    else if (comando == "ligar_ventilador") {
        digitalWrite(PIN_VENTILADOR, HIGH);
        enviarResposta(true, "Ventilador ligado");
    }
    else if (comando == "desligar_ventilador") {
        digitalWrite(PIN_VENTILADOR, LOW);
        enviarResposta(true, "Ventilador desligado");
    }
    else {
        enviarResposta(false, "Comando desconhecido");
    }
}

void enviarResposta(bool sucesso, String mensagem) {
    DynamicJsonDocument doc(256);
    doc["dispositivo_id"] = dispositivo_id;
    doc["sucesso"] = sucesso;
    doc["mensagem"] = mensagem;
    
    String topico = String("estufa/comando/response/") + dispositivo_id;
    String payload;
    serializeJson(doc, payload);
    
    client.publish(topico.c_str(), payload.c_str());
}
```

---

## 🚀 Endpoints da API

### Listar Dispositivos
```bash
GET /api/sensores/dispositivos/
  ?tipo=sensor_temp
  ?estufa=Estufa_01
```

### Enviar Comando
```bash
POST /api/sensores/comando/
{
  "dispositivo_id": "esp32_001",
  "comando": "ligar_bomba",
  "parametros": {}
}
```

### Controlar Bomba
```bash
POST /api/sensores/bomba/
{
  "dispositivo_id": "esp32_001",
  "estado": "ligar"
}
```

### Controlar Ventilador
```bash
POST /api/sensores/ventilador/
{
  "dispositivo_id": "esp32_001",
  "estado": "ligar",
  "velocidade": 75
}
```

### Histórico de Sensores
```bash
GET /api/sensores/historico/
  ?dispositivo_id=esp32_001
  ?dias=7
  ?limite=100
```

### Estatísticas
```bash
GET /api/sensores/stats/
  ?dispositivo_id=esp32_001
  ?dias=30
```

---

## ⚙️ Configuração MQTT

### Setup Local (Mosquitto)
```bash
# Instalar
sudo apt-get install mosquitto mosquitto-clients

# Iniciar
mosquitto -c /etc/mosquitto/mosquitto.conf

# Testar
mosquitto_pub -h localhost -t "test" -m "hello"
mosquitto_sub -h localhost -t "test"
```

### Setup HiveMQ Cloud
```bash
# URL: https://console.hivemq.cloud
# Credenciais: user/password configurados
# Porta: 8883 (TLS)

# Código ESP32:
const char* mqtt_broker = "seu-cluster.hivemq.com";
const int mqtt_port = 8883;
client.setServer(mqtt_broker, mqtt_port);
```

---

## 🔄 Rodar MQTT Service

### Development
```bash
cd Backend
python manage.py run_mqtt_service --debug
```

### Production (systemd)
```bash
sudo systemctl start agromonitor-mqtt
sudo systemctl status agromonitor-mqtt
```

Arquivo: `/etc/systemd/system/agromonitor-mqtt.service`
```ini
[Unit]
Description=AgroMonitor MQTT Service
After=network.target

[Service]
Type=simple
User=django
WorkingDirectory=/opt/agromonitor
ExecStart=/opt/venv/bin/python manage.py run_mqtt_service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 📊 Migrations

```bash
python manage.py migrate sensores
```

Criará:
- ✅ Tabela `Dispositivo`
- ✅ Tabela `ComandoAtuador` (com FK para Dispositivo)
- ✅ Tabela `RegraAutomacao` (com FK sensor + atuador)
- ✅ Campos extras em `SensorData` (luminosidade, co2, dispositivo)

---

## 🤖 Regras de Automação

### Criar Regra (via admin)
```
Nome: Ligar ventilador se temperatura > 30
Sensor: Sensor Temp 001
Condição: temperatura_maior
Valor limite: 30
Atuador: Ventilador Sala A
Ação: ligar_ventilador
Tempo de espera: 5 min (evita on/off rápido)
```

### Via Code
```python
from sensores.models import Dispositivo, RegraAutomacao

sensor = Dispositivo.objects.get(nome="Sensor Temp")
atuador = Dispositivo.objects.get(nome="Ventilador")

RegraAutomacao.objects.create(
    nome="Auto Ventilador",
    sensor=sensor,
    condicao="temperatura_maior",
    valor_limite=30,
    atuador=atuador,
    acao="ligar_ventilador",
    ativa=True
)
```

---

## 🚨 Alertas Automáticos

Sistema gera alertas automaticamente para:
- 🔴 **Crítico**: Temperatura > 40°C
- 🔵 **Aviso**: Temperatura < 5°C
- 💧 **Aviso**: Umidade > 95% (risco de mofo)

Customizáveis em `processar_leitura_sensor()` no MQTT service

---

## 🔧 Troubleshooting

### MQTT não conecta
```bash
# Verificar se broker está rodando
netstat -an | grep 1883

# Reiniciar Mosquitto
sudo systemctl restart mosquitto
```

### ESP32 não envia dados
- Verificar WiFi: `Serial.println(WiFi.status())`
- Verificar MQTT: `Serial.println(client.state())`
- Testar com mosquitto_sub

### Dados não aparecem no BD
- Verificar migrations: `python manage.py showmigrations`
- Verificar logs do MQTT service
- Verificar formato JSON

---

## 📈 Status: ~60% Implementado

✅ Modelos completos
✅ Endpoints de controle
✅ MQTT management command
✅ Automação com regras
✅ Alertas automáticos
⏳ Frontend dashboard (gráficos em tempo real)
⏳ WebSocket para updates live

---

## 📝 Próximas Melhorias

1. Dashboard com gráficos em tempo real
2. WebSocket para atualizações live
3. Histórico de comandos executados
4. Agendamento de tarefas (cronJobs)
5. Backup/sincronização de dados
6. Suporte a mais sensores/atuadores
