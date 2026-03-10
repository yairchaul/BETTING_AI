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
    rule_engine = RuleEngine()
    
    # Obtener procesador según deporte
    procesadores = {
        '⚽ Fútbol': SoccerProcessor(),
        '�� NBA': NBAProcessor(),
        '🥊 UFC': UFCProcessor()
    }
    
    with st.sidebar:
        st.header('⚙️ Configuración')
        deporte = st.radio(
            'Selecciona deporte',
            ['⚽ Fútbol', '🏀 NBA', '🥊 UFC'],
            index=0
        )
        
        st.divider()
        st.header('📊 Estadísticas')
        stats = tracker.get_stats()
        st.metric('Parlays', stats['total'])
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
            # PASO 1: Extraer texto de la imagen
            raw_lines = vision.process_image(uploaded.getvalue())
            
            # PASO 2: Normalización - convertir a Eventos
            processor = procesadores[deporte]
            eventos = processor.process(raw_lines)
            
            if not eventos:
                st.error('❌ No se detectaron eventos')
                return
            
            st.success(f"✅ {len(eventos)} eventos detectados")
            
            # PASO 3: Enriquecimiento - calcular probabilidades reales
            for evento in eventos:
                evento = stats_engine.enriquecer(evento)
                
                # Mostrar cada evento
                with st.expander(f"**{evento.local} vs {evento.visitante}**"):
                    # Mostrar odds originales
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Local", evento.odds.get('local', 'N/A'))
                    with col2:
                        st.metric("Empate", evento.odds.get('draw', 'N/A'))
                    with col3:
                        st.metric("Visitante", evento.odds.get('visitante', 'N/A'))
                    
                    # Mostrar mercados calculados
                    if evento.mercados:
                        st.markdown("**📊 Probabilidades calculadas:**")
                        cols = st.columns(3)
                        items = list(evento.mercados.items())[:6]
                        for i, (k, v) in enumerate(items):
                            with cols[i % 3]:
                                if isinstance(v, float):
                                    st.metric(k.replace('_', ' ').title(), f"{v:.1%}")
                    
                    # PASO 4: Aplicar reglas
                    picks = rule_engine.ejecutar(evento)
                    
                    if picks:
                        st.markdown("**🎯 Picks según reglas:**")
                        for pick in picks:
                            st.info(f"Nivel {pick['nivel']}: **{pick['mercado']}** ({pick['prob']:.1%})")
                            
                            if st.button(f"➕ Agregar", key=f"add_{evento.local}_{pick['nivel']}"):
                                tracker.add_pick(
                                    f"{evento.local} vs {evento.visitante}",
                                    pick['mercado'],
                                    pick['prob'],
                                    pick['nivel'],
                                    evento.deporte
                                )
                                st.rerun()
                    else:
                        st.warning("No se generaron picks para este evento")
    
    # Parlay
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
