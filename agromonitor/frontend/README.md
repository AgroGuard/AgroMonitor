# 🌾 AgroMonitor - Frontend React

Frontend da plataforma AgroMonitor para monitoramento climático em tempo real com alertas automáticos.

## 🎯 O que é?

AgroMonitor é uma aplicação de monitoramento agrícola que integra:
- **Previsão de tempo em tempo real** via OpenWeatherMap API
- **Alertas automáticos** para condições climáticas extremas
- **Dashboard interativo** com visualizações de dados
- **Integração completa** com backend Django

## 📱 Funcionalidades

✅ Widget de previsão de tempo atual  
✅ Alertas automáticos (chuva forte, vento, calor, geada, etc)  
✅ Previsão de 5 dias  
✅ Histórico climático  
✅ Autenticação por token  
✅ URLs dinâmicas (dev/prod)  

## 🛠️ Stack Tecnológico

- **React 19.2.4** - UI components
- **React Router 7.13.2** - Navegação
- **Lucide React** - Icons
- **Fetch API** - Requisições HTTP
- **localStorage** - Persistência de dados

## 🚀 Quick Start

### Instalação

```bash
# Entrar no diretório
cd agromonitor/frontend

# Instalar dependências
npm install

# Criar .env.local
echo "REACT_APP_API_URL=http://localhost:8000/api/clima" > .env.local
```

### Desenvolvimento

```bash
# Iniciar servidor de desenvolvimento
npm start

# Acesso
http://localhost:3000
```

### Build Produção

```bash
# Gerar build
npm run build

# Deploy no Vercel
vercel --prod
```

## 📋 Variáveis de Ambiente

Arquivo: `.env.local` (desenvolvimento) ou Vercel env vars (produção)

```
REACT_APP_API_URL=http://localhost:8000/api/clima
```

**Em Produção (Vercel):**
```
REACT_APP_API_URL=https://seu-backend.vercel.app/api/clima
```

## 🔌 API Integration

O frontend conecta automaticamente ao backend via `climaService.js`:

```javascript
import climaService from './services/climaService';

// Obter dados climáticos
const dados = await climaService.obterResumo();

// Sincronizar previsão
await climaService.sincronizar();

// Obter alertas
const alertas = await climaService.obterAlertas({ ativos: true });
```

## 📡 URLs Automáticas

O frontend detecta automaticamente:

- **Desenvolvimento:** `http://localhost:8000/api/clima`
- **Produção:** Usa `REACT_APP_API_URL` do Vercel

Nenhuma URL hardcoded! ✨

## 🔐 Autenticação

Token armazenado em `localStorage`:

```javascript
// Fazer login e armazenar token
climaService.setAuthToken(token);

// Token recuperado automaticamente em cada requisição
// Header: Authorization: Token seu-token
```

## 📚 Documentação

- [Guia de Integração Frontend-Backend](../../GUIA_INTEGRACAO_FRONTEND_BACKEND.md)
- [API Reference](../../INTEGRACAO_CLIMA.md)
- [Deployment](../../DEPLOY_VERCEL.md)

## 📁 Estrutura de Pastas

```
src/
├── components/          # Componentes React
├── services/           # Integração com API
│   └── climaService.js
├── App.js              # Componente principal
└── index.js            # Entry point
```

## ✅ Testes

```bash
# Rodar testes
npm test

# Build test
npm run build
```

## 🆘 Troubleshooting

### Erro: "Cannot find module 'react'"
```bash
npm install
```

### Erro: "CORS error" no console
- Verificar se backend está rodando em `localhost:8000`
- Verificar `REACT_APP_API_URL` está correto
- Backend deve ter CORS configurado

### Erro: "401 Unauthorized"
- Verificar token em `localStorage.getItem('authToken')`
- Re-fazer login

## 📞 Support

- [README principal](../../README_DEPLOY.md)
- [Cheat Sheet](../../CHEAT_SHEET.md)
- [Índice Documentação](../../INDEX_DOCUMENTACAO.md)

---

**Parte do projeto AgroMonitor - Monitoramento Climático Agrícola**

Versão: 1.0.0  
Status: ✅ Pronto para Produção
