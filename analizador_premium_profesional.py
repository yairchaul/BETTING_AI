"""
ANALIZADOR PREMIUM PROFESIONAL - Edge Rating, No-Vig Odds, RLM, Sharps Detection
Versión profesional con limpieza de vig y ajuste por volumen
"""
import streamlit as st
import random
import math

class AnalizadorPremiumProfesional:
    """
    Analizador premium de nivel profesional que incorpora:
    - Edge Rating basado en probabilidad real (sin vig)
    - Public Money vs Sharp Money
    - Reverse Line Movement (RLM) detection
    - Ajuste por volumen de partidos
    - Detección de valor profesional
    """
    
    def __init__(self):
        print("✅ Analizador Premium Profesional inicializado")
    
    def _american_to_prob(self, american_odds):
        """
        Convierte odds americanos a probabilidad implícita (%)
        Ejemplo: -218 -> 68.6%, +180 -> 35.7%
        """
        try:
            if isinstance(american_odds, str):
                american_odds = american_odds.replace('+', '')
            odds = int(american_odds)
            
            if odds > 0:
                return 100 / (odds + 100) * 100
            else:
                return abs(odds) / (abs(odds) + 100) * 100
        except:
            return 50
    
    def _limpiar_vig(self, prob_local, prob_visit):
        """
        Elimina la comisión de la casa (vig) para obtener probabilidad real
        Fórmula: prob_real = prob_sucia / (total/100)
        """
        total = prob_local + prob_visit
        
        # Si la suma es menor a 100, ya está limpio
        if total <= 100:
            return prob_local, prob_visit
        
        # Limpiar vig (si total = 106, dividir entre 1.06)
        factor = total / 100
        prob_real_local = prob_local / factor
        prob_real_visit = prob_visit / factor
        
        return round(prob_real_local, 2), round(prob_real_visit, 2)
    
    def _calcular_overround(self, prob_local, prob_visit):
        """
        Calcula la comisión de la casa (vig)
        """
        return round((prob_local + prob_visit) - 100, 2)
    
    def _ajustar_por_volumen(self, edge_base, partidos_jugados):
        """
        Ajusta el edge según el volumen de datos
        """
        # Máxima confianza tras 20 partidos
        factor_confianza = min(1.0, partidos_jugados / 20)
        return edge_base * factor_confianza
    
    def analizar(self, partido, resultado_heurístico, stats_adicionales=None):
        """
        Genera análisis premium con métricas profesionales
        
        Args:
            partido: Datos del partido (local, visitante, odds actuales)
            resultado_heurístico: Resultado del análisis heurístico
            stats_adicionales: Datos adicionales (líneas históricas, volumen, etc.)
        """
        local = partido['local']
        visitante = partido['visitante']
        
        # Extraer datos
        prob = resultado_heurístico.get('confianza', 50)
        apuesta = resultado_heurístico.get('apuesta', '')
        regla = resultado_heurístico.get('regla', 0)
        
        # Extraer odds moneyline
        odds_ml_local = partido.get('odds', {}).get('moneyline', {}).get('local', '-110')
        odds_ml_visit = partido.get('odds', {}).get('moneyline', {}).get('visitante', '-110')
        
        # Determinar equipo recomendado
        if local in apuesta or 'GANA LOCAL' in apuesta or local.lower() in apuesta.lower():
            equipo_recomendado = local
            prob_equipo = prob
        elif visitante in apuesta or 'GANA VISITANTE' in apuesta or visitante.lower() in apuesta.lower():
            equipo_recomendado = visitante
            prob_equipo = prob
        else:
            equipo_recomendado = "Empate"
            prob_equipo = 50
        
        # ============================================
        # 1. PROBABILIDADES DEL MERCADO (con y sin vig)
        # ============================================
        # Probabilidades sucias (con comisión)
        prob_sucia_local = self._american_to_prob(odds_ml_local)
        prob_sucia_visit = self._american_to_prob(odds_ml_visit)
        
        # Calcular overround (comisión de la casa)
        overround = self._calcular_overround(prob_sucia_local, prob_sucia_visit)
        
        # Limpiar vig (probabilidades reales)
        prob_real_local, prob_real_visit = self._limpiar_vig(prob_sucia_local, prob_sucia_visit)
        
        # ============================================
        # 2. EDGE RATING PROFESIONAL (contra probabilidad real)
        # ============================================
        if equipo_recomendado == local:
            diff = prob_equipo - prob_real_local
            prob_mercado = prob_real_local
        elif equipo_recomendado == visitante:
            diff = prob_equipo - prob_real_visit
            prob_mercado = prob_real_visit
        else:
            diff = 0
            prob_mercado = 50
        
        # Edge base: cada 1% de diferencia = 0.4 puntos de edge
        edge_base = 5.0 + (diff * 0.4)
        edge_base = max(1.0, min(10.0, edge_base))
        
        # Ajustar por volumen de datos
        partidos_jugados = stats_adicionales.get('partidos_jugados', 20) if stats_adicionales else 20
        edge = self._ajustar_por_volumen(edge_base, partidos_jugados)
        
        # ============================================
        # 3. PUBLIC MONEY vs SHARP MONEY (simulado con datos realistas)
        # ============================================
        # En producción, estos datos vendrían de scraping de sitios como Action Network
        # Por ahora, usamos una simulación realista basada en el edge
        
        # El público suele apostar al favorito (mayor probabilidad)
        if prob_sucia_local > prob_sucia_visit:
            public_team = local
            public_percentage = 65 + (edge_base - 5) * 2  # 65-75%
        else:
            public_team = visitante
            public_percentage = 65 + (edge_base - 5) * 2
        
        public_percentage = min(85, max(50, public_percentage))
        
        # Sharp money: dinero inteligente
        if diff > 3:
            # Si hay edge positivo, sharps confirman
            sharps = f"Sharps confirming {equipo_recomendado}"
            sharps_confidence = "ALTA" if diff > 5 else "MEDIA"
        elif diff < -3:
            # Si el modelo es más pesimista que mercado, sharps en contra
            sharps = f"Sharps fading {equipo_recomendado}"
            sharps_confidence = "ALTA" if diff < -5 else "MEDIA"
        else:
            sharps = "Sharps split"
            sharps_confidence = "BAJA"
        
        # ============================================
        # 4. REVERSE LINE MOVEMENT (RLM) DETECTION
        # ============================================
        reverse_line = False
        rlm_description = ""
        
        if stats_adicionales and 'spread_apertura' in stats_adicionales:
            spread_apertura = stats_adicionales.get('spread_apertura', 0)
            spread_actual = partido.get('odds', {}).get('spread', {}).get('valor', 0)
            
            # Si el público va al local pero la línea se mueve al visitante
            if public_team == local and spread_actual > spread_apertura:
                reverse_line = True
                edge += 1.0
                rlm_description = f"RLM: público en {local} pero línea movida a {visitante}"
            
            # Si el público va al visitante pero la línea se mueve al local
            elif public_team == visitante and spread_actual < spread_apertura:
                reverse_line = True
                edge += 1.0
                rlm_description = f"RLM: público en {visitante} pero línea movida a {local}"
        
        # ============================================
        # 5. VALUE DETECTION PROFESIONAL
        # ============================================
        value_detected = False
        value_reasons = []
        
        # Criterio 1: Edge significativo (>= 1.5 puntos de edge)
        if edge >= 6.5 and diff > 3:
            value_detected = True
            value_reasons.append(f"Edge {edge:.1f} con diferencial +{diff:.1f}% vs mercado")
        
        # Criterio 2: Reverse line movement detectado
        if reverse_line:
            value_detected = True
            value_reasons.append(rlm_description)
        
        # Criterio 3: Diferencia significativa con mercado en partidos parejos
        if regla in [1, 2, 3] and diff > 5:
            value_detected = True
            value_reasons.append(f"Regla {regla} de alta confianza +{diff:.1f}% vs mercado")
        
        # ============================================
        # 6. RECOMENDACIÓN DE INTENSIDAD
        # ============================================
        if value_detected and edge >= 7.0:
            intensidad = "🔥🔥 FUERTE"
        elif value_detected and edge >= 6.0:
            intensidad = "🔥 MEDIA"
        elif value_detected:
            intensidad = "⚪ LIGERA"
        else:
            intensidad = "⛔ PASAR"
        
        return {
            # Métricas principales
            'edge_rating': round(edge, 1),
            'prob_modelo': round(prob_equipo, 1),
            'prob_mercado': round(prob_mercado, 1),
            'diff_mercado': round(diff, 1),
            
            # Información del mercado
            'prob_sucia_local': round(prob_sucia_local, 1),
            'prob_sucia_visit': round(prob_sucia_visit, 1),
            'overround': overround,
            
            # Dinero público y sharps
            'public_money': public_percentage,
            'public_team': public_team,
            'sharps_action': sharps,
            'sharps_confidence': sharps_confidence,
            
            # Reverse line movement
            'reverse_line': reverse_line,
            'rlm_description': rlm_description,
            
            # Value detection
            'value_detected': value_detected,
            'value_reasons': value_reasons,
            'intensidad': intensidad,
            
            # Metadata
            'tipo': 'premium_profesional'
        }
    
    def obtener_recomendacion_texto(self, analisis):
        """
        Genera texto explicativo para mostrar en UI
        """
        if not analisis['value_detected']:
            return "⛔ Sin valor claro - Mejor pasar"
        
        texto = f"**{analisis['intensidad']}**\n\n"
        texto += f"Edge Rating: {analisis['edge_rating']} "
        texto += f"(Modelo {analisis['prob_modelo']}% vs Mercado {analisis['prob_mercado']}%)\n"
        texto += f"Comisión casa: {analisis['overround']}%\n\n"
        
        if analisis['reverse_line']:
            texto += f"📉 {analisis['rlm_description']}\n\n"
        
        texto += "🎯 Razones de valor:\n"
        for r in analisis['value_reasons']:
            texto += f"• {r}\n"
        
        return texto

# ============================================
# MÓDULO DE SCRAPING PARA TENDENCIAS REALES
# ============================================
class ScraperTendencias:
    """
    Scraper para obtener tendencias reales de apuestas
    Fuentes: Action Network, Covers.com, OddsPortal
    """
    
    def __init__(self):
        self.fuentes = {
            'action_network': 'https://www.actionnetwork.com',
            'covers': 'https://www.covers.com',
            'oddsportal': 'https://www.oddsportal.com'
        }
        print("✅ Scraper Tendencias inicializado")
    
    def obtener_tendencias(self, equipo_local, equipo_visitante):
        """
        Simula la obtención de tendencias reales
        En producción, aquí iría el scraping real
        """
        # Por ahora, devolvemos datos simulados realistas
        import random
        
        # Simular porcentaje de apuestas (tickets)
        ticket_percentage = random.randint(55, 75)
        
        # Simular porcentaje de dinero (money)
        # Si el dinero % es menor que tickets %, hay sharps en contra
        if random.random() > 0.7:  # 30% de probabilidad de sharps
            money_percentage = ticket_percentage - random.randint(5, 15)
        else:
            money_percentage = ticket_percentage + random.randint(-5, 5)
        
        money_percentage = max(30, min(70, money_percentage))
        
        return {
            'ticket_percentage': ticket_percentage,
            'money_percentage': money_percentage,
            'public_team': equipo_local if random.random() > 0.5 else equipo_visitante,
            'fuente': 'Action Network (simulado)'
        }
