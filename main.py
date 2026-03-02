import streamlit as st
import pandas as pd
import re
from modules.vision_reader import ImageParser
from modules.analyzer import MatchAnalyzer
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker
from modules.team_matcher import TeamMatcher
from modules.ev_engine import build_smart_parlay

st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache para mejorar rendimiento"""
    return {
        'vision': ImageParser(),
        'analyzer': MatchAnalyzer(st.secrets.get("FOOTBALL_API_KEY", "")),
        'tracker': BettingTracker(),
        'matcher': TeamMatcher(st.secrets.get("FOOTBALL_API_KEY", ""))
    }

components = init_components()

def parse_raw_betting_text(text):
    """
    Separa el texto raw pegado usando expresiones regulares avanzadas.
    Efectivo para casos como: 'Real Madrid-278 Empate+340Getafe+900'
    """
    # Regex optimizada:
    # ([a-zA-Z\s]+?) -> Nombre Local (non-greedy para no comerse números)
    # ([-+]\d+)      -> Cuota Local
    # \s*Empate\s* -> Palabra clave Empate
    # ([-+]\d+)      -> Cuota Empate
    # ([a-zA-Z\s]+?) -> Nombre Visitante
    # ([-+]\d+)      -> Cuota Visitante
    pattern = r"([a-zA-Z\s]+?)([-+]\d+)\s*Empate\s*([-+]\d+)([a-zA-Z\s]+?)([-+]\d+)"
    
    matches_found = re.findall(pattern, text)
    
    clean_list = []
    for m in matches_found:
        clean_list.append({
            'home': m[0].strip(),
            'away': m[3].strip(),
            'all_odds': [m[1], m[2], m[4]]
        })
    return clean_list

def main():
    st.title("🎯 Analizador Universal de Partidos")
    st.markdown("Sube una captura y analizo **partido por partido**")
    
    # ============================================================================
    # SIDEBAR CON CONFIGURACIÓN AVANZADA
    # ============================================================================
    with st.sidebar:
        st.header("⚙️ Configuración")
        prob_minima = st.slider("Probabilidad mínima", 0.0, 1.0, 0.5, 0.05)
        st.divider()
        categorias = st.multiselect(
            "Selecciona categorías",
            ["1X2", "Doble Oportunidad", "Totales", "Primer Tiempo", "BTTS", "Handicap"],
            default=["1X2", "Totales", "BTTS"]
        )
        ev_minimo = st.number_input("EV mínimo", 0.0, 1.0, 0.05, 0.01)
        debug_mode = st.checkbox("🔧 Mostrar debug OCR", value=True)
        components['tracker'].show_tracker_ui()
    
    # ============================================================================
    # PROCESAMIENTO DE IMAGEN
    # ============================================================================
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader("Selecciona imagen", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, caption="Imagen subida", use_container_width=True)
    
    if uploaded_file:
        with st.spinner("🔍 Extrayendo datos y limpiando texto..."):
            img_bytes = uploaded_file.getvalue()
            
            # 1. Obtener texto crudo de Google Vision
            raw_text = ""
            try:
                from google.cloud import vision
                image = vision.Image(content=img_bytes)
                response = components['vision'].client.text_detection(image=image)
                if response.text_annotations:
                    raw_text = response.text_annotations[0].description
            except Exception as e:
                st.error(f"Error OCR: {e}")

            # 2. Aplicar parseo Regex para limpiar el texto pegado
            matches = parse_raw_betting_text(raw_text)

        # ============================================================================
        # TABLA DE 6 COLUMNAS (ESTILO IMAGEN REQUERIDA)
        # ============================================================================
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                # Construcción del DataFrame para visualización limpia
                df_view = []
                for m in matches:
                    df_view.append({
                        'LOCAL': m['home'],
                        'CUOTA L': m['all_odds'][0],
                        'EMPATE': 'Empate',
                        'CUOTA E': m['all_odds'][1],
                        'VISITANTE': m['away'],
                        'CUOTA V': m['all_odds'][2]
                    })
                
                # Mostramos la tabla formateada (6 columnas)
                st.table(pd.DataFrame(df_view))

            if debug_mode:
                with st.expander("🔧 Ver Texto Raw Detectado"):
                    st.code(raw_text)

            # ============================================================================
            # ANÁLISIS POR PARTIDO Y EV ENGINE
            # ============================================================================
            st.divider()
            st.subheader("3. Análisis de IA y Valor Esperado")
            
            all_picks_for_ev = []
            all_picks_simple = []
            
            for i, match in enumerate(matches):
                home, away = match['home'], match['away']
                odds = match['all_odds']
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    analysis = components['analyzer'].analyze_match(home, away, "")
                    
                    # Mostrar mercados filtrados
                    markets_filtered = [m for m in analysis['markets'] if m['prob'] >= prob_minima]
                    
                    if markets_filtered:
                        m_df = pd.DataFrame([{
                            'Mercado': m['name'],
                            'Probabilidad': f"{m['prob']:.1%}",
                            'Categoría': m['category']
                        } for m in markets_filtered[:5]])
                        st.dataframe(m_df, use_container_width=True, hide_index=True)
                        
                        # Preparar datos para EV Engine
                        for m in markets_filtered[:3]:
                            # Lógica simple de conversión de cuota para EV
                            try:
                                o_val = int(odds[0]) if 'Local' in m['name'] else int(odds[2])
                                decimal_odd = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
                                ev = (m['prob'] * decimal_odd) - 1
                                
                                if ev > ev_minimo:
                                    all_picks_for_ev.append({
                                        'match': f"{home} vs {away}",
                                        'selection': m['name'],
                                        'probability': m['prob'],
                                        'odd': decimal_odd,
                                        'ev': ev
                                    })
                            except: pass

            # ============================================================================
            # GENERACIÓN DE PARLAYS
            # ============================================================================
            st.divider()
            cp1, cp2 = st.columns(2)
            with cp1:
                st.subheader("🎯 Parlays Recomendados")
                if matches: # Picks básicos basados en probabilidad
                    # (Lógica de parlay builder...)
                    pass
            
            with cp2:
                st.subheader("📈 Parlay Inteligente (EV+)")
                if all_picks_for_ev:
                    smart = build_smart_parlay(all_picks_for_ev)
                    if smart:
                        st.success(f"Cuota Total: {smart['total_odd']} | EV: {smart['total_ev']:.2%}")
        else:
            st.error("No se pudieron extraer partidos. Verifica que la imagen tenga el formato: Equipo + Cuotas.")
    else:
        st.info("Sube una captura para organizar los datos en columnas.")

if __name__ == "__main__":
    main()
