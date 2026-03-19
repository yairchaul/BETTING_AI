"""
ANALIZADOR UFC KO PROFESIONAL - Predice probabilidad de KO basado en datos reales
Inspirado en modelos de Machine Learning y análisis estadístico
"""
import streamlit as st
import numpy as np

class AnalizadorUFCKOPro:
    """
    Analiza la probabilidad de KO en combates UFC usando:
    - Historial de finalizaciones
    - Eficiencia de golpeo vs defensa
    - Volumen de golpeo
    - Factor sorpresa (estilo de pelea)
    """
    
    def __init__(self):
        self.modelo_entrenado = None  # Para futura integración con ML
        print("✅ Analizador UFC KO Profesional inicializado")
    
    def _calcular_ko_rate(self, fighter_data):
        """
        Calcula el % de victorias por KO en la carrera
        """
        record_dict = fighter_data.get('record_dict', {'wins': 0, 'losses': 0})
        wins = record_dict['wins']
        
        # Intentar obtener historial de peleas
        historial = fighter_data.get('historial', [])
        
        ko_wins = 0
        for pelea in historial:
            if pelea.get('resultado') == 'Victoria' and pelea.get('metodo'):
                metodo = str(pelea.get('metodo', '')).upper()
                if 'KO' in metodo or 'TKO' in metodo:
                    ko_wins += 1
        
        if wins == 0:
            return 0
        
        return (ko_wins / wins) * 100
    
    def _calcular_sub_rate(self, fighter_data):
        """
        Calcula el % de victorias por sumisión
        """
        wins = fighter_data.get('record_dict', {'wins': 0})['wins']
        historial = fighter_data.get('historial', [])
        
        sub_wins = 0
        for pelea in historial:
            if pelea.get('resultado') == 'Victoria' and pelea.get('metodo'):
                metodo = str(pelea.get('metodo', '')).upper()
                if 'SUBMISSION' in metodo:
                    sub_wins += 1
        
        if wins == 0:
            return 0
        
        return (sub_wins / wins) * 100
    
    def _calcular_striking_efficiency(self, fighter_data):
        """
        Calcula eficiencia de golpeo usando estadísticas disponibles
        Basado en investigación de GitHub
        """
        stats = fighter_data.get('estadisticas_carrera', {})
        
        # Intentar obtener estadísticas de golpeo
        sig_strikes_landed = stats.get('sig_strikes_landed_per_min', 0)
        sig_strike_accuracy = stats.get('sig_strike_accuracy', 0)
        striking_defense = stats.get('striking_defense', 0)
        
        # Evitar división por cero
        if striking_defense == 0:
            striking_defense = 1
        
        # Fórmula de eficiencia 
        efficiency = (sig_strike_accuracy / striking_defense) * (sig_strikes_landed / 5)
        
        return min(100, efficiency)
    
    def _calcular_wrestling_efficiency(self, fighter_data):
        """
        Calcula eficiencia de lucha
        Basado en investigación de GitHub
        """
        stats = fighter_data.get('estadisticas_carrera', {})
        
        td_accuracy = stats.get('td_accuracy', 0)
        td_defense = stats.get('td_defense', 0)
        
        if td_defense == 0:
            td_defense = 1
        
        efficiency = (td_accuracy / td_defense) * 10
        
        return min(100, efficiency)
    
    def _calcular_volumen_golpeo(self, fighter_data):
        """
        Calcula volumen de golpeo por minuto
        """
        stats = fighter_data.get('estadisticas_carrera', {})
        return stats.get('sig_strikes_landed_per_min', 0) * 10
    
    def analizar_ko_probability(self, fighter1_data, fighter2_data):
        """
        Analiza la probabilidad de KO en el combate
        
        Returns:
            Dict con probabilidades para cada peleador y método
        """
        # 1. KO rates históricos
        ko_rate1 = self._calcular_ko_rate(fighter1_data)
        ko_rate2 = self._calcular_ko_rate(fighter2_data)
        
        # 2. Sub rates (para determinar si no es KO)
        sub_rate1 = self._calcular_sub_rate(fighter1_data)
        sub_rate2 = self._calcular_sub_rate(fighter2_data)
        
        # 3. Eficiencia de golpeo
        striking_eff1 = self._calcular_striking_efficiency(fighter1_data)
        striking_eff2 = self._calcular_striking_efficiency(fighter2_data)
        
        # 4. Volumen de golpeo
        volumen1 = self._calcular_volumen_golpeo(fighter1_data)
        volumen2 = self._calcular_volumen_golpeo(fighter2_data)
        
        # 5. Wrestling efficiency (para saber si pueden llevar a tierra)
        wrestling_eff1 = self._calcular_wrestling_efficiency(fighter1_data)
        wrestling_eff2 = self._calcular_wrestling_efficiency(fighter2_data)
        
        # ============================================
        # CÁLCULO DE PROBABILIDAD DE KO POR PELEADOR
        # ============================================
        
        # Factor de KO base (historial)
        ko_factor1 = ko_rate1 / 100
        ko_factor2 = ko_rate2 / 100
        
        # Factor de striking (quien golpea mejor)
        striking_factor1 = striking_eff1 / (striking_eff1 + striking_eff2) if (striking_eff1 + striking_eff2) > 0 else 0.5
        striking_factor2 = 1 - striking_factor1
        
        # Factor de volumen (quien lanza más golpes)
        volumen_factor1 = volumen1 / (volumen1 + volumen2) if (volumen1 + volumen2) > 0 else 0.5
        volumen_factor2 = 1 - volumen_factor1
        
        # Factor de defensa de wrestling (quien puede mantener la pelea de pie)
        # Si tiene buena defensa de derribos, más probable que la pelea se quede de pie = más chance de KO
        wrestling_def_factor1 = wrestling_eff1 / 100
        wrestling_def_factor2 = wrestling_eff2 / 100
        
        # Probabilidad compuesta de KO por cada peleador
        prob_ko_por_peleador1 = (
            ko_factor1 * 0.4 +
            striking_factor1 * 0.3 +
            volumen_factor1 * 0.2 +
            wrestling_def_factor1 * 0.1
        ) * 100
        
        prob_ko_por_peleador2 = (
            ko_factor2 * 0.4 +
            striking_factor2 * 0.3 +
            volumen_factor2 * 0.2 +
            wrestling_def_factor2 * 0.1
        ) * 100
        
        # ============================================
        # PROBABILIDAD GENERAL DE KO EN LA PELEA
        # ============================================
        
        # Probabilidad de que la pelea termine en KO (sin importar quién)
        prob_ko_general = (ko_rate1 + ko_rate2) / 2
        
        # Ajustar por eficiencia de striking combinada
        striking_combinado = (striking_eff1 + striking_eff2) / 2
        prob_ko_general = prob_ko_general * (striking_combinado / 50)
        prob_ko_general = min(90, max(10, prob_ko_general))
        
        # ============================================
        # RECOMENDACIÓN Y ANÁLISIS
        # ============================================
        
        recomendaciones = []
        
        # Determinar favorito para KO
        if prob_ko_por_peleador1 > prob_ko_por_peleador2 + 20:
            favorito_ko = fighter1_data.get('nombre', 'Peleador 1')
            recomendaciones.append(f"🔥 {favorito_ko} tiene ventaja clara para KO")
        elif prob_ko_por_peleador2 > prob_ko_por_peleador1 + 20:
            favorito_ko = fighter2_data.get('nombre', 'Peleador 2')
            recomendaciones.append(f"🔥 {favorito_ko} tiene ventaja clara para KO")
        
        # Determinar si es probable KO temprano
        if ko_rate1 > 60 and ko_rate2 > 60:
            recomendaciones.append("⚡ Ambos finalizadores - KO probable antes del 3er round")
        
        # Determinar si es probable que llegue a decisión
        if ko_rate1 < 30 and ko_rate2 < 30:
            recomendaciones.append("🛡️ Peleadores defensivos - probable decisión")
        
        return {
            'prob_ko_general': round(prob_ko_general, 1),
            'prob_ko_peleador1': round(prob_ko_por_peleador1, 1),
            'prob_ko_peleador2': round(prob_ko_por_peleador2, 1),
            'ko_rate1': round(ko_rate1, 1),
            'ko_rate2': round(ko_rate2, 1),
            'striking_eff1': round(striking_eff1, 1),
            'striking_eff2': round(striking_eff2, 1),
            'volumen1': round(volumen1, 1),
            'volumen2': round(volumen2, 1),
            'wrestling_def1': round(wrestling_eff1, 1),
            'wrestling_def2': round(wrestling_eff2, 1),
            'recomendaciones': recomendaciones,
            'color': 'red' if prob_ko_general > 60 else 'orange' if prob_ko_general > 40 else 'blue'
        }
    
    def analizar_metodo_victoria(self, fighter1_data, fighter2_data):
        """
        Analiza el método de victoria más probable
        """
        ko_rate1 = self._calcular_ko_rate(fighter1_data)
        ko_rate2 = self._calcular_ko_rate(fighter2_data)
        sub_rate1 = self._calcular_sub_rate(fighter1_data)
        sub_rate2 = self._calcular_sub_rate(fighter2_data)
        
        ko_general = (ko_rate1 + ko_rate2) / 2
        sub_general = (sub_rate1 + sub_rate2) / 2
        dec_general = 100 - ko_general - sub_general
        dec_general = max(0, dec_general)
        
        if ko_general > sub_general and ko_general > dec_general:
            metodo = "KO/TKO"
            prob = ko_general
        elif sub_general > ko_general and sub_general > dec_general:
            metodo = "Sumisión"
            prob = sub_general
        else:
            metodo = "Decisión"
            prob = dec_general
        
        return {
            'metodo_mas_probable': metodo,
            'probabilidad': round(prob, 1),
            'prob_ko': round(ko_general, 1),
            'prob_sub': round(sub_general, 1),
            'prob_dec': round(dec_general, 1)
        }
