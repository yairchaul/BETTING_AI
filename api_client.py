"""
Cliente API Definitivo - Con nombres correctos y caché
"""
import requests
import os
import json
from typing import List, Dict
from datetime import datetime, timedelta
from ufc_scraper_dinamico import UFCDynamicScraper

class OddsAPIClient:
    def __init__(self):
        self.api_key = os.getenv("ODDS_API_KEY", "98ccdb7d4c28042caa8bc8fe7ff6cc62")
        self.base_url = "https://api.the-odds-api.com/v4"
        self.ufc_scraper = UFCDynamicScraper()
        self.cache_dir = "api_cache"
        self.cache_duracion_horas = 6  # Cache de 6 horas para no abusar
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # ========================================
        # 🏆 NOMBRES OFICIALES DE LIGAS (VERIFICADOS)
        # ========================================
        self.leagues = [
            # MÉXICO
            'soccer_mexico_liga_mx',
            'soccer_mexico_liga_de_expansion_mx',
            
            # UEFA
            'soccer_uefa_champions_league',
            'soccer_uefa_europa_league',
            
            # TOP 5 (Nombres correctos)
            'soccer_spain_la_liga',
            'soccer_england_premier_league',     # ✅ CORRECTO (NO epl)
            'soccer_germany_bundesliga',
            'soccer_italy_serie_a',
            'soccer_france_ligue_1',              # ✅ CORRECTO (NO ligue_one)
            
            # OTRAS
            'soccer_netherlands_eredivisie',
            'soccer_portugal_primeira_liga',
            'soccer_belgium_first_div',
            'soccer_turkey_super_league',
            
            # NBA
            'basketball_nba'
        ]
        print(f"🔑 API Cliente Inicializado - {len(self.leagues)} ligas")

    def _get_cache_path(self, league):
        """Obtiene ruta de caché para una liga"""
        return os.path.join(self.cache_dir, f"{league.replace('/', '_')}.json")

    def _cargar_desde_cache(self, league):
        """Carga datos desde caché si son recientes"""
        cache_path = self._get_cache_path(league)
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            timestamp = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - timestamp < timedelta(hours=self.cache_duracion_horas):
                print(f"📦 Cargando {league} desde caché")
                return data['partidos']
        return None

    def _guardar_en_cache(self, league, partidos):
        """Guarda datos en caché"""
        cache_path = self._get_cache_path(league)
        data = {
            'timestamp': datetime.now().isoformat(),
            'partidos': partidos
        }
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def get_partidos_futbol(self) -> List[Dict]:
        """Obtiene partidos usando caché para no agotar API"""
        todos_partidos = []
        
        for league in self.leagues:
            if 'soccer' not in league:
                continue
            
            # Intentar cargar desde caché
            partidos_cache = self._cargar_desde_cache(league)
            if partidos_cache is not None:
                todos_partidos.extend(partidos_cache)
                continue
            
            # Si no hay caché, llamar a API
            url = f"{self.base_url}/sports/{league}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us,eu",  # USA y Europa = máxima cobertura
                "markets": "h2h",
                "oddsFormat": "decimal"
            }
            
            try:
                print(f"📡 Consultando {league}...")
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    partidos_league = []
                    
                    for item in data:
                        if not item.get('bookmakers'):
                            continue
                        
                        bookmaker = item['bookmakers'][0]
                        odds_dict = {}
                        for market in bookmaker['markets']:
                            if market['key'] == 'h2h':
                                for outcome in market['outcomes']:
                                    odds_dict[outcome['name']] = outcome['price']
                        
                        league_name = league.replace('soccer_', '').replace('_', ' ').upper()
                        
                        partido = {
                            'liga': league_name,
                            'local': item['home_team'],
                            'visitante': item['away_team'],
                            'odds_local': odds_dict.get(item['home_team'], 0),
                            'odds_empate': odds_dict.get('Draw', 0),
                            'odds_visitante': odds_dict.get(item['away_team'], 0),
                        }
                        partidos_league.append(partido)
                        todos_partidos.append(partido)
                    
                    # Guardar en caché
                    self._guardar_en_cache(league, partidos_league)
                    print(f"  ✅ {len(partidos_league)} partidos")
                    
                elif response.status_code == 401:
                    print(f"❌ API Key inválida o expirada")
                    return []
                elif response.status_code == 429:
                    print(f"❌ Límite de requests alcanzado - usando caché existente")
                    # Si hay caché viejo, usarlo de emergencia
                    if os.path.exists(self._get_cache_path(league)):
                        with open(self._get_cache_path(league), 'r') as f:
                            data = json.load(f)
                            todos_partidos.extend(data['partidos'])
                else:
                    print(f"⚠️ Error {response.status_code} en {league}")
                    
            except Exception as e:
                print(f"⚠️ Error en {league}: {e}")
        
        print(f"\n✅ TOTAL: {len(todos_partidos)} partidos de fútbol")
        return todos_partidos

    def get_partidos_nba(self) -> List[Dict]:
        """Obtiene partidos de NBA"""
        # Intentar caché primero
        cache_nba = self._cargar_desde_cache('basketball_nba')
        if cache_nba is not None:
            return cache_nba
        
        url = f"{self.base_url}/sports/basketball_nba/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us,eu",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "decimal"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {len(data)} partidos de NBA")
                
                partidos = []
                for item in data:
                    if not item.get('bookmakers'):
                        continue
                    bookmaker = item['bookmakers'][0]
                    odds = {'h2h': {}, 'spreads': {}, 'totals': {}}
                    
                    for market in bookmaker['markets']:
                        if market['key'] == 'h2h':
                            for outcome in market['outcomes']:
                                odds['h2h'][outcome['name']] = outcome['price']
                        elif market['key'] == 'spreads':
                            for outcome in market['outcomes']:
                                odds['spreads'][outcome['name']] = {
                                    'price': outcome['price'],
                                    'point': outcome.get('point', 0)
                                }
                        elif market['key'] == 'totals':
                            for outcome in market['outcomes']:
                                odds['totals'][outcome['name']] = {
                                    'price': outcome['price'],
                                    'point': outcome.get('point', 0)
                                }
                    
                    partidos.append({
                        'liga': 'NBA',
                        'local': item['home_team'],
                        'visitante': item['away_team'],
                        'odds': odds,
                    })
                
                # Guardar en caché
                self._guardar_en_cache('basketball_nba', partidos)
                return partidos
            else:
                return []
        except:
            return []
    
    def get_combates_ufc(self):
        """Obtiene cartelera UFC completa"""
        try:
            combates = self.ufc_scraper.get_next_event()
            return combates if combates else []
        except:
            return []
