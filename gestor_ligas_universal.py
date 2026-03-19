"""
GESTOR LIGAS UNIVERSAL - Administra TODAS las ligas con múltiples fuentes
"""
import streamlit as st
from datetime import datetime
import random

from espn_league_codes import ESPNLeagueCodes
from scraper_universal import ScraperUniversal

class GestorLigasUniversal:
    """
    Obtiene datos de cualquier liga usando:
    1. API de ESPN (si tiene código)
    2. Scraping (para ligas sin código)
    3. Datos simulados (fallback)
    """
    
    def __init__(self):
        self.scraper = ScraperUniversal()
        self.codigos_espn = ESPNLeagueCodes.CODIGOS_CONFIRMADOS
        self.cache_partidos = {}
        self.cache_stats = {}
        print("✅ Gestor Ligas Universal inicializado")
    
    def obtener_partidos(self, nombre_liga):
        """
        Obtiene partidos de una liga por su nombre
        """
        cache_key = f"{nombre_liga}_{datetime.now().strftime('%Y%m%d')}"
        
        if cache_key in self.cache_partidos:
            return self.cache_partidos[cache_key]
        
        partidos = []
        
        # 1. Intentar con código ESPN
        codigo = self.codigos_espn.get(nombre_liga)
        if codigo:
            try:
                from espn_futbol_data import ESPNFootballData
                espn = ESPNFootballData()
                partidos = espn.get_games_today(nombre_liga)
                if partidos:
                    self.cache_partidos[cache_key] = partidos
                    return partidos
            except:
                pass
        
        # 2. Intentar con scraping universal
        if codigo:
            partidos = self.scraper.obtener_partidos_hoy(codigo)
            if partidos:
                for p in partidos:
                    p['liga'] = nombre_liga
                self.cache_partidos[cache_key] = partidos
                return partidos
        
        # 3. Si no hay partidos, devolver lista vacía
        self.cache_partidos[cache_key] = []
        return []
    
    def obtener_estadisticas_equipo(self, nombre_equipo, nombre_liga):
        """
        Obtiene estadísticas de un equipo
        """
        cache_key = f"stats_{nombre_equipo}"
        
        if cache_key in self.cache_stats:
            return self.cache_stats[cache_key]
        
        # Intentar scraping
        stats = self.scraper.obtener_estadisticas_equipo(nombre_equipo)
        
        self.cache_stats[cache_key] = stats
        return stats
    
    def obtener_todas_ligas_disponibles(self):
        """
        Devuelve lista de todas las ligas (ESPN + pendientes)
        """
        from espn_league_codes import ESPNLeagueCodes
        return ESPNLeagueCodes.obtener_todas()
    
    def obtener_ligas_por_region(self, region):
        """
        Filtra ligas por región
        """
        regiones = {
            "México": ["México - Liga MX", "México - Liga de Expansión MX", "México - Liga MX Femenil"],
            "USA": ["MLS - Major League Soccer", "USA - US Open Cup", "USA - MLS Next Pro"],
            "Brasil": ["Brasil - Serie A", "Brasil - Serie B", "Brasil - Copa do Brasil", "Brasil - Copa do Nordeste"],
            "Argentina": ["Argentina - Liga Profesional", "Argentina - Primera Nacional", "Argentina - Copa Argentina"],
            "España": ["La Liga", "Segunda División", "Copa del Rey"],
            "Inglaterra": ["Inglaterra - Premier League", "Inglaterra - Championship", "Inglaterra - League One"],
            "Italia": ["Serie A", "Serie B", "Coppa Italia"],
            "Francia": ["Ligue 1", "Ligue 2", "Copa de Francia"],
            "Alemania": ["Bundesliga 1", "Bundesliga 2", "Bundesliga 3", "DFB Pokal"],
            "UEFA": ["UEFA - Champions League", "UEFA - Europa League", "UEFA - Europa Conference League"],
        }
        
        return regiones.get(region, [])
    
    def limpiar_cache(self):
        """Limpia la caché"""
        self.cache_partidos = {}
        self.cache_stats = {}
        st.success("✅ Caché limpiada")

# ============================================
# INTERFAZ DE PRUEBA
# ============================================
def main():
    st.set_page_config(page_title="Gestor Universal de Ligas", page_icon="🌎", layout="wide")
    
    st.title("🌎 Gestor Universal de Ligas")
    st.markdown("### Accede a datos de 100+ ligas sin APIs de pago")
    
    gestor = GestorLigasUniversal()
    
    col1, col2 = st.columns(2)
    
    with col1:
        region = st.selectbox("🌎 Selecciona región:", [
            "México", "USA", "Brasil", "Argentina", "España", 
            "Inglaterra", "Italia", "Francia", "Alemania", "UEFA"
        ])
        
        ligas = gestor.obtener_ligas_por_region(region)
        liga_seleccionada = st.selectbox("⚽ Selecciona liga:", ligas)
    
    with col2:
        st.info("""
        **Sistema Híbrido:**
        1. ✅ Liga MX, Premier, La Liga (ESPN)
        2. 🔄 Ligas secundarias (Scraping)
        3. ⚠️ Fallback simulado
        """)
    
    if st.button("🔍 CARGAR PARTIDOS", use_container_width=True):
        with st.spinner(f"Buscando partidos en {liga_seleccionada}..."):
            partidos = gestor.obtener_partidos(liga_seleccionada)
            
            if partidos:
                st.success(f"✅ {len(partidos)} partidos encontrados")
                for p in partidos:
                    st.write(f"- {p['local']} vs {p['visitante']} ({p.get('fecha', 'Hoy')})")
                    
                    # Obtener estadísticas del local como ejemplo
                    stats = gestor.obtener_estadisticas_equipo(p['local'], liga_seleccionada)
                    with st.expander(f"📊 Últimos 5 de {p['local']}"):
                        st.json(stats)
            else:
                st.warning("⚠️ No hay partidos hoy en esta liga")

if __name__ == "__main__":
    main()
