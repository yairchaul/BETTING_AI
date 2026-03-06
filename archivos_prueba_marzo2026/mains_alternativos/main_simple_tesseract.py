import streamlit as st
import pandas as pd
import numpy as np
from modules.parser_caliente_doble_bloque import CalienteDobleBloqueParser
from modules.pro_analyzer_simple import ProAnalyzerSimple
from modules.odds_api_integrator import OddsAPIIntegrator
import pytesseract
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="Analizador de Apuestas", layout="wide")

if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

@st.cache_resource
def init_components():
    return {
        'parser': CalienteDobleBloqueParser(),
        'analyzer': ProAnalyzerSimple(),
        'odds_api': OddsAPIIntegrator()
    }

def american_to_decimal(american):
    if not american or american == 'N/A':
        return 2.0
    try:
        american = str(american).replace('+', '')
        american = int(american)
        if american > 0:
            return round(1 + (american / 100), 2)
        else:
            return round(1 + (100 / abs(american)), 2)
    except:
        return 2.0

def extract_text_with_tesseract(image_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            tmp.write(image_bytes.getvalue())
            tmp_path = tmp.name
        
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        tessdata_path = os.path.join(tempfile.gettempdir(), 'tessdata')
        os.environ['TESSDATA_PREFIX'] = tessdata_path
        
        image = Image.open(tmp_path)
        image = image.convert('L')
        image = image.point(lambda x: 0 if x < 128 else 255)
        
        text = pytesseract.image_to_string(image, lang='spa')
        os.unlink(tmp_path)
        return text
    except Exception as e:
        st.error(f"Error en OCR: {e}")
        return ""

def main():
    st.title(" Analizador Profesional de Apuestas")
    st.markdown("**Formato doble bloque - Caliente.mx**")

    with st.sidebar:
        st.header(" Configuración")
        bankroll = st.number_input("Bankroll ($)", min_value=100, max_value=10000, value=1000, step=100)
        min_ev = st.slider("EV mínimo", 0.0, 0.2, 0.05, 0.01)
        st.session_state.debug_mode = st.checkbox(" Modo debug", value=False)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("1. Sube tu captura")
        uploaded_file = st.file_uploader("Selecciona imagen", type=['png', 'jpg', 'jpeg'])
        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)

    if uploaded_file:
        with st.spinner(" Procesando imagen con Tesseract..."):
            text = extract_text_with_tesseract(uploaded_file)
            
            if st.session_state.debug_mode:
                st.write(" **TEXTO CRUDO:**")
                st.code(text)
            
            components = init_components()
            matches = components['parser'].parse_text(text)
            
            if matches:
                st.success(f" Partidos detectados: {len(matches)}")
            else:
                st.error(" No se detectaron partidos")

        if matches:
            with col2:
                st.subheader(f"2. Partidos detectados ({len(matches)})")
                
                df_view = []
                for m in matches:
                    df_view.append({
                        'LOCAL': m.get('local', 'N/A')[:15],
                        'L': m.get('cuota_local', 'N/A'),
                        'EMP': m.get('empate', 'N/A')[:5],
                        'E': m.get('cuota_empate', 'N/A'),
                        'VISITANTE': m.get('visitante', 'N/A')[:15],
                        'V': m.get('cuota_visitante', 'N/A')
                    })
                
                st.dataframe(pd.DataFrame(df_view), hide_index=True, use_container_width=True)

            st.divider()
            st.subheader("3. Análisis con datos REALES 2026")

            all_analisis = []
            
            for idx, match in enumerate(matches):
                home = match.get('local', '').strip()
                away = match.get('visitante', '').strip()
                
                odds_captura = {
                    'local': american_to_decimal(match.get('cuota_local', '')),
                    'draw': american_to_decimal(match.get('cuota_empate', '')),
                    'away': american_to_decimal(match.get('cuota_visitante', ''))
                }
                
                with st.expander(f" {home} vs {away}", expanded=(idx == 0)):
                    analisis = components['analyzer'].analyze_match(home, away, odds_captura)
                    all_analisis.append(analisis)
                    
                    st.caption(
                        f" Odds: Local **{analisis['odds_reales']['cuota_local']:.2f}** | "
                        f"Empate **{analisis['odds_reales']['cuota_empate']:.2f}** | "
                        f"Visitante **{analisis['odds_reales']['cuota_visitante']:.2f}**"
                    )
                    
                    col_p1, col_p2, col_p3 = st.columns(3)
                    with col_p1:
                        st.metric("Gana Local", f"{analisis['elo_probs']['home']:.1%}")
                    with col_p2:
                        st.metric("Empate", f"{analisis['elo_probs']['draw']:.1%}")
                    with col_p3:
                        st.metric("Gana Visitante", f"{analisis['elo_probs']['away']:.1%}")
                    
                    if analisis['value_bets']:
                        st.markdown("###  VALUE BETS")
                        vb_data = []
                        for vb in analisis['value_bets']:
                            vb_data.append({
                                'Mercado': vb['name'][:20],
                                'Prob': f"{vb['prob']:.1%}",
                                'Odds': f"{vb['odds']:.2f}",
                                'EV': f"+{vb['ev']:.1%}"
                            })
                        st.dataframe(pd.DataFrame(vb_data), hide_index=True, use_container_width=True)

if __name__ == "__main__":
    main()
