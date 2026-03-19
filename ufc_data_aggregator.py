"""
UFC DATA AGGREGATOR - Versión corregida
"""
import streamlit as st
from ufc_dataset_integrator import UFCDatasetIntegrator

class UFCDataAggregator:
    def __init__(self):
        self.dataset = UFCDatasetIntegrator()
        self.cache = {}
        print("✅ UFC Data Aggregator inicializado")
    
    def _parse_record(self, record_str):
        """Parsea string de récord (ej: '11-5-0') a dict"""
        try:
            parts = record_str.split('-')
            if len(parts) >= 3:
                return {
                    'wins': int(parts[0]),
                    'losses': int(parts[1]),
                    'draws': int(parts[2])
                }
            elif len(parts) == 2:
                return {
                    'wins': int(parts[0]),
                    'losses': int(parts[1]),
                    'draws': 0
                }
        except:
            pass
        return {'wins': 0, 'losses': 0, 'draws': 0}
    
    def get_fighter_basic_data(self, fighter_name, espn_record=None):
        """
        Obtiene datos básicos del peleador
        """
        if fighter_name in self.cache:
            return self.cache[fighter_name]
        
        # Intentar obtener del dataset
        stats = self.dataset.get_fighter_stats(fighter_name)
        
        # Usar récord de ESPN si está disponible
        record = espn_record if espn_record else '0-0-0'
        if stats and stats.get('record') and record == '0-0-0':
            record = stats.get('record')
        
        data = {
            'nombre': fighter_name,
            'record': record,
            'altura': stats.get('altura', 'N/A') if stats else 'N/A',
            'peso': stats.get('peso', 'N/A') if stats else 'N/A',
            'alcance': stats.get('alcance', 'N/A') if stats else 'N/A',
            'postura': stats.get('postura', 'Desconocida') if stats else 'Desconocida',
            'record_dict': self._parse_record(record)
        }
        
        self.cache[fighter_name] = data
        return data
    
    def get_fight_data(self, fighter1_name, fighter2_name, event_data=None):
        """
        Obtiene datos de ambos peleadores
        """
        if not fighter1_name or not fighter2_name:
            return None
        
        # Buscar récords de ESPN
        espn_record1 = None
        espn_record2 = None
        
        if event_data:
            for fight in event_data:
                p1 = fight.get('peleador1', {})
                p2 = fight.get('peleador2', {})
                
                if fighter1_name.lower() in p1.get('nombre', '').lower() or p1.get('nombre', '').lower() in fighter1_name.lower():
                    espn_record1 = p1.get('record')
                if fighter2_name.lower() in p2.get('nombre', '').lower() or p2.get('nombre', '').lower() in fighter2_name.lower():
                    espn_record2 = p2.get('record')
        
        # Obtener datos básicos
        p1_data = self.get_fighter_basic_data(fighter1_name, espn_record1)
        p2_data = self.get_fighter_basic_data(fighter2_name, espn_record2)
        
        return {
            'peleador1': p1_data,
            'peleador2': p2_data,
            'real': True
        }
