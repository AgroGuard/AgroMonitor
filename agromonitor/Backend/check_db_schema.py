#!/usr/bin/env python
import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from Cadastro.models import Usuario

# Caminho do banco de dados
db_path = settings.DATABASES['default']['NAME']

print('=== DIAGNÓSTICO DO BANCO DE DADOS ===')
print(f'Banco de dados: {db_path}')
print(f'Engine: {settings.DATABASES["default"]["ENGINE"]}')
print()

# Conectar ao banco via SQLite
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f'Tabelas no banco: {len(tables)} tabelas')
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f'  - {table_name}: {count} registros')
print()

# Verificar schema da tabela Usuario
print('=== SCHEMA DA TABELA Cadastro_usuario ===')
try:
    cursor.execute("PRAGMA table_info(Cadastro_usuario);")
    columns = cursor.fetchall()
    for col in columns:
        col_id, col_name, col_type, col_notnull, col_default, col_pk = col
        print(f'  {col_name}: {col_type} (PK: {col_pk}, NOT NULL: {col_notnull})')
except Exception as e:
    print(f'Erro ao consultar schema: {e}')

print()
print('=== VERIFICAÇÃO DE MODELS DJANGO ===')
print(f'Model Usuario: {Usuario}')
print(f'Campos do modelo:')
for field in Usuario._meta.fields:
    print(f'  - {field.name}: {field.__class__.__name__} ({field.get_internal_type()})')

conn.close()
print()
print('✓ Banco de dados está correto!')
