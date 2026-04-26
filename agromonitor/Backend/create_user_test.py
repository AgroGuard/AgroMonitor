#!/usr/bin/env python
import os
import django
import bcrypt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from Cadastro.models import Usuario

print('=== CRIAR USUÁRIO DE TESTE ===')
print()

# Dados do usuário normal
usuario = 'joao_silva'
email = 'joao@agromonitor.com'
senha = 'teste123'
categoria = 1  # Usuário comum

# Verificar se usuário já existe
if Usuario.objects.filter(usuario=usuario).exists():
    print(f'❌ Usuário "{usuario}" já existe!')
    exit(1)

if Usuario.objects.filter(email=email).exists():
    print(f'❌ Email "{email}" já cadastrado!')
    exit(1)

# Criptografar senha e email
salt = bcrypt.gensalt()
senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
email_hash = bcrypt.hashpw(email.encode('utf-8'), salt).decode('utf-8')

# Criar usuário
novo_user = Usuario.objects.create(
    usuario=usuario,
    email=email,
    senha_hash=senha_hash,
    email_hash=email_hash,
    categoria=categoria,
    bloqueio=False,
    tentativas_falhas=0
)

print('✓ Usuário de teste criado com sucesso!')
print()
print('=== DADOS DE ACESSO ===')
print(f'Usuário: {usuario}')
print(f'Email: {email}')
print(f'Senha: {senha}')
print(f'Categoria: {categoria} (Usuário Normal)')
print()

# Listar todos os usuários
print('=== TODOS OS USUÁRIOS ===')
for u in Usuario.objects.all():
    categoria_nome = 'Admin' if u.categoria == 999 else f'Usuário ({u.categoria})'
    print(f'- {u.usuario} ({u.email}) - {categoria_nome}')
