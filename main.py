import streamlit as st
import pandas as pd
import re
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
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
        'groq_vision': GroqVisionParser() if st.secrets.get("GROQ_API_KEY") else None,
        'analyzer': MatchAnalyzer(st.secrets.get("FOOTBALL_API_KEY", "")),
        'tracker': BettingTracker(),
        'matcher': TeamMatcher(st.secrets.get("FOOTBALL_API_KEY", ""))
    }

components = init_components()

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
        
        # Configuración de EV Engine
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
        
        # Estado de las APIs
        col_api1, col_api2 = st.columns(2)
        with col_api1:
            if st.secrets.get("FOOTBALL_API_KEY"):
                st.success("⚽ API")
            else:
                st.warning("⚽ No API")
        
        with col_api2:
            if st.secrets.get("GROQ_API_KEY"):
                st.success("🤖 Groq")
            else:
                st.warning("🤖 No Groq")
        
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
        with st.spinner("🔍 Procesando imagen con IA..."):
            img_bytes = uploaded_file.getvalue()
            matches = []
            metodo_usado = "Ninguno"
            raw_text = ""
            
            if components['groq_vision']:
                try:
                    matches = components['groq_vision'].extract_matches_with_vision(img_bytes)
                    metodo_usado = "Groq Vision AI"
                    st.success(f"✅ Usando {metodo_usado}")
                except Exception as e:
                    st.warning(f"⚠️ Groq falló, usando OCR tradicional: {e}")
                    matches = components['vision'].process_image(img_bytes)
                    metodo_usado = "OCR Tradicional (fallback)"
            else:
                matches = components['vision'].process_image(img_bytes)
                metodo_usado = "OCR Tradicional"
            
            if not matches:
                try:
                    from google.cloud import vision
                    image = vision.Image(content=img_bytes)
                    response = components['vision'].client.text_detection(image=image)
                    if response.text_annotations:
                        raw_text = response.text_annotations[0].description
                except:
                    pass
        
        # ============================================================================
        # DEBUG MEJORADO: ESTRUCTURA DE 6 COLUMNAS
        # ============================================================================
        if debug_mode:
            with st.expander("🔧 Debug OCR - Estructura de 6 Columnas", expanded=True):
                st.write(f"**Método:** {metodo_usado} | **Detecciones:** {len(matches)}")
                
                if matches:
                    # Estilo CSS para la tabla de debug
                    st.markdown("""
                        <style>
                        .debug-table { width:100%; border-collapse: collapse; font-family: 'Courier New', Courier, monospace; font-size: 13px; }
                        .debug-table th { background-color: #2e3136; color: white; padding: 8px; border: 1px solid #444; text-align: center; }
                        .debug-table td { padding: 6px; border: 1px solid #eee; text-align: center; }
                        .col-name { text-align: left !important; font-weight: bold; background-color: #f9f9f9; }
                        .col-odd { color: #1565C0; font-weight: bold; background-color: #e3f2fd; }
                        </style>
                    """, unsafe_allow_html=True)

                    html = '<table class="debug-table"><tr>'
                    html += '<th>#</th><th>1. LOCAL</th><th>2. CUOTA L</th><th>3. EMPATE</th><th>4. CUOTA E</th><th>5. VISITANTE</th><th>6. CUOTA V</th></tr>'
                    
                    for i, m in enumerate(matches):
                        odds = m.get('all_odds', [])
                        # Aseguramos que existan 3 valores para las 6 columnas
                        o1 = odds[0] if len(odds) > 0 else "???"
                        o2 = odds[1] if len(odds) > 1 else "???"
                        o3 = odds[2] if len(odds) > 2 else "???"
                        
                        html += f"<tr>"
                        html += f"<td>{i+1}</td>"
                        html += f"<td class='col-name'>{m['home']}</td>"
                        html += f"<td class='col-odd'>{o1}</td>"
                        html += f"<td>Empate</td>"
                        html += f"<td class='col-odd'>{o2}</td>"
                        html += f"<td class='col-name'>{m['away']}</td>"
                        html += f"<td class='col-odd'>{o3}</td>"
                        html += "</tr>"
                    
                    html += "</table>"
                    st.markdown(html, unsafe_allow_html=True)
                
                if raw_text:
                    st.write("**Texto Raw (Primeros 500 caracteres):**")
                    st.code(raw_text[:500])

        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                df_data = []
                for m in matches:
                    odds = m.get('all_odds', ['N/A', 'N/A', 'N/A'])
                    df_data.append({
                        'Local': m['home'],
                        'Visitante': m['away'],
                        'Cuota L': odds[0] if len(odds) > 0 else 'N/A',
                        'Cuota E': odds[1] if len(odds) > 1 else 'N/A',
                        'Cuota V': odds[2] if len(odds) > 2 else 'N/A'
                    })
                st.dataframe(pd.DataFrame(df_data), use_container_width=True)
            
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
                            st.success(f"✅ Local encontrado: {analysis['home_team']}")
                        else:
                            st.warning(f"⚠️ Local: {home} (no encontrado en API)")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ Visitante encontrado: {analysis['away_team']}")
                        else:
                            st.warning(f"⚠️ Visitante: {away} (no encontrado en API)")
                    
                    markets_filtered = [
                        m for m in analysis['markets'] 
                        if m['prob'] >= prob_minima and m['category'] in categorias
                    ]
                    
                    if show_high_scoring:
                        for m in markets_filtered:
                            if 'Over 4.5' in m['name'] or 'Over 5.5' in m['name']:
                                m['highlight'] = True
                    
                    if markets_filtered:
                        st.caption(f"📊 Goles promedio esperados: {analysis['probabilidades']['goles_promedio']:.2f}")
                        
                        market_df = pd.DataFrame([{
                            'Mercado': ("🔴 " if m.get('highlight') else "") + m['name'],
                            'Probabilidad': f"{m['prob']:.1%}",
                            'Categoría': m['category']
                        } for m in markets_filtered[:10]])
                        
                        st.dataframe(market_df, use_container_width=True, hide_index=True)
                        
                        best = markets_filtered[0]
                        best_emoji = "🔴" if best.get('highlight') else "✨"
                        st.success(f"{best_emoji} **Mejor opción:** {best['name']} - {best['prob']:.1%}")
                        
                        all_picks_simple.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['name'],
                            'prob': best['prob'],
                            'category': best['category']
                        })
                        
                        for idx, m in enumerate(markets_filtered[:5]):
                            odd_value = 2.0
                            if odds and len(odds) > 0:
                                if 'Local' in m['name'] and odds[0] != 'N/A':
                                    odd_val = str(odds[0])
                                    if odd_val.startswith('+'): odd_value = (int(odd_val[1:]) / 100) + 1
                                    elif odd_val.startswith('-'): odd_value = (100 / abs(int(odd_val))) + 1
                                elif 'Visitante' in m['name'] and len(odds) > 2 and odds[2] != 'N/A':
                                    odd_val = str(odds[2])
                                    if odd_val.startswith('+'): odd_value = (int(odd_val[1:]) / 100) + 1
                                    elif odd_val.startswith('-'): odd_value = (100 / abs(int(odd_val))) + 1
                            
                            ev = (m['prob'] * odd_value) - 1
                            if ev > ev_minimo:
                                all_picks_for_ev.append({
                                    'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                                    'selection': m['name'],
                                    'probability': m['prob'],
                                    'odd': odd_value,
                                    'ev': ev,
                                    'category': m['category']
                                })
                    else:
                        st.info("📭 No hay mercados con los filtros seleccionados")
            
            # ============================================================================
            # GENERAR PARLAYS
            # ============================================================================
            st.divider()
            col_parlay1, col_parlay2 = st.columns(2)
            
            with col_parlay1:
                st.subheader("🎯 Parlays Simples")
                if all_picks_simple:
                    show_parlay_options(all_picks_simple, components['tracker'])
                else:
                    st.info("ℹ️ No hay picks suficientes")
            
            with col_parlay2:
                st.subheader("📈 Parlays Optimizados (EV+)")
                if all_picks_for_ev:
                    smart_parlay = build_smart_parlay(all_picks_for_ev)
                    if smart_parlay:
                        with st.container(border=True):
                            st.markdown(f"**🤖 Parlay Máximo EV: {smart_parlay['total_ev']:.2%}**")
                            st.markdown(f"Prob: {smart_parlay['combined_prob']:.1%} | Cuota: {smart_parlay['total_odd']}")
                            for m in smart_parlay['matches']:
                                st.markdown(f"• {m}")
                            if st.button("📝 Registrar", key="reg_smart"):
                                components['tracker'].add_bet(smart_parlay, stake=100)
                                st.rerun()
                else:
                    st.info("ℹ️ No hay picks con EV suficiente")
        else:
            st.error("❌ No se detectaron partidos")
    else:
        st.info("👆 Sube una imagen para comenzar")

if __name__ == "__main__":
    main()
