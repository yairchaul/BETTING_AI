#!/usr/bin/env python3
"""
Diagnóstico completo de la API-Football
"""
import requests
import json

API_KEY = "11eaff423a9042393b1fe21512384884"
BASE_URL = "https://v3.football.api-sports.io"
headers = {'x-apisports-key': API_KEY}

print("🔍 DIAGNÓSTICO COMPLETO DE API")
print("=" * 60)

# 1. Verificar estado de la cuenta
print("\n1️⃣ VERIFICANDO ESTADO DE LA CUENTA")
response = requests.get(f"{BASE_URL}/status", headers=headers)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2)[:500])  # Primeros 500 chars
else:
    print(f"Error: {response.text}")

# 2. Obtener países (CORREGIDO)
print("\n2️⃣ VERIFICANDO PAÍSES")
response = requests.get(f"{BASE_URL}/countries", headers=headers)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        print(f"✅ Lista de {len(data)} países")
        for i, pais in enumerate(data[:10]):
            print(f"   {i+1}. {pais.get('name', 'N/A')}")
    elif isinstance(data, dict) and 'response' in data:
        print(f"✅ {len(data['response'])} países")
        for i, pais in enumerate(data['response'][:10]):
            print(f"   {i+1}. {pais.get('name', 'N/A')}")
    else:
        print(f"Formato inesperado: {type(data)}")
        print(json.dumps(data, indent=2)[:500])
else:
    print(f"Error: {response.text}")

# 3. Verificar una liga específica (LaLiga)
print("\n3️⃣ VERIFICANDO LIGA (LaLiga ID: 140)")
response = requests.get(f"{BASE_URL}/leagues", headers=headers, params={'id': 140})
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2)[:500])
else:
    print(f"Error: {response.text}")

# 4. Verificar equipos de una liga
print("\n4️⃣ VERIFICANDO EQUIPOS DE LA LIGA ESPAÑOLA")
response = requests.get(f"{BASE_URL}/teams", headers=headers, params={'league': 140, 'season': 2025})
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        print(f"✅ {len(data)} equipos encontrados")
    elif isinstance(data, dict) and 'response' in data:
        print(f"✅ {len(data['response'])} equipos encontrados")
    else:
        print(f"Formato: {type(data)}")
else:
    print(f"Error: {response.text}")
