# paso2_nombres_faltantes.py
import requests

API_KEY = '05b9723d89e43cf50594304fe3ee0f8e'
headers = {'x-apisports-key': API_KEY}

# Equipos que no funcionaron con sus posibles variantes
equipos_a_probar = {
    'Pumas': ['Pumas', 'UNAM', 'Club Universidad', 'Pumas UNAM', 'Universidad Nacional'],
    'Leon': ['Leon', 'León', 'Club León', 'Leon FC'],
    'Necaxa': ['Necaxa', 'Club Necaxa', 'Necaxa FC'],
    'Pachuca': ['Pachuca', 'C.F. Pachuca', 'Pachuca FC', 'Club Pachuca'],
    'Queretaro': ['Queretaro', 'Querétaro', 'Querétaro FC', 'Club Querétaro', 'Gallos Blancos'],
    'Juarez': ['Juarez', 'Juárez', 'FC Juárez', 'F.C. Juárez', 'Bravos'],
    'Tijuana': ['Tijuana', 'Club Tijuana', 'Xolos', 'Tijuana Xoloitzcuintles'],
    'Toluca': ['Toluca', 'Deportivo Toluca', 'Toluca FC', 'Club Toluca'],
    'Mazatlan': ['Mazatlan', 'Mazatlán', 'Mazatlán FC', 'Mazatlán F.C.']
}

print(' BUSCANDO NOMBRES EXACTOS PARA EQUIPOS FALTANTES')
print('=' * 70)

for equipo, variantes in equipos_a_probar.items():
    print(f'\n {equipo}:')
    print('-' * 40)
    
    encontrado = False
    for variante in variantes:
        print(f'   Probando: "{variante}"', end='')
        url = "https://v3.football.api-sports.io/teams"
        params = {"search": variante}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('response') and len(data['response']) > 0:
                    team = data['response'][0]['team']
                    print(f'   ENCONTRADO: {team["name"]} (ID: {team["id"]})')
                    encontrado = True
                    break
                else:
                    print('   No encontrado')
            else:
                print(f'   Error {response.status_code}')
        except Exception as e:
            print(f'   Error: {e}')
    
    if not encontrado:
        print('     No se encontró ninguna variante')

print('\n' + '=' * 70)
