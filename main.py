import streamlit as st
import pandas as pd
import re
import numpy as np
from modules.vision_reader import ImageParser
from modules.groq_vision import GroqVisionParser
from modules.parlay_builder import show_parlay_options
from modules.betting_tracker import BettingTracker
from modules.team_matcher import TeamMatcher
from modules.ev_engine import build_smart_parlay
from modules.hybrid_analyzer import HybridAnalyzer

st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

@st.cache_resource
def init_components():
    """Inicializa componentes con cache para mejorar rendimiento"""
    return {
        'vision': ImageParser(),
        'groq_vision': GroqVisionParser() if st.secrets.get("GROQ_API_KEY") else None,
        'analyzer': HybridAnalyzer(),
        'tracker': BettingTracker(),
        'matcher': TeamMatcher(st.secrets.get("FOOTBALL_API_KEY", ""))
    }

components = init_components()

def parse_raw_betting_text(text):
    """
    Separa el texto raw pegado usando expresiones regulares avanzadas.
    Efectivo para casos como: 'Real Madrid-278 Empate+340Getafe+900'
    """
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

def generar_parlay_seguro(matches_data):
    """
    Genera un parlay "seguro" basado en las mejores opciones de cada partido
    Siguiendo los parámetros: Resultado, BTTS, Over/Under, 1ra Mitad, Combinados
    """
    if not matches_data:
        return None
    
    # Categorías de apuestas a considerar (según los parámetros)
    categorias_prioritarias = [
        "Ambos anotan (BTTS)",
        "Over 1.5 goles",
        "Over 2.5 goles",
        "Over 0.5 goles (1T)",
        "Gana Local + Over 1.5",
        "Gana Visitante + Over 1.5",
        "BTTS + Over 2.5"
    ]
    
    selecciones = []
    
    for match in matches_data:
        home = match.get('home_team', match.get('home', ''))
        away = match.get('away_team', match.get('away', ''))
        markets = match.get('markets', [])
        odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
        
        if not markets:
            continue
        
        # Encontrar la mejor opción según categorías prioritarias
        mejor_opcion = None
        mejor_prob = 0
        
        for mercado in markets:
            nombre = mercado.get('name', '')
            prob = mercado.get('prob', 0)
            
            # Verificar si está en categorías prioritarias
            for cat in categorias_prioritarias:
                if cat.lower() in nombre.lower() and prob > mejor_prob and prob > 0.6:
                    mejor_prob = prob
                    mejor_opcion = mercado
                    break
        
        # Si no encontró en prioritarias, tomar la de mayor probabilidad
        if not mejor_opcion and markets:
            mejor_opcion = max(markets, key=lambda x: x.get('prob', 0))
        
        if mejor_opcion:
            # Calcular cuota aproximada
            odd_value = 2.0
            if 'Local' in mejor_opcion['name'] and odds[0] != 'N/A':
                o_val = int(odds[0])
                odd_value = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
            elif 'Visitante' in mejor_opcion['name'] and odds[2] != 'N/A':
                o_val = int(odds[2])
                odd_value = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
            
            selecciones.append({
                'match': f"{home} vs {away}",
                'selection': mejor_opcion['name'],
                'prob': mejor_opcion['prob'],
                'odd': odd_value,
                'category': mejor_opcion.get('category', '')
            })
    
    # Calcular probabilidad combinada del parlay
    if len(selecciones) >= 2:
        prob_combinada = np.prod([s['prob'] for s in selecciones])
        odd_combinada = np.prod([s['odd'] for s in selecciones])
        ev = (prob_combinada * odd_combinada) - 1
        
        return {
            'selecciones': selecciones,
            'probabilidad_total': prob_combinada,
            'cuota_total': round(odd_combinada, 2),
            'ev': round(ev, 4),
            'riesgo': 'BAJO' if prob_combinada > 0.3 else 'MEDIO' if prob_combinada > 0.15 else 'ALTO'
        }
    
    return None

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
                st.success("⚽ API Football")
            else:
                st.warning("⚽ No API Football")
        
        with col_api2:
            if st.secrets.get("GROQ_API_KEY"):
                st.success("🤖 Groq AI")
            else:
                st.warning("🤖 No Groq")
        
        # Mostrar estado de otras APIs
        if st.secrets.get("GOOGLE_API_KEY") and st.secrets.get("GOOGLE_CSE_ID"):
            st.success("🔍 Google CSE")
        else:
            st.warning("🔍 No Google CSE")
            
        if st.secrets.get("ODDS_API_KEY"):
            st.success("📊 Odds API")
        else:
            st.warning("📊 No Odds API")
        
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
        with st.spinner("🔍 Extrayendo datos y limpiando texto..."):
            img_bytes = uploaded_file.getvalue()
            matches = []
            metodo_usado = "Ninguno"
            raw_text = ""
            
            # INTENTO 1: Usar Groq Vision (si está disponible)
            if components['groq_vision']:
                try:
                    matches = components['groq_vision'].extract_matches_with_vision(img_bytes)
                    metodo_usado = "Groq Vision AI"
                    st.success(f"✅ Usando {metodo_usado}")
                except Exception as e:
                    st.warning(f"⚠️ Groq falló: {e}")
            
            # INTENTO 2: Usar parse_raw_betting_text
            if not matches:
                try:
                    from google.cloud import vision
                    image = vision.Image(content=img_bytes)
                    response = components['vision'].client.text_detection(image=image)
                    if response.text_annotations:
                        raw_text = response.text_annotations[0].description
                        matches = parse_raw_betting_text(raw_text)
                        metodo_usado = "Parseo Regex"
                        st.info(f"📝 Usando {metodo_usado}")
                except Exception as e:
                    st.error(f"Error en OCR: {e}")
            
            # INTENTO 3: Fallback al vision_reader tradicional
            if not matches:
                matches = components['vision'].process_image(img_bytes)
                metodo_usado = "Vision Reader"
                st.info(f"🔄 Usando {metodo_usado}")

        # ============================================================================
        # MOSTRAR PARTIDOS DETECTADOS
        # ============================================================================
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                df_view = []
                for m in matches:
                    odds = m.get('all_odds', ['N/A', 'N/A', 'N/A'])
                    df_view.append({
                        'LOCAL': m.get('home', m.get('local', 'N/A')),
                        'CUOTA L': odds[0],
                        'EMPATE': 'Empate',
                        'CUOTA E': odds[1],
                        'VISITANTE': m.get('away', m.get('visitante', 'N/A')),
                        'CUOTA V': odds[2]
                    })
                
                st.dataframe(pd.DataFrame(df_view), use_container_width=True, hide_index=True)

            # ============================================================================
            # DEBUG
            # ============================================================================
            if debug_mode:
                with st.expander("🔧 Debug OCR", expanded=True):
                    st.write(f"**Método:** {metodo_usado}")
                    st.write(f"**Partidos:** {len(matches)}")
                    
                    if raw_text:
                        st.write("**Texto raw:**")
                        st.code(raw_text[:500])

            # ============================================================================
            # ANÁLISIS HÍBRIDO (APIs + Groq)
            # ============================================================================
            st.divider()
            st.subheader("3. Análisis Híbrido (APIs + Groq AI)")
            
            all_picks_for_ev = []
            all_picks_simple = []
            matches_analizados = []
            
            for i, match in enumerate(matches):
                home = match.get('home', match.get('local', ''))
                away = match.get('away', match.get('visitante', ''))
                odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                
                with st.expander(f"📊 {home} vs {away}", expanded=i==0):
                    st.caption(f"🎲 **Cuotas:** Local {odds[0]} | Empate {odds[1]} | Visitante {odds[2]}")
                    
                    # Analizar con HybridAnalyzer
                    with st.spinner(f"🤖 Analizando {home} vs {away}..."):
                        analysis = components['analyzer'].analyze_match(home, away, odds)
                    
                    # Mostrar fuente del análisis
                    source = analysis.get('source', 'Desconocido')
                    st.info(f"📊 Fuente: {source}")
                    
                    # Mostrar resultados de búsqueda
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if analysis.get('home_found'):
                            st.success(f"✅ {analysis['home_team']}")
                        else:
                            st.warning(f"⚠️ {home}")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ {analysis['away_team']}")
                        else:
                            st.warning(f"⚠️ {away}")
                    
                    # Mostrar análisis de Groq si existe
                    if 'groq_analysis' in analysis:
                        with st.container(border=True):
                            st.markdown("**🤔 Análisis de Groq AI:**")
                            if 'liga' in analysis['groq_analysis']:
                                st.caption(f"Liga: {analysis['groq_analysis']['liga']}")
                            if 'explicacion' in analysis['groq_analysis']:
                                st.info(analysis['groq_analysis']['explicacion'])
                            if 'confianza' in analysis['groq_analysis']:
                                conf = analysis['groq_analysis']['confianza']
                                if conf == 'ALTA':
                                    st.success(f"Confianza: {conf}")
                                elif conf == 'MEDIA':
                                    st.warning(f"Confianza: {conf}")
                                else:
                                    st.error(f"Confianza: {conf}")
                    
                    # Mostrar mercados
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
                        
                        # Mejor opción
                        best = markets_filtered[0]
                        best_emoji = "🔴" if best.get('highlight') else "✨"
                        st.success(f"{best_emoji} **Mejor opción:** {best['name']} - {best['prob']:.1%}")
                        
                        # Guardar para parlays
                        match_data = {
                            'home_team': analysis['home_team'],
                            'away_team': analysis['away_team'],
                            'markets': markets_filtered,
                            'all_odds': odds,
                            'best_option': best
                        }
                        matches_analizados.append(match_data)
                        
                        all_picks_simple.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['name'],
                            'prob': best['prob'],
                            'category': best['category']
                        })
                        
                        # Preparar para EV
                        for m in markets_filtered[:3]:
                            try:
                                odd_value = 2.0
                                if 'Local' in m['name'] and odds[0] != 'N/A':
                                    o_val = int(odds[0])
                                    odd_value = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
                                elif 'Visitante' in m['name'] and odds[2] != 'N/A':
                                    o_val = int(odds[2])
                                    odd_value = (o_val/100)+1 if o_val > 0 else (100/abs(o_val))+1
                                
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
                            except:
                                pass
            
            # ============================================================================
            # GENERAR PARLAY SEGURO (EL QUE PEDISTE)
            # ============================================================================
            st.divider()
            st.subheader("🎯 Parlay Recomendado (Basado en análisis)")
            
            if matches_analizados:
                parlay_seguro = generar_parlay_seguro(matches_analizados)
                
                if parlay_seguro:
                    with st.container(border=True):
                        col_p1, col_p2, col_p3 = st.columns(3)
                        
                        with col_p1:
                            st.metric("Cuota Total", parlay_seguro['cuota_total'])
                        with col_p2:
                            st.metric("Probabilidad", f"{parlay_seguro['probabilidad_total']:.1%}")
                        with col_p3:
                            riesgo_color = "normal" if parlay_seguro['riesgo'] == 'BAJO' else "inverse"
                            st.metric("Riesgo", parlay_seguro['riesgo'], delta_color=riesgo_color)
                        
                        st.markdown("**Selecciones del parlay:**")
                        for s in parlay_seguro['selecciones']:
                            st.markdown(f"• {s['match']}: **{s['selection']}** (Prob: {s['prob']:.1%})")
                        
                        if st.button("📝 Registrar este parlay", key="register_seguro"):
                            components['tracker'].add_bet({
                                'matches': [s['match'] + ": " + s['selection'] for s in parlay_seguro['selecciones']],
                                'total_odds': parlay_seguro['cuota_total'],
                                'total_prob': parlay_seguro['probabilidad_total']
                            }, stake=100)
                            st.success("✅ Parlay registrado!")
                            st.rerun()
                else:
                    st.info("No se pudo generar un parlay con las selecciones actuales")
            
            # ============================================================================
            # OTROS PARLAYS (EV+ y Simples)
            # ============================================================================
            col_parlay1, col_parlay2 = st.columns(2)
            
            with col_parlay1:
                st.subheader("🎯 Parlays Simples")
                if all_picks_simple:
                    from modules.parlay_builder import show_parlay_options as show_simple_parlays
                    show_simple_parlays(all_picks_simple, components['tracker'])
                else:
                    st.info("ℹ️ No hay suficientes picks")
            
            with col_parlay2:
                st.subheader("📈 Parlays EV+")
                if all_picks_for_ev:
                    smart = build_smart_parlay(all_picks_for_ev)
                    if smart:
                        with st.container(border=True):
                            st.markdown(f"**Cuota:** {smart['total_odd']} | **EV:** {smart['total_ev']:.2%}")
                            for m in smart['matches']:
                                st.markdown(f"• {m}")
                            
                            if st.button("📝 Registrar", key="register_ev"):
                                components['tracker'].add_bet({
                                    'matches': smart['matches'],
                                    'total_odds': smart['total_odd'],
                                    'total_prob': smart['combined_prob']
                                }, stake=100)
                                st.success("✅ Registrado!")
                                st.rerun()
                    else:
                        st.info("No hay parlays con EV positivo")
        
        else:
            st.error("❌ No se detectaron partidos")
    
    else:
        st.info("👆 Sube una imagen para comenzar")
        
        with st.expander("📋 Formato esperado"):
            st.code("""
[Equipo Local] [Cuota L] [Empate] [Cuota E] [Equipo Visitante] [Cuota V]

Ejemplo:
Real Madrid -278 Empate +340 Getafe +900
            """)

if __name__ == "__main__":
    main()
