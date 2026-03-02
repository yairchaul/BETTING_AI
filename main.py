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
    Parsea texto raw pegado: 'Real Madrid-278 Empate+340Getafe+900'
    Retorna lista de diccionarios con estructura limpia.
    """
    # Expresión regular para separar: [Equipo] [Cuota] [Empate] [Cuota] [Equipo] [Cuota]
    # Maneja casos donde no hay espacios entre cuota y el siguiente nombre
    pattern = r"([a-zA-Z\s]+)([-+]\d+)\s*Empate\s*([-+]\d+)([a-zA-Z\s]+)([-+]\d+)"
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
        
        prob_minima = st.slider(
            "Probabilidad mínima", 
            min_value=0.0, 
            max_value=1.0, 
            value=0.5, 
            step=0.05,
            help="Solo muestra mercados con probabilidad mayor a este valor"
        )
        
        st.divider()
        
        st.subheader("🎲 Mercados a mostrar")
        categorias = st.multiselect(
            "Selecciona categorías",
            ["1X2", "Doble Oportunidad", "Totales", "Primer Tiempo", 
             "BTTS", "Handicap", "Goleador", "Combinado", "Totales (Especial)"],
            default=["1X2", "Totales", "Primer Tiempo", "BTTS", "Totales (Especial)"],
            help="Selecciona qué tipos de mercados quieres ver"
        )
        
        show_high_scoring = st.checkbox(
            "⚽ Enfatizar equipos goleadores", 
            value=True,
            help="Resalta mercados de Over 4.5 y Over 5.5 goles"
        )
        
        st.divider()
        
        st.subheader("📈 Valor Esperado (EV)")
        ev_minimo = st.number_input(
            "EV mínimo para considerar",
            min_value=0.0,
            max_value=1.0,
            value=0.05,
            step=0.01,
            format="%.2f",
            help="Solo picks con EV > este valor serán considerados"
        )
        
        max_picks_parlay = st.slider(
            "Máximo picks por parlay",
            min_value=2,
            max_value=6,
            value=5,
            help="Número máximo de selecciones en un parlay"
        )
        
        st.divider()
        
        if st.secrets.get("FOOTBALL_API_KEY"):
            st.success("✅ API conectada")
        else:
            st.warning("⚠️ Modo simulación")
        
        debug_mode = st.checkbox("🔧 Mostrar debug OCR", value=True)
        components['tracker'].show_tracker_ui()
    
    # ============================================================================
    # ÁREA PRINCIPAL
    # ============================================================================
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader(
            "Selecciona imagen", 
            type=['png', 'jpg', 'jpeg'],
            help="Sube una captura de pantalla con partidos y cuotas"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Imagen subida", use_container_width=True)
    
    if uploaded_file:
        with st.spinner("🔍 Procesando imagen con Google Vision..."):
            img_bytes = uploaded_file.getvalue()
            
            # 1. Intento de detección normal por coordenadas
            matches = components['vision'].process_image(img_bytes)
            
            # 2. Obtener texto raw para limpieza profunda
            raw_text = ""
            try:
                from google.cloud import vision
                image = vision.Image(content=img_bytes)
                response = components['vision'].client.text_detection(image=image)
                if response.text_annotations:
                    raw_text = response.text_annotations[0].description
                    
                    # SI LA DETECCIÓN NORMAL FALLÓ O VIENE VACÍA, USAMOS EL PARSEO POR REGEX
                    if not matches or len(matches) == 0:
                        matches = parse_raw_betting_text(raw_text)
                    
                    if re.search(r"\d{1,2}['′]", raw_text) or re.search(r"\d+\s*-\s*\d+", raw_text):
                        st.info("🏟️ **Partido en tiempo real detectado**")
            except Exception as e:
                if debug_mode:
                    st.warning(f"Nota: No se pudo obtener texto raw: {e}")
        
        # ============================================================================
        # TABLA DE 6 COLUMNAS (DEBUG / RESULTADOS)
        # ============================================================================
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                df_data = []
                for m in matches:
                    odds = m.get('all_odds', ['N/A', 'N/A', 'N/A'])
                    df_data.append({
                        'Local': m['home'],
                        'Cuota L': odds[0],
                        'Empate': 'Empate',
                        'Cuota E': odds[1],
                        'Visitante': m['away'],
                        'Cuota V': odds[2]
                    })
                st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)

            if debug_mode and raw_text:
                with st.expander("🔧 Ver Texto Raw Detectado"):
                    st.code(raw_text)

            st.divider()
            st.subheader("3. Análisis partido por partido")
            
            all_picks_for_ev = []
            all_picks_simple = []
            
            for i, match in enumerate(matches):
                home = match['home']
                away = match['away']
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    if odds and odds[0] != 'N/A':
                        st.caption(f"🎲 **Cuotas:** Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    analysis = components['analyzer'].analyze_match(home, away, "")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if analysis.get('home_found'):
                            st.success(f"✅ Local: {analysis['home_team']}")
                        else:
                            st.warning(f"⚠️ Local: {home}")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ Visitante: {analysis['away_team']}")
                        else:
                            st.warning(f"⚠️ Visitante: {away}")
                    
                    markets_filtered = [
                        m for m in analysis['markets'] 
                        if m['prob'] >= prob_minima and m['category'] in categorias
                    ]
                    
                    if markets_filtered:
                        st.caption(f"📊 Goles promedio esperados: {analysis['probabilidades']['goles_promedio']:.2f}")
                        
                        market_df = pd.DataFrame([{
                            'Mercado': ("🔴 " if m.get('highlight') else "") + m['name'],
                            'Probabilidad': f"{m['prob']:.1%}",
                            'Categoría': m['category']
                        } for m in markets_filtered[:10]])
                        
                        st.dataframe(market_df, use_container_width=True, hide_index=True)
                        
                        best = markets_filtered[0]
                        st.success(f"✨ **Mejor opción:** {best['name']} - {best['prob']:.1%}")
                        
                        all_picks_simple.append({
                            'match': f"{home} vs {away}",
                            'selection': best['name'],
                            'prob': best['prob'],
                            'category': best['category']
                        })
                        
                        # Cálculo de EV
                        for m in markets_filtered[:5]:
                            odd_value = 2.0 # Default
                            target_odd = "N/A"
                            
                            if 'Local' in m['name']: target_odd = odds[0]
                            elif 'Visitante' in m['name']: target_odd = odds[2]
                            elif 'Empate' in m['name']: target_odd = odds[1]

                            if target_odd != "N/A":
                                try:
                                    val = int(target_odd)
                                    odd_value = (val/100)+1 if val > 0 else (100/abs(val))+1
                                except: pass
                                
                                ev = (m['prob'] * odd_value) - 1
                                if ev > ev_minimo:
                                    all_picks_for_ev.append({
                                        'match': f"{home} vs {away}",
                                        'selection': m['name'],
                                        'probability': m['prob'],
                                        'odd': odd_value,
                                        'ev': ev
                                    })
                    else:
                        st.info("📭 Sin mercados para los filtros actuales")

            # ============================================================================
            # SECCIÓN PARLAYS
            # ============================================================================
            st.divider()
            cp1, cp2 = st.columns(2)
            
            with cp1:
                st.subheader("🎯 Parlays Simples")
                if all_picks_simple:
                    show_parlay_options(all_picks_simple, components['tracker'])
            
            with cp2:
                st.subheader("📈 Parlays Optimizados (EV+)")
                if all_picks_for_ev:
                    smart_parlay = build_smart_parlay(all_picks_for_ev)
                    if smart_parlay:
                        with st.container(border=True):
                            st.write(f"**Cuota Total:** {smart_parlay['total_odd']}")
                            st.write(f"**EV:** {smart_parlay['total_ev']:.2%}")
                            for m in smart_parlay['matches']:
                                st.write(f"• {m}")
        else:
            st.error("❌ No se detectaron partidos. Intenta con una imagen más clara.")

if __name__ == "__main__":
    main()
