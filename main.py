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
        # ============================================================================
        # PROCESAMIENTO DE IMAGEN
        # ============================================================================
        with st.spinner("🔍 Procesando imagen con Google Vision..."):
            img_bytes = uploaded_file.getvalue()
            matches = components['vision'].process_image(img_bytes)
            
            # Obtener texto raw para debug
            raw_text = ""
            try:
                from google.cloud import vision
                image = vision.Image(content=img_bytes)
                response = components['vision'].client.text_detection(image=image)
                if response.text_annotations:
                    raw_text = response.text_annotations[0].description
                    
                    # Detección de partido en vivo
                    if re.search(r"\d{1,2}['′]", raw_text) or re.search(r"\d+\s*-\s*\d+", raw_text):
                        st.info("🏟️ **Partido en tiempo real detectado** - Analizando con condiciones actuales")
            except Exception as e:
                if debug_mode:
                    st.warning(f"Nota: No se pudo obtener texto raw: {e}")
        
        # ============================================================================
        # MOSTRAR DEBUG MEJORADO (CON TU CÓDIGO)
        # ============================================================================
        if debug_mode:
            with st.expander("🔧 Debug OCR - Información de detección", expanded=True):
                st.write(f"**Partidos detectados:** {len(matches)}")
                
                if matches:
                    st.write("**Detalle de detecciones:**")
                    for i, m in enumerate(matches):
                        odds = m.get('all_odds', ['N/A', 'N/A', 'N/A'])
                        # ============================================================================
                        # TU CÓDIGO DE DEBUG MEJORADO
                        # ============================================================================
                        st.write(f"{i+1}. 🏠 {m['home']} vs 🚀 {m['away']}")
                        st.write(f"   📊 Odds: Local {odds[0]}, Empate {odds[1]}, Visitante {odds[2]}")
                        st.write("---")
                
                if raw_text:
                    st.write("**Texto raw detectado (primeros 500 caracteres):**")
                    st.code(raw_text)  # Cambiado a st.code para mejor formato
        
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
            
            # Preparar picks para EV Engine
            all_picks_for_ev = []
            all_picks_simple = []
            
            for i, match in enumerate(matches):
                home = match['home']
                away = match['away']
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    # Mostrar cuotas si están disponibles
                    if odds and odds[0] != 'N/A':
                        st.caption(f"🎲 **Cuotas:** Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    # Analizar el partido
                    analysis = components['analyzer'].analyze_match(home, away, "")
                    
                    # Mostrar resultados de búsqueda
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
                    
                    # Filtrar mercados
                    markets_filtered = [
                        m for m in analysis['markets'] 
                        if m['prob'] >= prob_minima and m['category'] in categorias
                    ]
                    
                    # Resaltar mercados especiales
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
                        
                        # Guardar para parlays simples
                        all_picks_simple.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['name'],
                            'prob': best['prob'],
                            'category': best['category']
                        })
                        
                        # Preparar picks para EV Engine
                        for idx, m in enumerate(markets_filtered[:5]):
                            odd_value = 2.0
                            
                            if odds and len(odds) > 0:
                                if 'Local' in m['name'] and odds[0] != 'N/A':
                                    odd_val = odds[0]
                                    if odd_val.startswith('+'):
                                        odd_value = (int(odd_val[1:]) / 100) + 1
                                    elif odd_val.startswith('-'):
                                        odd_value = (100 / abs(int(odd_val))) + 1
                                elif 'Visitante' in m['name'] and len(odds) > 2 and odds[2] != 'N/A':
                                    odd_val = odds[2]
                                    if odd_val.startswith('+'):
                                        odd_value = (int(odd_val[1:]) / 100) + 1
                                    elif odd_val.startswith('-'):
                                        odd_value = (100 / abs(int(odd_val))) + 1
                            
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
                    from modules.parlay_builder import show_parlay_options as show_simple_parlays
                    show_simple_parlays(all_picks_simple, components['tracker'])
                else:
                    st.info("ℹ️ No hay suficientes picks para generar parlays simples")
            
            with col_parlay2:
                st.subheader("📈 Parlays Optimizados (EV+)")
                if all_picks_for_ev:
                    smart_parlay = build_smart_parlay(all_picks_for_ev)
                    
                    if smart_parlay:
                        with st.container(border=True):
                            st.markdown("**🤖 Parlay Inteligente - Máximo EV**")
                            st.markdown(f"**Cuota Total:** {smart_parlay['total_odd']}")
                            st.markdown(f"**Probabilidad Combinada:** {smart_parlay['combined_prob']:.1%}")
                            st.markdown(f"**Valor Esperado (EV):** {smart_parlay['total_ev']:.2%}")
                            
                            if smart_parlay['total_ev'] > 0.2:
                                st.markdown("🟢 **EV Alto - Muy Recomendado**")
                            elif smart_parlay['total_ev'] > 0.1:
                                st.markdown("🟡 **EV Moderado - Recomendado**")
                            else:
                                st.markdown("🟠 **EV Bajo - Considerar riesgo**")
                            
                            st.markdown("**Selecciones:**")
                            for m in smart_parlay['matches']:
                                st.markdown(f"• {m}")
                            
                            if st.button("📝 Registrar este parlay", key="register_smart"):
                                components['tracker'].add_bet({
                                    'matches': smart_parlay['matches'],
                                    'total_odds': smart_parlay['total_odd'],
                                    'total_prob': smart_parlay['combined_prob']
                                }, stake=100)
                                st.success("✅ Parlay registrado!")
                                st.rerun()
                    else:
                        st.info("📭 No se encontraron parlays con EV positivo")
                        
                        st.caption("**Top picks individuales con mejor EV:**")
                        top_ev_picks = sorted(all_picks_for_ev, key=lambda x: x['ev'], reverse=True)[:5]
                        for p in top_ev_picks:
                            ev_color = "🟢" if p['ev'] > 0.1 else "🟡"
                            st.markdown(f"{ev_color} {p['match']}: {p['selection']} (EV: {p['ev']:.2%})")
                else:
                    st.info("ℹ️ No hay picks con EV suficiente")
        
        else:
            st.error("❌ No se detectaron partidos en la imagen")
            st.info("""
            **Sugerencias para mejorar la detección:**
            - Asegúrate que la imagen tenga buena resolución
            - Los nombres de equipos deben ser legibles
            - La imagen debe contener cuotas en formato americano (+120, -150)
            - Activa el debug para ver qué texto detectó el OCR
            """)
    
    else:
        st.info("👆 Sube una imagen para comenzar el análisis")
        
        with st.expander("📋 Formato esperado (ejemplo)"):
            st.code("""
[Equipo Local] [Cuota Local] [Empate] [Cuota Empate] [Equipo Visitante] [Cuota Visitante]

Ejemplos:
Real Madrid -278 Empate +340 Getafe +900
Rayo Vallecano -145 Empate +265 Real Oviedo +410
Celta de Vigo +330 Empate +290 Real Madrid -132
            """)
        
        with st.expander("ℹ️ Cómo funciona"):
            st.markdown("""
            ### 🎯 Flujo de análisis:
            
            1. **Subes una captura** de cualquier casa de apuestas
            2. **Google Vision OCR** detecta palabras con coordenadas
            3. **Algoritmo inteligente** busca patrón: EQUIPO + 3 ODDS + EQUIPO
            4. **Buscamos los equipos** en API-Sports
            5. **Simulación Monte Carlo** (20,000 iteraciones)
            6. **Analizamos 20+ mercados** por partido
            7. **Generamos parlays** con valor esperado positivo
            8. **Registramos apuestas** y tracking de resultados
            """)

if __name__ == "__main__":
    main()
