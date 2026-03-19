"""
ANALIZADOR GEMINI NBA - Versión corregida con clave apuesta
"""
import google.generativeai as genai
import json
import re
import streamlit as st

class AnalizadorGeminiNBA:
    def __init__(self, api_key):
        self.api_key = api_key
        self.disponible = False
        
        try:
            genai.configure(api_key=self.api_key)
            # Usar modelo estable
            self.model = genai.GenerativeModel('models/gemini-2.5-flash')
            self.disponible = True
            print("✅ Gemini NBA conectado")
        except Exception as e:
            st.warning(f"⚠️ Gemini no disponible: {e}")
    
    def analizar(self, partido):
        if not self.disponible:
            return {
                'apuesta': 'GEMINI NO DISPONIBLE',
                'ganador': 'N/A',
                'confianza': 0,
                'razones': [],
                'color': 'red'
            }
        
        local = partido['local']
        visitante = partido['visitante']
        records = partido.get('records', {})
        odds = partido.get('odds', {})
        
        # Extraer spread de forma segura
        spread_val = 0
        if isinstance(odds.get('spread'), dict):
            spread_val = odds['spread'].get('valor', 0)
        else:
            spread_val = odds.get('spread', 0)
        
        try:
            spread_num = float(spread_val)
        except:
            spread_num = 0
        
        # Calcular win rates
        wr_local = self._calcular_wr(records.get('local', '0-0'))
        wr_visit = self._calcular_wr(records.get('visitante', '0-0'))
        
        prompt = f"""
        Eres un analista de NBA con 20 años de experiencia. Analiza este partido:
        
        **{local} vs {visitante}**
        
        DATOS REALES:
        - Récord {local}: {records.get('local', '0-0')} (Win Rate: {wr_local:.1f}%)
        - Récord {visitante}: {records.get('visitante', '0-0')} (Win Rate: {wr_visit:.1f}%)
        - Diferencia de win rate: {abs(wr_local - wr_visit):.1f}%
        - Spread: {spread_num:+g}
        
        INSTRUCCIONES:
        1. Si los win rates son muy similares (<5% diferencia), indica que es un partido parejo
        2. Si hay clara diferencia (>10%), el favorito es el de mejor win rate
        3. Considera la ventaja de localía (+3% al local)
        
        Responde SOLO con JSON:
        {{
            "ganador": "{local} o {visitante}",
            "apuesta": "GANA X",
            "confianza": 65,
            "razones": ["razón 1", "razón 2"],
            "color": "green"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                resultado = json.loads(match.group(0))
                # Asegurar que tenga clave 'apuesta'
                if 'apuesta' not in resultado and 'ganador' in resultado:
                    resultado['apuesta'] = f"GANA {resultado['ganador']}"
                return resultado
        except Exception as e:
            st.warning(f"Error en Gemini: {e}")
        
        # Fallback al heurístico
        if wr_local > wr_visit + 5:
            ganador = local
            confianza = 60
        elif wr_visit > wr_local + 5:
            ganador = visitante
            confianza = 60
        else:
            ganador = local if wr_local > wr_visit else visitante
            confianza = 55
        
        return {
            'apuesta': f"GANA {ganador}",
            'ganador': ganador,
            'confianza': confianza,
            'razones': [f"Basado en win rates ({wr_local:.1f}% vs {wr_visit:.1f}%)"],
            'color': 'orange' if confianza > 55 else 'yellow'
        }
    
    def _calcular_wr(self, record_str):
        """Calcula win rate de string '45-23'"""
        try:
            parts = record_str.split('-')
            wins = int(parts[0])
            losses = int(parts[1])
            total = wins + losses
            return (wins / total * 100) if total > 0 else 50
        except:
            return 50
