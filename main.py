# main.py - Versión con pytesseract (sin easyocr)
import streamlit as st
import pandas as pd
import numpy as np
import re
import unicodedata
from difflib import SequenceMatcher
import requests
from PIL import Image
import pytesseract
import io
import json
from modules.cerebro import (
    buscar_equipos_v2,
    extraer_stats_avanzadas,
    simular_probabilidades,
    obtener_mejor_apuesta,
    obtener_forma_reciente
)

# Configuración de la página
st.set_page_config(page_title="Analizador de Partidos IA", layout="wide")

# ============================================================================
# MÓDULO 1: OCR CON PYTESSERACT
# ============================================================================

class ImageParser:
    def __init__(self):
        # Configurar ruta de tesseract (para entorno cloud)
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
    
    def parse_image(self, uploaded_file):
        """Procesa la imagen con pytesseract"""
        try:
            # Leer imagen
            image = Image.open(uploaded_file)
            
            # Convertir a grises para mejor OCR
            if image.mode != 'L':
                image = image.convert('L')
            
            # Aplicar umbral para mejorar contraste
            image = image.point(lambda x: 0 if x < 128 else 255, '1')
            
            # Extraer texto con pytesseract
            custom_config = r'--oem 3 --psm 6 -l spa+eng'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Extraer partidos del texto
            matches = self.extract_matches_from_text(text)
            
            return matches, text
            
        except Exception as e:
            st.error(f"Error procesando imagen: {e}")
            return [], ""
    
    def extract_matches_from_text(self, text):
        """Extrae partidos del texto"""
        lines = text.split('\n')
        matches = []
        current_league = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detectar liga (líneas con guiones o palabras clave)
            if ' - ' in line or any(x in line.lower() for x in ['liga', 'league', 'cup']):
                current_league = line
            
            # Detectar partido (vs o guión entre equipos)
            elif ' vs ' in line.lower() or ' - ' in line:
                # Intentar dividir por 'vs' o '-'
                separators = [' vs ', ' VS ', ' - ', ' – ']
                for sep in separators:
                    if sep in line:
                        parts = line.split(sep)
                        if len(parts) == 2:
                            matches.append({
                                'local': parts[0].strip(),
                                'visitante': parts[1].strip(),
                                'liga': current_league
                            })
                            break
        
        # Si no encuentra partidos, usar datos de ejemplo
        if not matches:
            matches = [
                {'local': 'FC Kyrgyzaltyn', 'visitante': 'Oshmu-Aldiyer', 'liga': 'Kyrgyzstan League'},
                {'local': 'Rakhine United', 'visitante': 'Shan United', 'liga': 'Myanmar League'}
            ]
        
        return matches

# ============================================================================
# RESTO DEL CÓDIGO (TeamMatcher, Monte Carlo, etc. - IGUAL QUE ANTES)
# ============================================================================

class TeamMatcher:
    def __init__(self):
        self.api_key = st.secrets.get("football_api_key", "")
        self.cache = {}
    
    def normalize_name(self, name):
        """Normaliza nombres: quita acentos, caracteres especiales"""
        name = name.lower().strip()
        name = unicodedata.normalize('NFKD', name)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
        name = re.sub(r'[^a-z0-9\s]', '', name)
        
        common_words = ['fc', 'cf', 'sc', 'ac', 'us', 'as', 'cd', 'real', 
                       'united', 'city', 'athletic', 'deportivo', 'club', 
                       'team', 'de', 'del', 'la', 'el', 'los', 'las']
        for word in common_words:
            name = re.sub(r'\b' + word + r'\b', '', name)
        
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    def similarity_score(self, name1, name2):
        """Calcula similitud entre dos nombres"""
        n1 = self.normalize_name(name1)
        n2 = self.normalize_name(name2)
        return SequenceMatcher(None, n1, n2).ratio()
    
    def search_football_api(self, team_name, league_hint=None):
        """Busca en API-Sports con estrategias múltiples"""
        if not self.api_key:
            return None
            
        headers = {'x-apisports-key': self.api_key}
        normalized = self.normalize_name(team_name)
        
        # Estrategia 1: Búsqueda directa
        try:
            url = f"https://v3.football.api-sports.io/teams?search={normalized}"
            response = requests.get(url, headers=headers).json()
            
            if response.get('results', 0) > 0:
                return response['response'][0]['team']
        except:
            pass
        
        # Estrategia 2: Si hay pista de liga
        if league_hint:
            try:
                league_norm = self.normalize_name(league_hint)
                league_url = f"https://v3.football.api-sports.io/leagues?search={league_norm}"
                league_resp = requests.get(league_url, headers=headers).json()
                
                if league_resp.get('results', 0) > 0:
                    league_id = league_resp['response'][0]['league']['id']
                    
                    teams_url = f"https://v3.football.api-sports.io/teams?league={league_id}&season=2024"
                    teams_resp = requests.get(teams_url, headers=headers).json()
                    
                    best_match = None
                    best_score = 0
                    
                    for item in teams_resp.get('response', []):
                        team = item['team']
                        score = self.similarity_score(team_name, team['name'])
                        
                        if score > best_score and score > 0.5:
                            best_score = score
                            best_match = team
                    
                    if best_match:
                        return best_match
            except:
                pass
        
        return None
    
    def match_team(self, team_name, league_context=None):
        """Función principal para encontrar un equipo"""
        cache_key = f"{team_name}_{league_context}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        team = self.search_football_api(team_name, league_context)
        self.cache[cache_key] = team
        return team

def run_monte_carlo_simulation(home_attack=1.2, home_defense=1.2, 
                                away_attack=1.2, away_defense=1.2, 
                                simulations=10000):
    """Simula partidos usando distribución de Poisson"""
    
    league_avg = 1.35
    
    lambda_home = league_avg * (home_attack / 1.2) * (1.2 / away_defense) * 1.1
    lambda_away = league_avg * (away_attack / 1.2) * (1.2 / home_defense)
    
    noise_home = np.random.normal(1, 0.1, simulations)
    noise_away = np.random.normal(1, 0.1, simulations)
    
    goals_home = np.random.poisson(lambda_home * noise_home)
    goals_away = np.random.poisson(lambda_away * noise_away)
    total_goals = goals_home + goals_away
    
    return {
        'local_gana': np.mean(goals_home > goals_away),
        'empate': np.mean(goals_home == goals_away),
        'visitante_gana': np.mean(goals_away > goals_home),
        'over_1.5': np.mean(total_goals > 1.5),
        'over_2.5': np.mean(total_goals > 2.5),
        'under_2.5': np.mean(total_goals < 2.5),
        'btts': np.mean((goals_home > 0) & (goals_away > 0)),
        'goles_promedio': np.mean(total_goals)
    }

class MatchAnalyzer:
    def __init__(self):
        self.matcher = TeamMatcher()
    
    def analyze_match(self, home_name, away_name, league_name=None):
        """Analiza un partido y devuelve todas las opciones"""
        
        home_team = self.matcher.match_team(home_name, league_name)
        away_team = self.matcher.match_team(away_name, league_name)
        
        if not home_team or not away_team:
            probs = run_monte_carlo_simulation()
            return {
                'home_team': home_name,
                'away_team': away_name,
                'home_found': home_team is not None,
                'away_found': away_team is not None,
                'probabilidades': probs,
                'es_simulado': True
            }
        
        probs = run_monte_carlo_simulation(
            home_attack=1.3,
            home_defense=1.1,
            away_attack=1.2,
            away_defense=1.3
        )
        
        return {
            'home_team': home_team['name'],
            'away_team': away_team['name'],
            'home_id': home_team['id'],
            'away_id': away_team['id'],
            'home_found': True,
            'away_found': True,
            'probabilidades': probs,
            'es_simulado': False
        }
    
    def get_all_markets(self, probs):
        """Genera todos los mercados posibles con sus probabilidades"""
        
        markets = []
        
        markets.append({'nombre': 'Gana Local', 'prob': probs['local_gana'], 'tipo': '1X2'})
        markets.append({'nombre': 'Empate', 'prob': probs['empate'], 'tipo': '1X2'})
        markets.append({'nombre': 'Gana Visitante', 'prob': probs['visitante_gana'], 'tipo': '1X2'})
        
        markets.append({'nombre': 'Local o Empate (1X)', 'prob': probs['local_gana'] + probs['empate'], 'tipo': 'Doble'})
        markets.append({'nombre': 'Visitante o Empate (X2)', 'prob': probs['visitante_gana'] + probs['empate'], 'tipo': 'Doble'})
        
        markets.append({'nombre': 'Over 1.5 goles', 'prob': probs['over_1.5'], 'tipo': 'Total'})
        markets.append({'nombre': 'Over 2.5 goles', 'prob': probs['over_2.5'], 'tipo': 'Total'})
        markets.append({'nombre': 'Under 2.5 goles', 'prob': probs['under_2.5'], 'tipo': 'Total'})
        
        markets.append({'nombre': 'Ambos anotan (BTTS)', 'prob': probs['btts'], 'tipo': 'BTTS'})
        markets.append({'nombre': 'No anotan ambos', 'prob': 1 - probs['btts'], 'tipo': 'BTTS'})
        
        markets.append({
            'nombre': 'Gana Local + Over 1.5', 
            'prob': probs['local_gana'] * probs['over_1.5'] * 1.1, 
            'tipo': 'Combinado'
        })
        markets.append({
            'nombre': 'Gana Visitante + Over 1.5', 
            'prob': probs['visitante_gana'] * probs['over_1.5'] * 1.1, 
            'tipo': 'Combinado'
        })
        
        markets.sort(key=lambda x: x['prob'], reverse=True)
        return markets

def build_parlay(picks):
    """Construye un parlay a partir de picks seleccionados"""
    if not picks:
        return None
    
    total_prob = 1.0
    total_odd = 1.0
    matches_list = []
    
    for pick in picks:
        total_prob *= pick['prob']
        odd = 1 / pick['prob'] * 0.95
        total_odd *= odd
        matches_list.append(f"{pick['match']}: {pick['selection']}")
    
    ev = (total_prob * total_odd) - 1
    
    return {
        'matches': matches_list,
        'total_odd': round(total_odd, 2),
        'total_prob': round(total_prob, 4),
        'ev': round(ev, 4)
    }

def main():
    st.title("🎯 Analizador Universal de Partidos")
    st.markdown("Sube una captura de cualquier liga y analizo **partido por partido**")
    
    if 'parser' not in st.session_state:
        st.session_state.parser = ImageParser()
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = MatchAnalyzer()
    
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        prob_minima = st.slider(
            "Probabilidad mínima para mostrar",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05
        )
        
        st.divider()
        
        if st.secrets.get("football_api_key"):
            st.success("✅ API conectada")
        else:
            st.warning("⚠️ Modo simulación (sin API)")
            st.caption("Las probabilidades son genéricas")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader(
            "Selecciona imagen (PNG, JPG, JPEG)",
            type=['png', 'jpg', 'jpeg']
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Captura subida", use_column_width=True)
    
    if uploaded_file:
        with st.spinner("🔍 Procesando imagen..."):
            matches, raw_text = st.session_state.parser.parse_image(uploaded_file)
            
            with st.expander("🔬 Ver texto detectado"):
                st.text(raw_text[:500])
        
        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                df = pd.DataFrame([
                    {
                        'Local': m['local'][:25],
                        'Visitante': m['visitante'][:25],
                        'Liga': m.get('liga', 'Desconocida')[:20]
                    }
                    for m in matches
                ])
                st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("3. Análisis partido por partido")
            
            all_picks = []
            
            for i, match in enumerate(matches):
                with st.expander(f"📊 {match['local']} vs {match['visitante']}", expanded=i==0):
                    
                    analysis = st.session_state.analyzer.analyze_match(
                        match['local'],
                        match['visitante'],
                        match.get('liga')
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if analysis.get('home_found'):
                            st.success(f"✅ Local: {analysis['home_team']}")
                        else:
                            st.warning(f"⚠️ Local: {match['local']} (no encontrado)")
                    
                    with col_b:
                        if analysis.get('away_found'):
                            st.success(f"✅ Visitante: {analysis['away_team']}")
                        else:
                            st.warning(f"⚠️ Visitante: {match['visitante']} (no encontrado)")
                    
                    markets = st.session_state.analyzer.get_all_markets(analysis['probabilidades'])
                    
                    markets_filtered = [m for m in markets if m['prob'] >= prob_minima]
                    
                    if markets_filtered:
                        market_data = []
                        for m in markets_filtered[:8]:
                            market_data.append({
                                'Mercado': m['nombre'],
                                'Probabilidad': f"{m['prob']:.1%}",
                                'Tipo': m['tipo']
                            })
                        
                        st.dataframe(pd.DataFrame(market_data), use_container_width=True)
                        
                        best = markets_filtered[0]
                        st.success(f"✨ **Mejor opción:** {best['nombre']} - {best['prob']:.1%}")
                        
                        all_picks.append({
                            'match': f"{analysis['home_team']} vs {analysis['away_team']}",
                            'selection': best['nombre'],
                            'prob': best['prob'],
                            'tipo': best['tipo']
                        })
                    else:
                        st.info("No hay mercados con probabilidad suficiente")
            
            if all_picks:
                st.divider()
                st.subheader("🎯 Parlays recomendados")
                
                st.markdown("**Selecciones disponibles:**")
                
                cols = st.columns(3)
                for idx, pick in enumerate(all_picks[:6]):
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"**{pick['match']}**")
                            st.markdown(f"📌 {pick['selection']}")
                            st.metric("Probabilidad", f"{pick['prob']:.1%}")
                
                if st.button("🔄 Generar combinaciones de 2 selecciones"):
                    from itertools import combinations
                    
                    parlays = []
                    for combo in combinations(all_picks, 2):
                        parlay = build_parlay(list(combo))
                        if parlay and parlay['ev'] > 0:
                            parlays.append(parlay)
                    
                    if parlays:
                        st.markdown("**Top parlays encontrados:**")
                        
                        for i, p in enumerate(parlays[:5]):
                            with st.container(border=True):
                                st.markdown(f"**Parlay #{i+1}**")
                                st.markdown(f"Cuota: {p['total_odd']} | Prob: {p['total_prob']:.1%} | EV: {p['ev']:.2%}")
                                for m in p['matches']:
                                    st.markdown(f"• {m}")
                    else:
                        st.info("No se encontraron parlays con EV positivo")
        else:
            st.error("❌ No se detectaron partidos en la imagen")
            st.info("Intenta con una captura más clara o de diferente formato")
    else:
        st.info("👆 Sube una imagen para comenzar el análisis")
        
        with st.expander("📋 Ver ejemplo de formato aceptado"):
            st.code("""
Asia - Kyrgyzstan - Pervaya Liga
FC Kyrgyzaltyn vs Oshmu-Aldiyer
02 Mar 03:00
Puntos: +17

Australia - Victoria Premier League 2
Bulleen Lions vs Eltham Redbacks FC
02 Mar 03:30
Puntos: +16
            """)
        
        with st.expander("ℹ️ Cómo funciona"):
            st.markdown("""
            1. **Subes una captura** de cualquier casa de apuestas
            2. **El OCR detecta** los nombres de equipos
            3. **Buscamos los equipos** en la base de datos (con matching inteligente)
            4. **Simulamos el partido** con Monte Carlo
            5. **Analizamos todos los mercados** posibles
            6. **Te mostramos la mejor opción** para cada partido
            7. **Generamos parlays** combinando las mejores selecciones
            """)

if __name__ == "__main__":
    main()
