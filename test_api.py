import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

print("🔍 DIAGNÓSTICO DE API-FOOTBALL")
print("=" * 60)

# 1. Verificar estado de la cuenta
print("\n📡 1. VERIFICANDO ESTADO DE LA API...")
url = "https://v3.football.api-sports.io/status"
try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Respuesta: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# 2. Probar con un endpoint simple
print("\n📡 2. PROBANDO ENDPOINT DE PAÍSES...")
url = "https://v3.football.api-sports.io/countries"
try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Países encontrados: {len(data.get('response', []))}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# 3. Probar ligas de México
print("\n📡 3. PROBANDO LIGAS DE MÉXICO...")
url = "https://v3.football.api-sports.io/leagues"
params = {"country": "Mexico"}
try:
    response = requests.get(url, headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Ligas encontradas: {len(data.get('response', []))}")
        if data.get('response'):
            for league in data['response']:
                print(f"  - {league['league']['name']} (ID: {league['league']['id']})")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
