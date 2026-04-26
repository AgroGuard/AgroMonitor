#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from Cadastro.models import Usuario

print('=== Verificação de Banco de Dados ===')
print(f'Total de usuários: {Usuario.objects.count()}')
print()

if Usuario.objects.count() > 0:
    print('Usuários cadastrados:')
    for u in Usuario.objects.all():
        print(f'  - ID: {u.id}')
        print(f'    Usuario: {u.usuario}')
        print(f'    Email: {u.email}')
        print(f'    Categoria: {u.categoria}')
        print(f'    Bloqueado: {u.bloqueio}')
        print()
else:
    print('Nenhum usuário cadastrado ainda.')
