"""
MAIN VISION COMPLETO - Versión con Analizador Premium Profesional y UFC KO
NBA Props, UFC con análisis de KO y Fútbol con Triple Análisis para 100+ ligas
"""
import streamlit as st
from datetime import datetime

from espn_data_pipeline import ESPNDataPipeline
from bet_tracker import BetTracker
from visual_nba_mejorado import VisualNBAMejorado
from visual_ufc_mejorado import VisualUFCMejorado
from visual_futbol_triple import VisualFutbolTriple
from analizador_nba_mejorado import AnalizadorNBAMejorado
from analizador_gemini_nba import AnalizadorGeminiNBA
from analizador_premium_profesional import AnalizadorPremiumProfesional

# Módulos Fútbol Mejorados
from calculador_probabilidades_futbol import CalculadorProbabilidadesFutbol
from selector_mejor_opcion import SelectorMejorOpcion
from analizador_futbol_heurístico_mejorado import AnalizadorFutbolHeuristicoMejorado
from analizador_futbol_gemini_mejorado import AnalizadorFutbolGeminiMejorado
from analizador_futbol_premium import AnalizadorFutbolPremium

# Módulos UFC
from ufc_data_aggregator import UFCDataAggregator
from analizador_ufc_heurístico import AnalizadorUFCHuristico
from analizador_ufc_gemini import AnalizadorUFCGemini
from analizador_ufc_premium import AnalizadorUFCPremium

# 🔥 NUEVOS MÓDULOS UFC KO
from analizador_ufc_ko_pro import AnalizadorUFCKOPro
from visual_ufc_ko import VisualUFCKO

# Módulos NBA Props
from analizador_nba_props import AnalizadorNBAProps
from visual_nba_props import VisualNBAProps

# Gestor Universal de Ligas
from gestor_ligas_universal import GestorLigasUniversal
from espn_league_codes import ESPNLeagueCodes

# ============================================
# CONFIGURACIÓN
# ============================================
st.set_page_config(page_title="BETTING AI - TRIPLE ANÁLISIS + PROPS + KO", page_icon="🎯", layout="wide")

st.title("🎯 BETTING AI - NBA Props + UFC KO + Triple Análisis")
st.markdown(f"### 📅 {datetime.now().strftime('%d/%m/%Y')}")

def get_gemini_api_key():
    try:
        with open('.env', 'r') as f:
            for linea in f:
                if 'GEMINI_API_KEY' in linea:
                    return linea.split('=')[1].strip().strip('"').strip("'")
    except:
        return ""

GEMINI_API_KEY = get_gemini_api_key()

# ============================================
# LISTA COMPLETA DE LIGAS DE FÚTBOL
# ============================================
LIGAS_FUTBOL = ESPNLeagueCodes.obtener_todas()

def main():
    if 'init' not in st.session_state:
        st.session_state.espn = ESPNDataPipeline()
        st.session_state.tracker = BetTracker()
        st.session_state.visual_nba = VisualNBAMejorado()
        st.session_state.visual_ufc = VisualUFCMejorado()
        st.session_state.visual_futbol = VisualFutbolTriple()
        
        # Analizador Premium Profesional
        st.session_state.analizador_premium = AnalizadorPremiumProfesional()
        
        # Módulos Fútbol Premium
        st.session_state.analizador_futbol_premium = AnalizadorFutbolPremium()
        
        # Módulos UFC
        st.session_state.ufc_aggregator = UFCDataAggregator()
        st.session_state.analizador_ufc_premium = AnalizadorUFCPremium()
        
        # 🔥 NUEVOS MÓDULOS UFC KO
        st.session_state.analizador_ufc_ko = AnalizadorUFCKOPro()
        st.session_state.visual_ufc_ko = VisualUFCKO()
        
        # Módulos NBA Props
        st.session_state.analizador_props = AnalizadorNBAProps()
        st.session_state.visual_props = VisualNBAProps()
        
        # Gestor Universal de Ligas
        st.session_state.gestor_ligas = GestorLigasUniversal()
        
        if GEMINI_API_KEY:
            st.session_state.analizador_gemini = AnalizadorGeminiNBA(GEMINI_API_KEY)
            st.session_state.analizador_ufc_gemini = AnalizadorUFCGemini(GEMINI_API_KEY)
            st.session_state.analizador_futbol_gemini_mejorado = AnalizadorFutbolGeminiMejorado(GEMINI_API_KEY)
            st.success("✅ Gemini conectado para análisis")
        else:
            st.session_state.analizador_gemini = None
            st.session_state.analizador_ufc_gemini = None
            st.session_state.analizador_futbol_gemini_mejorado = None
            st.warning("⚠️ Gemini no disponible - Análisis limitado")
        
        # Data stores
        st.session_state.nba_partidos = []
        st.session_state.ufc_combates = []
        st.session_state.futbol_partidos = {}
        st.session_state.futbol_stats = {}
        
        # NBA analysis cache
        st.session_state.nba_analisis_heur = {}
        st.session_state.nba_analisis_gemini = {}
        st.session_state.nba_analisis_premium = {}
        
        # UFC data cache
        st.session_state.ufc_datos_peleadores = {}
        st.session_state.ufc_analisis_heur = {}
        st.session_state.ufc_analisis_gemini = {}
        st.session_state.ufc_analisis_premium = {}
        
        # Fútbol analysis cache
        st.session_state.futbol_analisis_heur = {}
        st.session_state.futbol_analisis_gemini = {}
        st.session_state.futbol_analisis_premium = {}
        
        st.session_state.init = True

    with st.sidebar:
        st.header("⚙️ CONTROLES")
        st.session_state.tracker.render_sidebar_tracker()
        st.markdown("---")
        
        # NBA
        if st.button("🏀 CARGAR NBA", use_container_width=True):
            with st.spinner("Cargando NBA..."):
                st.session_state.nba_partidos = st.session_state.espn.get_nba_games_with_odds()
                if st.session_state.nba_partidos:
                    st.session_state.nba_analisis_heur = {}
                    st.session_state.nba_analisis_gemini = {}
                    st.session_state.nba_analisis_premium = {}
                    st.success(f"✅ {len(st.session_state.nba_partidos)} partidos")
                else:
                    st.warning("⚠️ No hay partidos NBA hoy")
        
        # UFC
        if st.button("🥊 CARGAR UFC", use_container_width=True):
            with st.spinner("Cargando UFC y datos de peleadores..."):
                st.session_state.ufc_combates = st.session_state.espn.get_ufc_events()
                
                if st.session_state.ufc_combates:
                    st.session_state.ufc_datos_peleadores = {}
                    for idx, c in enumerate(st.session_state.ufc_combates):
                        if isinstance(c, dict):
                            p1 = c.get('peleador1', {}).get('nombre', '')
                            p2 = c.get('peleador2', {}).get('nombre', '')
                            
                            if p1 and p2:
                                datos_basicos = st.session_state.ufc_aggregator.get_fight_data(p1, p2, st.session_state.ufc_combates)
                                if datos_basicos:
                                    st.session_state.ufc_datos_peleadores[f"ufc_{idx}"] = datos_basicos
                    
                    st.session_state.ufc_analisis_heur = {}
                    st.session_state.ufc_analisis_gemini = {}
                    st.session_state.ufc_analisis_premium = {}
                    st.success(f"✅ {len(st.session_state.ufc_combates)} combates")
                else:
                    st.warning("⚠️ No hay eventos UFC disponibles")
        
        st.markdown("---")
        st.subheader("⚽ FÚTBOL (100+ LIGAS)")
        
        # Buscador de ligas
        buscar_liga = st.text_input("🔍 Buscar liga:", placeholder="Ej: México, Argentina, Premier...")
        
        # Filtrar ligas según búsqueda
        ligas_mostrar = LIGAS_FUTBOL
        if buscar_liga:
            ligas_mostrar = [l for l in LIGAS_FUTBOL if buscar_liga.lower() in l.lower()]
            st.caption(f"📊 {len(ligas_mostrar)} ligas encontradas")
        
        # Mostrar ligas en contenedor con scroll
        with st.container(height=400):
            for liga in sorted(ligas_mostrar)[:50]:
                if st.button(f"⚽ {liga[:40]}...", key=f"btn_{liga}", use_container_width=True):
                    with st.spinner(f"Cargando {liga}..."):
                        partidos = st.session_state.gestor_ligas.obtener_partidos(liga)
                        if partidos:
                            st.session_state.futbol_partidos[liga] = partidos
                            st.session_state.futbol_stats = {}
                            st.session_state.futbol_analisis_heur = {}
                            st.session_state.futbol_analisis_gemini = {}
                            st.session_state.futbol_analisis_premium = {}
                            st.success(f"✅ {len(partidos)} partidos")
                        else:
                            st.info(f"⚪ No hay partidos de {liga} hoy")
        
        if len(ligas_mostrar) > 50:
            st.caption(f"... y {len(ligas_mostrar) - 50} ligas más")
        
        if st.button("🧹 LIMPIAR CACHÉ", use_container_width=True):
            st.session_state.gestor_ligas.limpiar_cache()
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["🏀 NBA (TRIPLE ANÁLISIS + PROPS)", "🥊 UFC (TRIPLE ANÁLISIS + KO)", "⚽ FÚTBOL (TRIPLE ANÁLISIS)"])

    with tab1:  # NBA
        if st.session_state.nba_partidos:
            for idx, p in enumerate(st.session_state.nba_partidos):
                key = f"nba_{p['local']}_{p['visitante']}_{idx}"
                
                analisis_heur = st.session_state.nba_analisis_heur.get(key)
                analisis_gemini = st.session_state.nba_analisis_gemini.get(key)
                analisis_premium = st.session_state.nba_analisis_premium.get(key)
                
                accion = st.session_state.visual_nba.render(
                    p, idx,
                    tracker=st.session_state.tracker,
                    analisis_heurístico=analisis_heur,
                    analisis_gemini=analisis_gemini,
                    analisis_premium=analisis_premium
                )
                
                if accion == "analizar" and key not in st.session_state.nba_analisis_heur:
                    with st.spinner("📊 Ejecutando triple análisis NBA..."):
                        # Heurístico
                        analizador_heur = AnalizadorNBAMejorado(p)
                        resultado_heur = analizador_heur.analizar()
                        st.session_state.nba_analisis_heur[key] = resultado_heur
                        
                        # Premium PROFESIONAL con stats adicionales
                        try:
                            rec_local = p['records']['local'].split('-')
                            rec_visit = p['records']['visitante'].split('-')
                            partidos_local = int(rec_local[0]) + int(rec_local[1]) if len(rec_local) > 1 else 20
                            partidos_visit = int(rec_visit[0]) + int(rec_visit[1]) if len(rec_visit) > 1 else 20
                            partidos_jugados = (partidos_local + partidos_visit) // 2
                        except:
                            partidos_jugados = 20
                        
                        resultado_premium = st.session_state.analizador_premium.analizar(
                            p, 
                            resultado_heur,
                            stats_adicionales={'partidos_jugados': partidos_jugados}
                        )
                        st.session_state.nba_analisis_premium[key] = resultado_premium
                        
                        # Gemini
                        if st.session_state.analizador_gemini:
                            resultado_gemini = st.session_state.analizador_gemini.analizar(p)
                            st.session_state.nba_analisis_gemini[key] = resultado_gemini
                        
                        st.rerun()
                
                # Props de triples después del análisis tradicional
                if analisis_heur:
                    with st.expander("🏀 PROPS DE TRIPLES - Jugadores Destacados", expanded=False):
                        analisis_props = st.session_state.analizador_props.analizar_partido(p)
                        st.session_state.visual_props.render(
                            analisis_props, 
                            partido_info=f"{p['local']} vs {p['visitante']}"
                        )
        else:
            st.info("👈 Carga NBA en el sidebar")

    with tab2:  # UFC
        if st.session_state.ufc_combates:
            for idx, c in enumerate(st.session_state.ufc_combates):
                key = f"ufc_{idx}"
                
                datos_peleadores = st.session_state.ufc_datos_peleadores.get(key)
                
                analisis_heur = st.session_state.ufc_analisis_heur.get(key)
                analisis_gemini = st.session_state.ufc_analisis_gemini.get(key)
                analisis_premium = st.session_state.ufc_analisis_premium.get(key)
                
                accion = st.session_state.visual_ufc.render(
                    c, idx,
                    tracker=st.session_state.tracker,
                    datos_peleador1=datos_peleadores.get('peleador1') if datos_peleadores else None,
                    datos_peleador2=datos_peleadores.get('peleador2') if datos_peleadores else None,
                    analisis_heurístico=analisis_heur,
                    analisis_gemini=analisis_gemini,
                    analisis_premium=analisis_premium
                )
                
                if accion == "analizar" and key not in st.session_state.ufc_analisis_heur:
                    with st.spinner("🥊 Ejecutando triple análisis UFC..."):
                        
                        if datos_peleadores:
                            # Análisis heurístico
                            analizador_heur = AnalizadorUFCHuristico(
                                datos_peleadores['peleador1'], 
                                datos_peleadores['peleador2']
                            )
                            resultado_heur = analizador_heur.analizar()
                            st.session_state.ufc_analisis_heur[key] = resultado_heur
                            
                            # Análisis premium
                            resultado_premium = st.session_state.analizador_ufc_premium.analizar(
                                datos_peleadores['peleador1'],
                                datos_peleadores['peleador2'],
                                resultado_heur
                            )
                            st.session_state.ufc_analisis_premium[key] = resultado_premium
                            
                            # Análisis Gemini
                            if st.session_state.analizador_ufc_gemini:
                                resumen = analizador_heur.obtener_resumen()
                                resultado_gemini = st.session_state.analizador_ufc_gemini.analizar(
                                    datos_peleadores['peleador1'],
                                    datos_peleadores['peleador2'],
                                    resumen
                                )
                                st.session_state.ufc_analisis_gemini[key] = resultado_gemini
                            
                            # 🔥 NUEVO: Análisis de KO
                            with st.expander("💥 ANÁLISIS DE KO - Probabilidad de finalización", expanded=False):
                                analisis_ko = st.session_state.analizador_ufc_ko.analizar_ko_probability(
                                    datos_peleadores['peleador1'],
                                    datos_peleadores['peleador2']
                                )
                                
                                analisis_metodo = st.session_state.analizador_ufc_ko.analizar_metodo_victoria(
                                    datos_peleadores['peleador1'],
                                    datos_peleadores['peleador2']
                                )
                                
                                st.session_state.visual_ufc_ko.render(
                                    analisis_ko, 
                                    analisis_metodo,
                                    datos_peleadores['peleador1']['nombre'],
                                    datos_peleadores['peleador2']['nombre']
                                )
                            
                            st.rerun()
        else:
            st.info("👈 Carga UFC en el sidebar")

    with tab3:  # Fútbol con Gestor Universal
        if st.session_state.futbol_partidos:
            for liga, partidos in st.session_state.futbol_partidos.items():
                if partidos:
                    with st.expander(f"**{liga}** ({len(partidos)} partidos)", expanded=True):
                        for idx, p in enumerate(partidos):
                            key = f"fut_{liga}_{p['local']}_{p['visitante']}_{idx}"
                            
                            analisis_heur = st.session_state.futbol_analisis_heur.get(key)
                            analisis_gemini = st.session_state.futbol_analisis_gemini.get(key)
                            analisis_premium = st.session_state.futbol_analisis_premium.get(key)
                            
                            accion = st.session_state.visual_futbol.render(
                                p, idx, liga,
                                tracker=st.session_state.tracker,
                                stats_data=st.session_state.futbol_stats.get(key),
                                analisis_heurístico=analisis_heur,
                                analisis_gemini=analisis_gemini,
                                analisis_premium=analisis_premium
                            )
                            
                            if accion == "analizar" and key not in st.session_state.futbol_analisis_heur:
                                with st.spinner(f"📊 Analizando {p['local']} vs {p['visitante']}..."):
                                    
                                    stats_local = st.session_state.gestor_ligas.obtener_estadisticas_equipo(
                                        p['local'], liga
                                    )
                                    stats_visit = st.session_state.gestor_ligas.obtener_estadisticas_equipo(
                                        p['visitante'], liga
                                    )
                                    
                                    st.session_state.futbol_stats[key] = {
                                        'local': stats_local,
                                        'visitante': stats_visit
                                    }
                                    
                                    probabilidades = CalculadorProbabilidadesFutbol.calcular(stats_local, stats_visit)
                                    
                                    analizador_heur = AnalizadorFutbolHeuristicoMejorado(
                                        stats_local, 
                                        stats_visit,
                                        p['local'],
                                        p['visitante']
                                    )
                                    resultado_heur = analizador_heur.analizar()
                                    st.session_state.futbol_analisis_heur[key] = resultado_heur
                                    
                                    resultado_premium = st.session_state.analizador_futbol_premium.analizar(p, resultado_heur)
                                    st.session_state.futbol_analisis_premium[key] = resultado_premium
                                    
                                    if st.session_state.analizador_futbol_gemini_mejorado:
                                        resultado_gemini = st.session_state.analizador_futbol_gemini_mejorado.analizar(
                                            p, stats_local, stats_visit, probabilidades
                                        )
                                        st.session_state.futbol_analisis_gemini[key] = resultado_gemini
                                    
                                    st.rerun()
                else:
                    st.write(f"⚪ {liga}: No hay partidos hoy")
        else:
            st.info("👈 Carga ligas en el sidebar")

if __name__ == "__main__":
    main()
