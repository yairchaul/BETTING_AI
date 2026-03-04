# paso1_verificar_nombres.py
import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

equipos = [
    'Puebla',
    'Tigres UANL',
    'Club America',
    'Guadalajara Chivas',
    'Cruz Azul',
    'U.N.A.M. - Pumas',
    'Monterrey',
    'Atletico Atlas',
    'Santos Laguna',
    'Atletico San Luis',
    'Leon',
    'Necaxa',
    'Pachuca',
    'Club Queretaro',
    'FC Juarez',
    'Club Tijuana',
    'Toluca',
    'Mazatlán'
]

print('🔍 VERIFICANDO NOMBRES EXACTOS EN API')
print('=' * 60)

for equipo in equipos:
    print(f'\n🔎 Buscando: "{equipo}"')
    url = "https://v3.football.api-sports.io/teams"
    params = {"search": equipo}
    
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
