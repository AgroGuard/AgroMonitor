# Autenticação do AgroMonitor

## O que foi implementado

1. Proteção de exclusão de `super_admin`
   - O modelo `Usuario` agora levanta `PermissionDenied` ao tentar excluir um usuário `super_admin`.
   - A validação também está no signal `pre_delete` para proteger exclusões por qualquer caminho.

2. Autenticação com token customizado
   - Adicionado o modelo `UsuarioToken` em `Cadastro/models.py`.
   - O login em `Cadastro/views.py` gera um token único a cada login e limpa tokens anteriores do mesmo usuário.
   - O token é retornado no corpo JSON de `POST /api/login/` como `token`.

3. Autenticação de request por header
   - `obter_usuario_autenticado()` agora aceita três fontes de autenticação:
     - `request.session['user_id']`
     - `X-User-ID` no header
     - `Authorization: Token <token>` no header
   - Isso permite proteger endpoints usando tokens no frontend.

4. Logout
   - Adicionado endpoint `POST /api/logout/` em `Cadastro/urls.py`.
   - O logout apaga o token usado e limpa a sessão do Django.

5. Frontend básico
   - `frontend/src/components/Login/Login.js` agora armazena `authToken` no `localStorage` quando o login retorna com sucesso.
   - O token pode ser usado por serviços como `frontend/src/services/climaService.js`.

6. Testes
   - Novo teste cobre o bloqueio de exclusão de `super_admin`.
   - Teste de login garante que o token é retornado.
   - Teste de endpoint protegido garante que o token funcione ao acessar `/api/estufas/`.

## Como usar

### Login
Requisição:
```http
POST /api/login/
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

Resposta bem-sucedida:
```json
{
  "message": "Sucesso!",
  "user_id": 1,
  "role": "owner",
  "usuario": "usuario",
  "token": "..."
}
```

### Acesso autenticado
Enviar o header:
```http
Authorization: Token <token>
```

### Logout
Requisição:
```http
POST /api/logout/
Authorization: Token <token>
```

Resposta:
```json
{
  "message": "Logout realizado com sucesso."
}
```
