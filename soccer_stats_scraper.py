"""
Soccer Stats Scraper - Estadísticas REALES de equipos (xG, forma, etc.)
"""
import pandas as pd
import os
from datetime import datetime, timedelta
import time

class SoccerStatsScraper:
    """Extrae estadísticas de equipos con sistema de caché"""
    
    def __init__(self):
        self.cache_dir = "stats_cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # URLs de estadísticas por liga
        self.league_urls = {
            'LIGA_MX': 'https://fbref.com/en/comps/31/Liga-MX-Stats',
            'PREMIER_LEAGUE': 'https://fbref.com/en/comps/9/Premier-League-Stats',
            'LA_LIGA': 'https://fbref.com/en/comps/12/La-Liga-Stats',
            'CHAMPIONS_LEAGUE': 'https://fbref.com/en/comps/8/Champions-League-Stats',
            'SERIE_A': 'https://fbref.com/en/comps/11/Serie-A-Stats',
            'BUNDESLIGA': 'https://fbref.com/en/comps/20/Bundesliga-Stats',
            'LIGUE_1': 'https://fbref.com/en/comps/13/Ligue-1-Stats',
            'EREDIVISIE': 'https://fbref.com/en/comps/23/Eredivisie-Stats'
        }
        self.headers = {'User-Agent': 'Mozilla/5.0'}
    
    def get_league_stats(self, league_key: str):
        """
        Obtiene estadísticas de una liga con caché de 24 horas
        """
        cache_path = os.path.join(self.cache_dir, f"{league_key}.csv")
        
        # Verificar si existe caché válido
        if os.path.exists(cache_path):
            modified_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
            if datetime.now() - modified_time < timedelta(hours=24):
                print(f"📦 Cargando {league_key} desde caché")
                return pd.read_csv(cache_path)
        
        # Descargar nuevas estadísticas
        print(f"🌐 Descargando {league_key} desde FBRef...")
        try:
            # Pequeña pausa para no saturar el servidor
            time.sleep(2)
            
            tables = pd.read_html(self.league_urls[league_key])
            df = tables[0]
            
            # Limpiar columnas
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(0)
            
            # Seleccionar columnas relevantes
            cols_disponibles = [c for c in ['Squad', 'MP', 'W', 'D', 'L', 'GF', 'GA', 'xG', 'xGA'] if c in df.columns]
            df = df[cols_disponibles]
            
            # Guardar en caché
            df.to_csv(cache_path, index=False)
            return df
            
        except Exception as e:
            print(f"❌ Error descargando {league_key}: {e}")
            # Si falla, intentar usar caché viejo
            if os.path.exists(cache_path):
                return pd.read_csv(cache_path)
            return None
    
    def get_team_xg(self, league_key: str, team_name: str) -> float:
        """
        Obtiene el xG (goles esperados) de un equipo específico
        """
        df = self.get_league_stats(league_key)
        if df is None or 'xG' not in df.columns:
            return 1.5  # Valor por defecto
        
        # Buscar equipo (case insensitive)
        mask = df['Squad'].str.contains(team_name, case=False, na=False)
        if mask.any():
            xg_total = df.loc[mask, 'xG'].values[0]
            mp = df.loc[mask, 'MP'].values[0]
            return xg_total / mp if mp > 0 else 1.5
        
        return 1.5
