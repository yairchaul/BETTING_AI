def validar_y_obtener_stats(nombre_equipo):
    try:
        api_key = st.secrets["football_api_key"]
        # Limpieza para que busque 'Kasimpasa' aunque escribas 'Kasimpasa vs'
        nombre_limpio = nombre_equipo.replace("FC", "").replace("Youth", "").replace("U19", "").strip()
        
        url = f"https://v3.football.api-sports.io/teams?search={nombre_limpio}"
        headers = {'x-apisports-key': api_key}
        
        response = requests.get(url, headers=headers).json()
        if response.get('results', 0) > 0:
            # Seleccionamos el resultado más parecido o el primero
            team_data = response['response'][0]['team']
            return {"nombre_real": team_data['name'], "logo": team_data['logo'], "id": team_data['id'], "valido": True}
        return {"valido": False}
    except:
        return {"valido": False}
