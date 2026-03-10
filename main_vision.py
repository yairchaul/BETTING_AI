import streamlit as st
import pandas as pd
import re
from datetime import datetime
from modules.vision_reader import ImageParser
from sports.soccer import SoccerProcessor
from sports.nba import NBAProcessor
from sports.ufc import UFCProcessor
from sports.ufc.vision_processor import UFCVisionProcessor

st.set_page_config(page_title='BETTING_AI', page_icon='🎯', layout='wide')

class ParlayTracker:
    def __init__(self):
        self.parlays = []
        self.current_picks = []
    
    def add_pick(self, partido, mercado, prob, nivel, deporte, ev=0):
        self.current_picks.append({
            'partido': partido,
            'mercado': mercado,
            'prob': prob,
            'nivel': nivel,
            'deporte': deporte,
            'ev': ev
        })
    
    def clear_picks(self):
        self.current_picks = []
    
    def build_parlay(self):
        if len(self.current_picks) < 2:
            return None
        prob_total = 1.0
        ev_total = 0.0
        for pick in self.current_picks:
            prob_total *= pick['prob']
            ev_total += pick['ev']
        return {'picks': self.current_picks.copy(), 'prob_total': prob_total, 'ev_total': ev_total}
    
    def get_stats(self):
        return {'total': len(self.parlays)}

def main():
    st.title('🎯 BETTING_AI - Analizador por Deportes')
    st.caption(f'📅 {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    
    tracker = ParlayTracker()
    vision = ImageParser()
    soccer = SoccerProcessor()
    nba = NBAProcessor()
    ufc = UFCProcessor()
    ufc_vision = UFCVisionProcessor()
    
    with st.sidebar:
        st.header('⚙️ Configuración')
        deporte = st.radio(
            'Selecciona deporte',
            ['⚽ Fútbol', '🏀 NBA', '🥊 UFC'],
            index=0
        )
        
        st.divider()
        st.header('📊 Estadísticas')
        st.metric('Parlays', tracker.get_stats()['total'])
        if st.button('🧹 Limpiar picks'):
            tracker.clear_picks()
            st.rerun()
    
    st.header(f"📸 Sube tu captura de {deporte}")
    uploaded = st.file_uploader(
        "Selecciona una imagen",
        type=['png','jpg','jpeg'],
        key=f"uploader_{deporte}"
    )
    
    if uploaded:
        st.image(uploaded, caption='Captura subida', use_container_width=True)
        
        with st.spinner(f'🔍 Analizando imagen...'):
            img_bytes = uploaded.getvalue()
            matches = vision.process_image(img_bytes)
            
            if deporte == '🥊 UFC':
                st.header('🥊 Análisis UFC - Procesamiento Visual')
                
                # Obtener texto crudo de matches
                texto_crudo = []
                for match in matches:
                    if isinstance(match, dict):
                        texto_crudo.extend(match.get('all_odds', []))
                    else:
                        texto_crudo.append(str(match))
                
                # Procesar con el vision processor específico
                peleas = ufc_vision.process_raw_text(texto_crudo)
                picks = ufc_vision.render_ufc_fights(peleas)
                
                # Aquí conectarías con tu modelo UFC
                # for pick in picks:
                #     tracker.add_pick(...)
                
            elif deporte == '🏀 NBA':
                st.header('🏀 Análisis NBA')
                texto_completo = ' '.join([str(m) for m in matches])
                lineas = texto_completo.split()
                games = nba.parse_games(lineas)
                
                for i, game in enumerate(games):
                    picks = nba.render_game(i, game)
                    for p in picks:
                        if st.button(f"➕ {p['mercado']}", key=f"nba_{i}_{p['nivel']}"):
                            tracker.add_pick(
                                f"{game['home']} vs {game['away']}",
                                p['mercado'], p['prob'], p['nivel'], 'NBA',
                                p.get('ev', 0)
                            )
                            st.rerun()
            
            else:  # Fútbol
                st.header('⚽ Análisis Fútbol')
                for i, match in enumerate(matches):
                    odds = match.get('all_odds', ['N/A', 'N/A', 'N/A'])
                    picks = soccer.render_match(
                        i,
                        match.get('home', 'Local'),
                        match.get('away', 'Visitante'),
                        odds
                    )
                    for p in picks:
                        if st.button(f"➕ {p['mercado']}", key=f"futbol_{i}_{p['nivel']}"):
                            tracker.add_pick(
                                f"{match.get('home', 'Local')} vs {match.get('away', 'Visitante')}",
                                p['mercado'], p['prob'], p['nivel'], 'Fútbol',
                                p.get('ev', 0)
                            )
                            st.rerun()
    
    if tracker.current_picks:
        st.divider()
        st.header('🎯 Parlay en construcción')
        df = pd.DataFrame(tracker.current_picks)
        st.dataframe(df, use_container_width=True)
        
        parlay = tracker.build_parlay()
        if parlay:
            col1, col2 = st.columns(2)
            with col1:
                st.metric('Probabilidad total', f"{parlay['prob_total']:.1%}")
            with col2:
                st.metric('EV total', f"{parlay['ev_total']:.1%}")
            
            if st.button('✅ Confirmar parlay'):
                tracker.parlays.append(parlay)
                tracker.clear_picks()
                st.balloons()
                st.rerun()

if __name__ == '__main__':
    main()
