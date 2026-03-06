#!/usr/bin/env python3
"""
Diagnosticar temporadas disponibles en la API
"""
import requests
import json

API_KEY = "11eaff423a9042393b1fe21512384884"
BASE_URL = "https://v3.football.api-sports.io"
headers = {'x-apisports-key': API_KEY}

print("🔍 DIAGNOSTICANDO TEMPORADAS DISPONIBLES")
print("=" * 60)

# 1. Verificar información de una liga específica (LaLiga)
print("\n1️⃣ VERIFICANDO INFORMACIÓN DE LALIGA (ID: 140)")
url = f"{BASE_URL}/leagues"
params = {'id': 140}
response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    
    # Explorar la estructura para encontrar temporadas
    if isinstance(data, dict) and 'response' in data:
        liga_info = data['response'][0]
        print("✅ Liga encontrada")
        
        # Buscar temporadas
        if 'seasons' in liga_info:
            seasons = liga_info['seasons']
            print(f"\n📅 Temporadas disponibles:")
            for season in seasons[-5:]:  # Últimas 5
                year = season.get('year')
                start = season.get('start', 'N/A')
                end = season.get('end', 'N/A')
                current = season.get('current', False)
                print(f"   • {year} ({start} to {end}) {'(ACTUAL)' if current else ''}")
    else:
        print(f"Formato inesperado: {type(data)}")
        print(json.dumps(data, indent=2)[:500])
else:
    print(f"❌ Error: {response.status_code}")
