# paso4_buscar_leon_por_pais.py
import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

print(' BUSCANDO TODOS LOS EQUIPOS DE MÉXICO PARA ENCONTRAR LEÓN')
print('=' * 70)

# Obtener TODOS los equipos de México
url = "https://v3.football.api-sports.io/teams"
params = {"country": "Mexico"}

try:
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        equipos = data.get('response', [])
        print(f' Total equipos en México: {len(equipos)}')
        
        print('\n BUSCANDO "LEÓN" EN LA LISTA:')
        print('-' * 50)
        
        encontrado = False
        for eq in equipos:
            team = eq['team']
            nombre = team['name']
            if 'leon' in nombre.lower() or 'león' in nombre.lower():
                print(f'    {nombre} (ID: {team["id"]})')
                encontrado = True
        
        if not encontrado:
            print(' No se encontró ningún equipo con "León" en el nombre')
            
            # Mostrar primeros 20 equipos para referencia
            print('\n PRIMEROS 20 EQUIPOS DE MÉXICO:')
            for i, eq in enumerate(equipos[:20]):
                team = eq['team']
                print(f'   {i+1}. {team["name"]} (ID: {team["id"]})')
    else:
        print(f' Error HTTP: {response.status_code}')
        
except Exception as e:
    print(f' Error: {e}')  #  CORREGIDO: comilla cerrada correctamente

print('\n' + '=' * 70)
