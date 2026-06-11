# Deploy automatizado — AgroMonitor

Este arquivo descreve como configurar deploy automatizado do frontend no Vercel e do backend no Render.

1) GitHub Secrets necessários

- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
- `RENDER_API_KEY`, `RENDER_SERVICE_ID`

2) Backend (Render)

- O arquivo `render.yaml` já contém um serviço que executa durante o build:

```sh
pip install -r agromonitor/Backend/requirements-production.txt
python agromonitor/Backend/manage.py migrate --noinput
python agromonitor/Backend/manage.py collectstatic --noinput
```

- Defina as variáveis de ambiente no painel do Render (ou via `render.yaml` envVars):
  - `SECRET_KEY`, `DATABASE_URL`, `DEBUG`, `ALLOWED_HOSTS`, `FRONTEND_URL`, `EMAIL_*`.

- Start command (render.yaml / Procfile):

```sh
gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```

3) Frontend (Vercel)

- O workflow GitHub Actions builda o frontend em `agromonitor/frontend` e usa a ação do Vercel.
- Configure `REACT_APP_API_URL` como variável de ambiente do projeto no Vercel (ou use Secrets + Action).

4) Testando localmente

- Criar virtualenv e instalar dependências:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate    # Windows (PowerShell)
pip install -r agromonitor/Backend/requirements-production.txt
```

- Criar `.env` com as variáveis mínimas (poder usar `agromonitor/Backend/.env.example` como base).

- Rodar migrations e servidor local:

```bash
python agromonitor/Backend/manage.py migrate
python agromonitor/Backend/manage.py collectstatic --noinput
python agromonitor/Backend/manage.py runserver
```
Se quiser, posso também:
- adicionar os comandos de `migrate`/`collectstatic` ao `startCommand` (não recomendado),
- criar um `docker-compose` para testes locais,
- ou adicionar um passo no GitHub Actions para validar e rodar testes antes do deploy.
