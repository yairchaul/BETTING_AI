# modules/football_api_client.py
import requests
import streamlit as st

class FootballAPIClient:
    """
    Cliente para Football-API (usando tu key existente)
    Obtiene estadísticas actuales de equipos
    """
    
    def __init__(self):
        self.api_key = st.secrets.get("FOOTBALL_API_KEY", "")
        self.headers = {'x-apisports-key': self.api_key}
        self.base_url = "https://v3.football.api-sports.io"

        # IDs de equipos (basados en pruebas anteriores)
        self.team_ids = {
            # Serie A
            'Napoles': 871, 'Napoli': 871, 'Cagliari': 718, 'Como': 1574,
            'Atalanta': 499, 'Udinese': 674, 'Juventus': 496, 'Pisa': 1653,
            'Lecce': 1654, 'Cremonese': 1649, 'Fiorentina': 502, 'Parma': 517,
            'Torino': 503,
            
            # Liga MX
            'Puebla': 2291, 'Tigres UANL': 2279, 'Monterrey': 2282,
            'Querétaro FC': 2290, 'Atlas': 2283, 'Tijuana': 2280,
            'América': 2287, 'FC Juárez': 2298, 'Guadalajara': 2278,
            'Cruz Azul': 2295, 'Pumas UNAM': 2286, 'Santos Laguna': 2285,
            'Club León': 2289, 'Pachuca': 2292, 'Necaxa': 2288,
            'Toluca': 2281, 'Mazatlán FC': 14002, 'Atlético San Luis': 2314,
            
            # Liga de Expansión MX (IDs aproximados - necesitas verificarlos)
            'CD Tapatío': 17330,
            'Venados FC': 17331,
            'Atlante': 17332,
            'Irapuato FC': 17333,
            'Club Atlético La Paz': 17334,
            'Jaiba Brava': 17335,
            'Correcaminos UAT': 17336,
            'Atlético Morelia': 17337,
            'Alebrijes de Oaxaca': 17338,
            'Dorados de Sinaloa': 17339,
            'Mineros de Zacatecas': 17340,
            'CD Tepatitlán de Morelos': 17341,
        }

    def get_team_stats(self, team_name, league_id=262, season=2025):
        """
        Obtiene estadísticas de un equipo.
        Busca en Liga MX (262) por defecto, pero ajusta según el equipo.
        """
        team_id = self.team_ids.get(team_name)
        if not team_id:
            return self._get_fallback_stats(team_name)

        # Determinar liga por equipo
        if team_name in ['Napoles', 'Cagliari', 'Atalanta', 'Juventus', 
                         'Lecce', 'Cremonese', 'Fiorentina', 'Parma', 
                         'Torino', 'Udinese', 'Pisa', 'Como']:
            league_id = 135  # Serie A
        elif team_name in ['CD Tapatío', 'Venados FC', 'Atlante', 'Irapuato FC',
                           'Club Atlético La Paz', 'Jaiba Brava', 'Correcaminos UAT',
                           'Atlético Morelia', 'Alebrijes de Oaxaca', 'Dorados de Sinaloa',
                           'Mineros de Zacatecas', 'CD Tepatitlán de Morelos']:
            league_id = 263  # Liga de Expansión MX

        try:
            url = f"{self.base_url}/teams/statistics"
            params = {"team": team_id, "season": season, "league": league_id}
            response = requests.get(url, headers=self.headers, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('response'):
                    stats = data['response']
                    gf_avg = stats.get('goals', {}).get('for', {}).get('average', {}).get('total', 1.35)
                    ga_avg = stats.get('goals', {}).get('against', {}).get('average', {}).get('total', 1.35)
                    return {
                        'avg_goals_scored': float(gf_avg),
                        'avg_goals_conceded': float(ga_avg),
                        'source': 'football-api',
                        'confidence': 0.9
                    }
        except Exception as e:
            print(f"Error API: {e}")

        return self._get_fallback_stats(team_name)

    def _get_fallback_stats(self, team_name):
        """Fallback con datos observados"""
        stats_db = {
            # Serie A
            'Napoles': {'gf': 1.8, 'ga': 1.1}, 'Cagliari': {'gf': 1.2, 'ga': 1.6},
            'Atalanta': {'gf': 1.7, 'ga': 1.3}, 'Juventus': {'gf': 1.6, 'ga': 0.9},
            'Udinese': {'gf': 1.3, 'ga': 1.4}, 'Torino': {'gf': 1.4, 'ga': 1.3},
            'Fiorentina': {'gf': 1.5, 'ga': 1.2}, 'Parma': {'gf': 1.2, 'ga': 1.5},
            
            # Liga MX
            'Puebla': {'gf': 1.2, 'ga': 1.4}, 'Tigres UANL': {'gf': 1.5, 'ga': 1.2},
            'Monterrey': {'gf': 1.6, 'ga': 1.1}, 'Querétaro FC': {'gf': 1.1, 'ga': 1.4},
            'Atlas': {'gf': 1.1, 'ga': 1.3}, 'Tijuana': {'gf': 1.3, 'ga': 1.2},
            'América': {'gf': 1.5, 'ga': 1.1}, 'FC Juárez': {'gf': 1.2, 'ga': 1.3},
            'Guadalajara': {'gf': 1.4, 'ga': 1.2}, 'Cruz Azul': {'gf': 1.4, 'ga': 1.2},
            'Pumas UNAM': {'gf': 1.3, 'ga': 1.3}, 'Santos Laguna': {'gf': 1.4, 'ga': 1.3},
            'Club León': {'gf': 1.4, 'ga': 1.3}, 'Pachuca': {'gf': 1.5, 'ga': 1.2},
            'Necaxa': {'gf': 1.2, 'ga': 1.4}, 'Toluca': {'gf': 1.3, 'ga': 1.3},
            'Mazatlán FC': {'gf': 1.2, 'ga': 1.4}, 'Atlético San Luis': {'gf': 1.2, 'ga': 1.3},
            
            # Liga de Expansión MX (valores estimados)
            'CD Tapatío': {'gf': 1.3, 'ga': 1.3},
            'Venados FC': {'gf': 1.2, 'ga': 1.4},
            'Atlante': {'gf': 1.4, 'ga': 1.2},
            'Irapuato FC': {'gf': 1.3, 'ga': 1.3},
            'Club Atlético La Paz': {'gf': 1.2, 'ga': 1.4},
            'Jaiba Brava': {'gf': 1.4, 'ga': 1.2},
            'Correcaminos UAT': {'gf': 1.2, 'ga': 1.4},
            'Atlético Morelia': {'gf': 1.4, 'ga': 1.2},
            'Alebrijes de Oaxaca': {'gf': 1.2, 'ga': 1.4},
            'Dorados de Sinaloa': {'gf': 1.3, 'ga': 1.3},
            'Mineros de Zacatecas': {'gf': 1.3, 'ga': 1.3},
            'CD Tepatitlán de Morelos': {'gf': 1.2, 'ga': 1.3},
        }
        
        stats = stats_db.get(team_name, {'gf': 1.35, 'ga': 1.35})
        return {
            'avg_goals_scored': stats['gf'],
            'avg_goals_conceded': stats['ga']
        }