#!/usr/bin/env python
"""
Script de setup para a app Clima - AgroMonitor

Este script criará localidades de exemplo e sincronizará dados iniciais.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BD_FAZENDA.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from Clima.models import LocalidadeClima
from Clima.services import OpenWeatherMapService


def criar_localidades_exemplo():
    """Cria localidades de exemplo"""
    
    localidades_data = [
        {
            'nome': 'São Paulo',
            'latitude': -23.5505,
            'longitude': -46.6333,
            'estado': 'SP',
            'pais': 'Brasil',
            'fazenda_id': 'sp-01'
        },
        {
            'nome': 'Minas Gerais (Belo Horizonte)',
            'latitude': -19.9167,
            'longitude': -43.9345,
            'estado': 'MG',
            'pais': 'Brasil',
            'fazenda_id': 'mg-01'
        },
        {
            'nome': 'Paraná (Curitiba)',
            'latitude': -25.4284,
            'longitude': -49.2733,
            'estado': 'PR',
            'pais': 'Brasil',
            'fazenda_id': 'pr-01'
        },
        {
            'nome': 'Rio Grande do Sul (Porto Alegre)',
            'latitude': -30.0277,
            'longitude': -51.2287,
            'estado': 'RS',
            'pais': 'Brasil',
            'fazenda_id': 'rs-01'
        },
        {
            'nome': 'Goiás (Goiânia)',
            'latitude': -15.7942,
            'longitude': -48.0676,
            'estado': 'GO',
            'pais': 'Brasil',
            'fazenda_id': 'go-01'
        },
    ]
    
    criadas = 0
    existentes = 0
    
    for dados in localidades_data:
        localidade, created = LocalidadeClima.objects.get_or_create(
            latitude=dados['latitude'],
            longitude=dados['longitude'],
            defaults={
                'nome': dados['nome'],
                'estado': dados['estado'],
                'pais': dados['pais'],
                'fazenda_id': dados['fazenda_id'],
                'ativa': True,
            }
        )
        
        if created:
            print(f"✓ Criada: {dados['nome']}")
            criadas += 1
        else:
            print(f"⚠ Existente: {dados['nome']}")
            existentes += 1
    
    print(f"\nResumo: {criadas} criadas, {existentes} existentes")
    return criadas > 0


def sincronizar_dados():
    """Sincroniza dados de previsão do tempo"""
    
    print("\n🌤️ Sincronizando dados de previsão...")
    
    try:
        service = OpenWeatherMapService()
        resultados = service.atualizar_todas_localidades()
        
        sucessos = sum(1 for r in resultados if r['resultado']['sucesso'])
        erros = len(resultados) - sucessos
        
        print(f"\n✓ Sincronização concluída:")
        print(f"  Total: {len(resultados)}")
        print(f"  Sucessos: {sucessos}")
        print(f"  Erros: {erros}")
        
        if erros > 0:
            print(f"\nLocalidades com erro:")
            for resultado in resultados:
                if not resultado['resultado']['sucesso']:
                    print(f"  - {resultado['localidade']}: {resultado['resultado']['erro']}")
        
        return sucessos > 0
    except Exception as e:
        print(f"\n✗ Erro ao sincronizar: {e}")
        return False


def main():
    """Executa o setup completo"""
    
    print("=" * 60)
    print("SETUP - App Clima AgroMonitor")
    print("=" * 60)
    
    print("\n1️⃣ Criando localidades de exemplo...")
    criar_localidades_exemplo()
    
    print("\n2️⃣ Sincronizando dados de previsão...")
    sincronizar_dados()
    
    print("\n" + "=" * 60)
    print("✓ Setup concluído com sucesso!")
    print("=" * 60)
    print("\nPróximos passos:")
    print("1. Acesse http://localhost:8000/admin/")
    print("2. Navegue até Clima > Localidades para gerenciar localidades")
    print("3. Use a API em /api/clima/ para acessar os dados")
    print("\nVer mais em: Backend/Clima/README.md")


if __name__ == '__main__':
    main()
