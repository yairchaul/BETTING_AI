import learning
import injuries

def analizar_con_inteligencia(datos_selenium):
    picks_finales = []
    
    for partido in datos_selenium:
        for m in partido['mercados']:
            # 1. Filtro de lesiones
            if not injuries.verificar_disponibilidad(m['jugador']):
                continue
            
            # 2. Cálculo de probabilidad real combinada (Momio + Learning)
            prob_stat = learning.calcular_probabilidad_real(m['jugador'], float(m['linea']), "Puntos")
            
            # 3. Solo si supera el 70% de confianza combinada
            if prob_stat >= 0.70:
                picks_finales.append({
                    "partido": partido['juego'],
                    "seleccion": f"{m['jugador']} Over {m['linea']}",
                    "confianza": prob_stat * 100,
                    "momio": m['momio']
                })
    return picks_finales
