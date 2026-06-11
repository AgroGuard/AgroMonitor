# Testes locais sem Docker

Este guia mostra como executar o backend Django e o frontend React localmente sem usar Docker.

Requisitos:
- Python 3.11+
- Node.js 18+
- Postgres e Redis locais ou outros serviços acessíveis

Passos:

1. Copie o arquivo de ambiente example:

```powershell
copy .env.dev .env
```

2. Crie e ative o ambiente virtual Python:

```powershell
python -m venv .venv
.venv\Scripts\Activate
```

3. Instale as dependências do backend:

```powershell
pip install -r requirements-production.txt
```

4. Ajuste `DATABASE_URL` e `REDIS_URL` em `.env` para apontar para serviços locais.

5. Rode migrations e colecione arquivos estáticos:

```powershell
python agromonitor/Backend/manage.py migrate
python agromonitor/Backend/manage.py collectstatic --noinput
```

6. Inicie o backend:

```powershell
python agromonitor/Backend/manage.py runserver
```

7. No frontend, instale e inicie o React:

```powershell
cd agromonitor/frontend
npm install
npm start
```

Acessos:
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
