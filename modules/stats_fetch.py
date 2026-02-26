# modules/stats_fetch.py

def get_team_stats(home_name, away_name):
    """
    Simula o consulta la API para obtener el promedio de goles 
    de los últimos 5 partidos.
    """
    # Aquí irá tu lógica de API real. Por ahora devolvemos valores 
    # base para que el sistema sea funcional inmediatamente.
    return {
        'home_goals_avg': 1.6, 
        'away_goals_avg': 1.1,
        'home_form': 0.8, # 80% de efectividad últimos 5
        'away_form': 0.4
    }
