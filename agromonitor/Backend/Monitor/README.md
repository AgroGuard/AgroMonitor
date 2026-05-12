# App Monitor - Dashboard AgroMonitor

Esta aplicação Django fornece uma dashboard completa para monitoramento da plataforma AgroMonitor.

## Funcionalidades

### 📊 Estatísticas da Plataforma
- Total de usuários cadastrados
- Número de owners (donos de fazendas)
- Usuários ativos por dia
- Novos cadastros diários
- Distribuição por tipo de usuário

### 📈 Gráficos e Visualizações
- Gráfico de distribuição de usuários (Owners, Supervisores, Funcionários)
- Atividades recentes dos usuários
- Alertas do sistema ativos

### ⚡ Métricas em Tempo Real
- Dados atualizados automaticamente a cada 30 segundos
- Métricas customizáveis do sistema

### 🔔 Sistema de Alertas
- Alertas categorizados por nível (Info, Warning, Error, Critical)
- Rastreamento de resolução de problemas
- Interface administrativa para gestão

## Estrutura dos Modelos

### EstatisticaPlataforma
Armazena estatísticas diárias da plataforma:
- `data`: Data da estatística
- `total_usuarios`: Total de usuários
- `total_owners`: Total de owners
- `total_supervisores`: Total de supervisores
- `total_funcionarios`: Total de funcionários
- `usuarios_ativos_hoje`: Usuários ativos no dia
- `novos_usuarios_hoje`: Novos cadastros no dia

### AtividadeUsuario
Rastreia atividades dos usuários:
- `usuario_id`: ID do usuário
- `usuario_nome`: Nome do usuário
- `tipo_atividade`: Tipo da atividade
- `descricao`: Descrição detalhada
- `data_hora`: Quando ocorreu
- `ip_address`: Endereço IP (opcional)

### AlertaSistema
Gerencia alertas e notificações:
- `titulo`: Título do alerta
- `mensagem`: Descrição completa
- `nivel`: Nível de severidade
- `resolvido`: Status de resolução
- `usuario_relacionado`: Usuário afetado (opcional)

### MetricasTempoReal
Armazena métricas atualizadas em tempo real:
- `chave`: Identificador único da métrica
- `valor`: Valor atual
- `unidade`: Unidade de medida
- `descricao`: Descrição da métrica

## URLs Disponíveis

- `/dashboard/`: Página principal da dashboard
- `/dashboard/api/stats/`: API JSON com estatísticas

## Como Usar

### 1. Executar Migrações
```bash
python manage.py makemigrations Monitor
python manage.py migrate
```

### 2. Atualizar Estatísticas Diariamente
```bash
python manage.py update_stats
```

### 3. Acessar Dashboard
Acesse `http://localhost:8000/dashboard/` no navegador.

### 4. Configurar Atualização Automática
Adicione ao crontab para atualização diária:
```bash
# Executar todos os dias às 2:00 AM
0 2 * * * /path/to/your/project/manage.py update_stats
```

## Personalização

### Adicionar Novas Métricas
```python
from Monitor.models import MetricasTempoReal

# Criar ou atualizar métrica
metrica, created = MetricasTempoReal.objects.get_or_create(
    chave='usuarios_online',
    defaults={'unidade': 'usuários', 'descricao': 'Usuários online agora'}
)
metrica.valor = 42  # Seu valor calculado
metrica.save()
```

### Registrar Atividade do Usuário
```python
from Monitor.models import AtividadeUsuario

AtividadeUsuario.objects.create(
    usuario_id=user.id,
    usuario_nome=user.usuario,
    usuario_email=user.email,
    tipo_atividade='login',
    descricao='Usuário fez login no sistema',
    ip_address=request.META.get('REMOTE_ADDR')
)
```

### Criar Alerta do Sistema
```python
from Monitor.models import AlertaSistema

AlertaSistema.objects.create(
    titulo='Backup pendente',
    mensagem='O backup diário não foi executado',
    nivel='warning',
    usuario_relacionado=user.id
)
```

## Próximas Implementações

- [ ] Integração com múltiplos bancos de dados (tenants)
- [ ] Notificações em tempo real via WebSocket
- [ ] Relatórios exportáveis (PDF/Excel)
- [ ] Dashboards personalizáveis por usuário
- [ ] Alertas automáticos baseados em thresholds