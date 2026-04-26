# 🧪 Credenciais de Teste - AgroMonitor

## Usuário Administrador

```
Email: admin@agromonitor.com
Usuário: admin
Senha: admin123
Categoria: 999 (Administrador)
```

## Usuário Normal

```
Email: joao@agromonitor.com
Usuário: joao_silva
Senha: teste123
Categoria: 1 (Usuário Normal)
```

## 🚀 Como Testar

### 1. Iniciar o Backend Django
```bash
cd Backend
python manage.py runserver
```
O servidor estará em: `http://127.0.0.1:8000`

### 2. Iniciar o Frontend React (em outro terminal)
```bash
cd frontend
npm start
```
O app estará em: `http://localhost:3000`

### 3. Fazer Login
- Abra `http://localhost:3000` no navegador
- Use um dos emails acima + senha correspondente
- O login deve redirecionar para `/dashboard`

### 4. Testar Cadastro de Novo Usuário
- Clique em "Criar conta"
- Preencha os dados (email deve ser único)
- Após sucesso, volte para login com a nova conta

## 📝 Notas Importantes

- Emails devem ser **únicos** (não é possível registrar com email já existente)
- Senhas precisam de **mínimo 6 caracteres**
- O usuário é armazenado no `localStorage` após login bem-sucedido
- O Dashboard mostra o email do usuário logado

## 🔧 Ferramentas de Diagnóstico

Existem scripts de verificação disponíveis em `Backend/`:

```bash
# Verificar estado completo do banco
python check_db_schema.py

# Listar todos os usuários
python check_db.py

# Criar novo administrador
python create_admin.py

# Criar novo usuário normal
python create_user_test.py
```

## 📍 Endpoints da API

```
POST /api/login/          - Fazer login (JSON)
POST /api/cadastro/       - Registrar novo usuário (JSON)
```

**Exemplo de Login:**
```json
POST http://127.0.0.1:8000/api/login/
Content-Type: application/json

{
  "email": "admin@agromonitor.com",
  "password": "admin123"
}
```

**Resposta (sucesso):**
```json
{
  "message": "Sucesso!",
  "user_id": 1
}
```

**Exemplo de Cadastro:**
```json
POST http://127.0.0.1:8000/api/cadastro/
Content-Type: application/json

{
  "usuario": "novo_user",
  "email": "novo@agromonitor.com",
  "senha": "senha123",
  "confirma_senha": "senha123"
}
```

**Resposta (sucesso - 201):**
```json
{
  "message": "Usuário criado com sucesso!",
  "user_id": 3,
  "usuario": "novo_user"
}
```
