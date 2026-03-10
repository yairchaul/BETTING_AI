import streamlit as st
import pandas as pd
from datetime import datetime
from vision_reader import ImageParser
from sports.ufc.processor import UFCProcessor
from sports.nba.processor import NBAProcessor
from sports.soccer.processor import SoccerProcessor
from stats_engine import StatsEngine
from rule_engine import RuleEngine
from evento import Evento
from visual_futbol import VisualFutbol
from visual_nba import VisualNBA
from visual_ufc import VisualUFC

st.set_page_config(page_title='BETTING_AI - Motor de Apuestas', page_icon='🎯', layout='wide')

class ParlayTracker:
    def __init__(self):
        self.parlays = []
        self.current_picks = []
    
    def add_pick(self, partido, mercado, prob, nivel, deporte):
        self.current_picks.append({
            'partido': partido,
            'mercado': mercado,
            'prob': prob,
            'nivel': nivel,
            'deporte': deporte
        })
    
    def clear_picks(self):
        self.current_picks = []
    
    def build_parlay(self):
        if len(self.current_picks) < 2:
            return None
        prob_total = 1.0
        for pick in self.current_picks:
            prob_total *= pick['prob']
        return {'picks': self.current_picks.copy(), 'prob_total': prob_total}
    
    def get_stats(self):
        return {'total': len(self.parlays)}

def main():
    st.title('🎯 BETTING_AI - Motor Profesional de Apuestas')
    st.caption(f'📅 {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    
    tracker = ParlayTracker()
    vision = ImageParser()
    
    # Inicializar motores
    stats_engine = StatsEngine()
    
    # Inicializar visuales
    visual_futbol = VisualFutbol()
    visual_nba = VisualNBA()
    visual_ufc = VisualUFC()
    
    # Mapeo de deportes
    deporte_map = {
        '⚽ Fútbol': 'FUTBOL',
        '🏀 NBA': 'NBA',
        '🥊 UFC': 'UFC'
    }
    
    with st.sidebar:
        st.header('⚙️ Configuración')
        deporte_seleccionado = st.radio(
            'Selecciona deporte',
            ['⚽ Fútbol', '🏀 NBA', '🥊 UFC'],
            index=0
        )
        deporte = deporte_map[deporte_seleccionado]
        
        st.divider()
        st.header('📊 Estadísticas')
        stats = tracker.get_stats()
        st.metric('Parlays', stats['total'])
        if st.button('🧹 Limpiar picks'):
            tracker.clear_picks()
            st.rerun()
    
    st.header(f"📸 Sube tu captura de {deporte_seleccionado}")
    uploaded = st.file_uploader(
        "Selecciona una imagen",
        type=['png','jpg','jpeg'],
        key=f"uploader_{deporte}"
    )
    
    if uploaded:
        st.image(uploaded, caption='Captura subida', use_container_width=True)
        
        with st.spinner(f'🔍 Analizando imagen...'):
            raw_lines = vision.process_image(uploaded.getvalue())
            
            if deporte == 'FUTBOL':
                processor = SoccerProcessor()
            elif deporte == 'NBA':
                processor = NBAProcessor()
            elif deporte == 'UFC':
                processor = UFCProcessor()
            
            eventos = processor.process(raw_lines)
            
            if not eventos:
                st.error('❌ No se detectaron eventos')
                return
            
            st.success(f"✅ {len(eventos)} eventos detectados")
            
            for idx, evento in enumerate(eventos):
                evento.deporte = deporte
                evento = stats_engine.enriquecer(evento)
                
                # Usar el visual correspondiente
                if deporte == 'FUTBOL':
                    visual_futbol.render(evento, idx, tracker)
                elif deporte == 'NBA':
                    visual_nba.render(evento, idx, tracker)
                elif deporte == 'UFC':
                    visual_ufc.render(evento, idx, tracker)
    
    if tracker.current_picks:
        st.divider()
        st.header('🎯 Parlay en construcción')
        df = pd.DataFrame(tracker.current_picks)
        st.dataframe(df, use_container_width=True)
        
        parlay = tracker.build_parlay()
        if parlay:
            st.metric('Probabilidad total', f"{parlay['prob_total']:.1%}")
            if st.button('✅ Confirmar parlay'):
                st.balloons()
                tracker.parlays.append(parlay)
                tracker.clear_picks()
                st.rerun()

if __name__ == '__main__':
    main()
