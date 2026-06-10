#!/usr/bin/env python
import os
import django
import bcrypt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from Cadastro.models import Usuario

usuario = 'super_admin_test'
email = 'superadmin_test@agromonitor.com'
senha = 'superpass'
role = 'super_admin'

if Usuario.objects.filter(usuario=usuario).exists():
    print(f'Usuário "{usuario}" já existe.')
else:
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
    email_hash = bcrypt.hashpw(email.encode('utf-8'), salt).decode('utf-8')
    novo = Usuario.objects.create(
        usuario=usuario,
        email=email,
        senha_hash=senha_hash,
        email_hash=email_hash,
        role=role,
        bloqueio=False,
        tentativas_falhas=0
    )
    print('Usuário super_admin de teste criado com sucesso:')
    print(f'  usuario: {usuario}')
    print(f'  email: {email}')
    print(f'  senha: {senha}')
