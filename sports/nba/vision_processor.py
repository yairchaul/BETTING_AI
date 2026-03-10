import streamlit as st
import pandas as pd

class NBAVisionProcessor:
    def process_nba(self, raw_lines):
        """Procesa líneas de NBA y estructura juegos"""
        games = []
        # Unificamos todas las palabras en una lista plana
        flat_data = [word for line in raw_lines for word in line]
        
        # Filtramos basura (Configuración, etc)
        data = [d for d in flat_data if len(d) > 1 and not any(x in d for x in ['Configuración', 'Estadísticas'])]
        
        # Cada equipo ocupa 6 campos en Caliente NBA
        for i in range(0, len(data) - 11, 12):
            try:
                games.append({
                    'home': data[i], 
                    'h_spread': data[i+1], 
                    'h_odds_spread': data[i+2],
                    'h_total': data[i+3], 
                    'h_odds_total': data[i+4],
                    'h_ml': data[i+5],
                    'away': data[i+6], 
                    'a_spread': data[i+7], 
                    'a_odds_spread': data[i+8],
                    'a_total': data[i+9], 
                    'a_odds_total': data[i+10],
                    'a_ml': data[i+11]
                })
            except:
                continue
        return games

    def render_nba_games(self, games):
        if not games:
            st.error("❌ No se detectaron juegos de NBA")
            return
        
        st.success(f"✅ {len(games)} juegos detectados")
        for i, g in enumerate(games):
            with st.expander(f"**🏀 {g['home']} vs {g['away']}**", expanded=(i == 0)):
                df = pd.DataFrame({
                    '': ['LOCAL', 'VISITANTE'],
                    'EQUIPO': [g['home'], g['away']],
                    'MONEYLINE': [g['h_ml'], g['a_ml']],
                    'SPREAD': [f"{g['h_spread']} ({g['h_odds_spread']})", f"{g['a_spread']} ({g['a_odds_spread']})"],
                    'TOTAL': [f"{g['h_total']} ({g['h_odds_total']})", f"{g['a_total']} ({g['a_odds_total']})"]
                })
                st.table(df.set_index(''))
