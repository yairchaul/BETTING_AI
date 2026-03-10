import streamlit as st
import re
import pandas as pd

class UFCVisionProcessor:
    # Procesador visual específico para capturas de UFC
    
    def __init__(self):
        self.patterns = {
            'fighter_odds': re.compile(r'^([A-Za-zÀ-ÿ\s\-\.]+?)([+-]\d+)$'),
            'just_odds': re.compile(r'^([+-]\d+)$'),
            'just_name': re.compile(r'^([A-Za-zÀ-ÿ\s\-\.]+)$')
        }
    
    def process_raw_text(self, raw_lines):
        # Procesa las líneas de texto crudo y estructura las peleas
        peleas = []
        i = 0
        
        # Limpiar líneas
        lines = [line.strip() for line in raw_lines if line.strip() and not line.startswith('•')]
        
        st.write("📝 Líneas detectadas:", lines)  # Debug
        
        while i < len(lines) - 1:
            # Buscar patrón: peleador1, odds1, peleador2, odds2
            current = lines[i]
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            
            # Si la línea actual parece un nombre y la siguiente son odds
            if (not re.match(r'^[+-]', current) and 
                re.match(r'^[+-]', next_line)):
                
                fighter1 = current.strip('- •')
                odds1 = next_line
                
                # Buscar el siguiente par
                j = i + 2
                while j < len(lines) - 1:
                    if (not re.match(r'^[+-]', lines[j]) and 
                        re.match(r'^[+-]', lines[j + 1])):
                        fighter2 = lines[j].strip('- •')
                        odds2 = lines[j + 1]
                        
                        peleas.append({
                            'fighter1': fighter1,
                            'odds1': odds1,
                            'fighter2': fighter2,
                            'odds2': odds2
                        })
                        i = j + 2
                        break
                    j += 1
                else:
                    i += 1
            else:
                i += 1
        
        return peleas
    
    def render_ufc_fights(self, peleas):
        # Renderiza las peleas en formato UFC
        if not peleas:
            st.warning("No se pudieron estructurar las peleas correctamente")
            return []
        
        st.success(f"✅ {len(peleas)} peleas estructuradas")
        
        # Mostrar tabla de peleas
        df = pd.DataFrame(peleas)
        st.dataframe(df, use_container_width=True)
        
        picks_totales = []
        for i, pelea in enumerate(peleas):
            with st.expander(f"**🥊 {pelea['fighter1']} vs {pelea['fighter2']}**", expanded=(i == 0)):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### 🏠 **{pelea['fighter1']}**")
                    st.metric("Cuota", pelea['odds1'])
                with col2:
                    st.markdown(f"### 🚀 **{pelea['fighter2']}**")
                    st.metric("Cuota", pelea['odds2'])
                
                # Aquí iría el llamado a tu modelo UFC
                # picks = ufc_model.calcular(pelea)
                # picks_totales.extend(picks)
        
        return picks_totales
