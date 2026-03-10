import streamlit as st
import pandas as pd

class SoccerVisionProcessor:
    def process_soccer(self, raw_lines):
        """Procesa líneas de fútbol y estructura partidos"""
        matches = []
        for line in raw_lines:
            # Buscar "Empate" para identificar el formato
            empate_index = -1
            for i, word in enumerate(line):
                if word == "Empate":
                    empate_index = i
                    break
            
            if empate_index > 0 and len(line) >= empate_index + 3:
                home = " ".join(line[:empate_index-1])
                home_odd = line[empate_index-1]
                away = " ".join(line[empate_index+2:-1])
                away_odd = line[-1]
                draw_odd = line[empate_index+1]
                
                matches.append({
                    'home': home,
                    'odd_h': home_odd,
                    'draw_odd': draw_odd,
                    'away': away,
                    'odd_a': away_odd
                })
        return matches

    def render_soccer_matches(self, matches):
        if not matches:
            st.error("❌ No se detectaron partidos")
            return
        
        st.success(f"✅ {len(matches)} partidos detectados")
        for i, m in enumerate(matches):
            with st.expander(f"**⚽ {m['home']} vs {m['away']}**", expanded=(i == 0)):
                df = pd.DataFrame({
                    '': ['LOCAL', 'EMPATE', 'VISITANTE'],
                    'EQUIPO': [m['home'], 'Empate', m['away']],
                    'CUOTA': [m['odd_h'], m['draw_odd'], m['odd_a']]
                })
                st.table(df.set_index(''))
