# Dentro de modules/ev_engine.py

class EVEngine:
    def __init__(self):
        self.high_prob_threshold = 0.50 # Bajamos de 0.70 a 0.50 para pruebas
        self.top_n_picks = 5  

    def analyze_matches(self, datos_ia):
        """Analiza los datos de la IA buscando oportunidades de valor."""
        juegos = datos_ia.get("juegos", []) if isinstance(datos_ia, dict) else []
        df = pd.DataFrame(juegos)
        
        if df.empty: 
            return []

        picks = []
        for _, row in df.iterrows():
            try:
                # Limpieza robusta del momio para evitar ValueError
                raw_momio = str(row.get('moneyline', '100')).replace('+', '').strip()
                
                if not raw_momio or not raw_momio.lstrip('-').isdigit():
                    continue
                    
                momio = int(raw_momio)
                
                # Para la imagen f1f681, un momio de +125 con prob 0.52 da EV Positivo
                prob_modelo = 0.55 # Ajustamos a 0.55 para detectar valor real
                ev = calcular_ev(prob_modelo, momio)
                
                # Solo agregamos si el EV es mayor a 0
                if ev > 0:
                    picks.append({
                        "juego": f"{row.get('away', 'Visitante')} @ {row.get('home', 'Local')}",
                        "ev": ev,
                        "momio": momio,
                        "status": "🔥 VALOR" if ev > 0.05 else "LIGERO VALOR"
                    })
            except Exception:
                continue 
                
        return sorted(picks, key=lambda x: x["ev"], reverse=True)
