# paso3_corregir_leon.py
import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

print(' BUSCANDO NOMBRE EXACTO DE LEÓN')
print('=' * 60)

variantes = [
    'Club León',
    'León',
    'Leon FC',
    'Club Leon',
    'León FC'
]

for variante in variantes:
    print(f'\n Probando: "{variante}"')
    url = "https://v3.football.api-sports.io/teams"
    params = {"search": variante}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('response') and len(data['response']) > 0:
                team = data['response'][0]['team']
                print(f'    ENCONTRADO: {team["name"]} (ID: {team["id"]})')
            else:
                print(f'    No encontrado')
    except Exception as e:
        print(f'    Error: {e}')

print('\n' + '=' * 60)
