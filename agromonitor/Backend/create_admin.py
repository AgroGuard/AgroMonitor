#!/usr/bin/env python
import os
import django
import bcrypt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from Cadastro.models import Usuario

print('=== CRIAR USUÁRIO ADMINISTRADOR ===')
print()

# Dados do usuário administrador
usuario = 'admin'
email = 'admin@agromonitor.com'
senha = 'admin123'
role = 'super_admin'  # Super administrador do sistema

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
novo_admin = Usuario.objects.create(
    usuario=usuario,
    email=email,
    senha_hash=senha_hash,
    email_hash=email_hash,
    role=role,
    bloqueio=False,
    tentativas_falhas=0
)

print('✓ Usuário administrador criado com sucesso!')
print()
print('=== DADOS DE ACESSO ===')
print(f'Usuário: {usuario}')
print(f'Email: {email}')
print(f'Senha: {senha}')
print(f'Função: {role} (Super Administrador)')
print()
print('Use estas credenciais para fazer login no frontend!')
print()

# Listar todos os usuários
print('=== USUÁRIOS NO BANCO ===')
for u in Usuario.objects.all():
    role_nome = u.get_role_display()  # Usa o verbose_name do choice
    print(f'- {u.usuario} ({u.email}) - {role_nome}')
