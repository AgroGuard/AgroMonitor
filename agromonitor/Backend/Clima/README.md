# App Clima - AgroMonitor

Integração com a API OpenWeatherMap para previsão e monitoramento climático.

## Funcionalidades

- 🌤️ Previsão do tempo em tempo real
- 📊 Previsão de 5 dias
- ⚠️ Alertas automáticos para condições extremas
- 📈 Histórico climático
- 🌍 Suporte a múltiplas localidades

## Instalação

### 1. Dependências

Instale as pacotes necessárias:

```bash
pip install djangorestframework
pip install django-cors-headers
pip install requests
```

Ou adicione ao requirements.txt:
```
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
requests>=2.28.0
```

### 2. Configuração

A app já está configurada em `settings.py`, mas você precisa definir a chave da API OpenWeatherMap no arquivo `.env` do backend:

```env
OPENWEATHER_API_KEY=sua_chave_openweather_aqui
```

### 3. Migrations

Execute as migrations para criar as tabelas do banco de dados:

```bash
python manage.py migrate
```

## Uso

### Criar uma Localidade

```bash
python manage.py criar_localidade_clima "São Paulo" --latitude -23.5505 --longitude -46.6333 --estado "SP"
```

Ou via API:
```bash
POST /api/clima/api/localidades/
{
  "nome": "São Paulo",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "pais": "Brasil",
  "estado": "SP",
  "fazenda_id": "fazenda-01"
}
```

### Sincronizar Dados de Previsão

```bash
# Sincronizar todas as localidades
python manage.py sincronizar_tempo

# Sincronizar uma localidade específica
python manage.py sincronizar_tempo --localidade-id 1
```

Ou via API:
```bash
POST /api/clima/api/localidades/{id}/atualizar_previsao/
POST /api/clima/api/localidades/atualizar_todas/
POST /api/clima/api/sincronizar/
```

### Obter Previsões

```bash
# Obter previsões de uma localidade
GET /api/clima/api/localidades/{id}/previsoes_atuais/

# Listar todas as previsões
GET /api/clima/api/previsoes/

# Filtrar por condição
GET /api/clima/api/previsoes/?condicao=limpo

# Filtrar por período
GET /api/clima/api/previsoes/?periodo=semana
```

### Obter Alertas

```bash
# Alertas de uma localidade
GET /api/clima/api/localidades/{id}/alertas/

# Todos os alertas ativos
GET /api/clima/api/alertas/?ativos=true

# Alertas por severidade
GET /api/clima/api/alertas/?severidade=critica

# Desativar um alerta
POST /api/clima/api/alertas/{id}/desativar/
```

### Obter Histórico

```bash
# Histórico dos últimos 30 dias
GET /api/clima/api/localidades/{id}/historico/

# Histórico customizado
GET /api/clima/api/localidades/{id}/historico/?dias=60
```

### Resumo do Clima

```bash
# Resumo de todas as localidades
GET /api/clima/api/resumo/
```

## Modelos

### LocalidadeClima
Representa uma localidade para monitoramento climático.

```python
{
  "id": 1,
  "nome": "São Paulo",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "pais": "Brasil",
  "estado": "SP",
  "ativa": true,
  "fazenda_id": "fazenda-01",
  "criada_em": "2024-01-15T10:30:00Z",
  "atualizada_em": "2024-01-15T10:30:00Z"
}
```

### PrevisaoTempo
Previsão do tempo para uma localidade em um determinado momento.

```python
{
  "id": 1,
  "localidade": 1,
  "localidade_nome": "São Paulo",
  "data_hora": "2024-01-15T15:00:00Z",
  "temperatura_atual": 25.5,
  "temperatura_minima": 20.0,
  "temperatura_maxima": 30.0,
  "sensacao_termica": 24.0,
  "umidade": 70,
  "pressao": 1013,
  "velocidade_vento": 5.5,
  "direcao_vento": 180,
  "cobertura_nuvem": 40,
  "chance_chuva": 10,
  "precipitacao": null,
  "condicao_tempo": "nublado",
  "descricao": "Céu parcialmente nublado",
  "indice_uv": 6.5,
  "visibilidade": 10000,
  "fonte": "openweathermap",
  "data_requisicao": "2024-01-15T15:00:00Z"
}
```

### AlertaClima
Alerta para condições climáticas extremas ou perigosas.

```python
{
  "id": 1,
  "localidade": 1,
  "localidade_nome": "São Paulo",
  "previsao": 1,
  "previsao_data": "2024-01-15T15:00:00Z",
  "tipo_alerta": "chuva_forte",
  "severidade": "alta",
  "descricao": "Chuva forte prevista: 45mm/h",
  "recomendacoes": "Proteja plantas sensíveis. Verifique drenagem de água.",
  "ativo": true,
  "data_inicio": "2024-01-15T15:00:00Z",
  "data_fim": null,
  "criado_em": "2024-01-15T14:00:00Z",
  "atualizado_em": "2024-01-15T14:00:00Z"
}
```

### HistoricoClima
Dados históricos agregados do clima.

```python
{
  "id": 1,
  "localidade": 1,
  "localidade_nome": "São Paulo",
  "data": "2024-01-15",
  "temperatura_minima": 18.0,
  "temperatura_maxima": 32.0,
  "temperatura_media": 25.0,
  "umidade_media": 65,
  "precipitacao_total": 5.0,
  "velocidade_vento_media": 4.5,
  "criado_em": "2024-01-16T00:00:00Z"
}
```

## Tipos de Alertas

- **chuva_forte**: Precipitação > 20mm/h
- **tempestade**: Condição de tempestade detectada
- **vento_forte**: Velocidade do vento > 15 m/s
- **geada**: Temperatura < 0°C
- **seca**: Nenhuma precipitação por período prolongado
- **calor_extremo**: Temperatura > 35°C
- **frio_extremo**: Temperatura < 5°C
- **granizo**: Condição de granizo detectada

## Níveis de Severidade

- **baixa**: Condição incomum, monitore
- **media**: Risco moderado, tome precauções
- **alta**: Risco significativo, aja imediatamente
- **critica**: Risco crítico, ação urgente necessária

## Condições de Tempo

- limpo
- nublado
- nuvem_leve
- chuvoso
- tempestade
- neve
- neblina

## Integração com React (Frontend)

Exemplo de uso no frontend:

```javascript
// Obter previsões
const response = await fetch('/api/clima/api/localidades/1/previsoes_atuais/', {
  headers: {
    'Authorization': `Token ${authToken}`
  }
});

const data = await response.json();
console.log(data.previsao_atual); // Previsão atual
console.log(data.previsoes_proximos_dias); // Próximos 5 dias

// Obter alertas
const alertasResponse = await fetch('/api/clima/api/localidades/1/alertas/', {
  headers: {
    'Authorization': `Token ${authToken}`
  }
});

const alertas = await alertasResponse.json();
console.log(alertas.alertas); // Lista de alertas
```

## Testes

Execute os testes da app:

```bash
python manage.py test Clima
```

## Troubleshooting

### Erro: "OPENWEATHER_API_KEY não configurada"

Certifique-se de que a variável `OPENWEATHER_API_KEY` está configurada em `settings.py`.

### Erro de conexão com OpenWeatherMap

- Verifique sua conexão com internet
- Verifique se a chave da API é válida
- Verifique os logs em `agromonitor.log`

### Nenhuma previsão sendo retornada

Certifique-se de que:
1. Localidades foram criadas (GET /api/clima/api/localidades/)
2. A sincronização foi executada (POST /api/clima/api/sincronizar/)
3. As coordenadas estão corretas

## API Reference

### Endpoints

#### Localidades
- `GET /api/clima/api/localidades/` - Listar localidades
- `POST /api/clima/api/localidades/` - Criar localidade
- `GET /api/clima/api/localidades/{id}/` - Detalhe da localidade
- `PUT /api/clima/api/localidades/{id}/` - Atualizar localidade
- `DELETE /api/clima/api/localidades/{id}/` - Deletar localidade
- `POST /api/clima/api/localidades/{id}/atualizar_previsao/` - Atualizar previsão
- `POST /api/clima/api/localidades/atualizar_todas/` - Atualizar todas
- `GET /api/clima/api/localidades/{id}/previsoes_atuais/` - Previsões atuais
- `GET /api/clima/api/localidades/{id}/alertas/` - Alertas
- `GET /api/clima/api/localidades/{id}/historico/` - Histórico

#### Previsões
- `GET /api/clima/api/previsoes/` - Listar previsões
- `GET /api/clima/api/previsoes/{id}/` - Detalhe da previsão

#### Alertas
- `GET /api/clima/api/alertas/` - Listar alertas
- `GET /api/clima/api/alertas/{id}/` - Detalhe do alerta
- `POST /api/clima/api/alertas/{id}/desativar/` - Desativar alerta

#### Histórico
- `GET /api/clima/api/historicos/` - Listar histórico
- `GET /api/clima/api/historicos/{id}/` - Detalhe do histórico

#### Utilitários
- `GET /api/clima/api/resumo/` - Resumo de todas as localidades
- `POST /api/clima/api/sincronizar/` - Sincronizar todas as localidades

## Documentação OpenWeatherMap

Para mais informações sobre a API OpenWeatherMap, visite:
https://openweathermap.org/api

## Licença

Este código faz parte do projeto AgroMonitor.
