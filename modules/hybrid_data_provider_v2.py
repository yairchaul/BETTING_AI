#!/usr/bin/env python3
"""
Proveedor Híbrido de Datos 2.0 - VERSIÓN CORREGIDA
Múltiples fuentes gratuitas 2026
"""
import requests
from datetime import datetime

try:
    from odds_api import OddsAPIClient
    ODDS_API_AVAILABLE = True
except ImportError:
    ODDS_API_AVAILABLE = False
    print("⚠️ odds-api-io no instalado. Ejecuta: pip install odds-api-io")

class HybridDataProviderV2:
    """
    Obtiene datos actualizados de múltiples fuentes gratuitas:
    - Odds-API.io (odds en vivo, 5,000 req/hora gratis)
    - Football-Data.org (fixtures, resultados)
    """
    
    def __init__(self, odds_api_key=None, football_data_key=None):
        self.odds_api_key = odds_api_key or "98ccdb7d4c28042caa8bc8fe7ff6cc62"
        self.football_data_key = football_data_key or ""
        
        self.odds_client = None
        if ODDS_API_AVAILABLE:
            try:
                self.odds_client = OddsAPIClient(api_key=self.odds_api_key)
                print(f"✅ Odds-API cliente inicializado")
            except Exception as e:
                print(f"⚠️ Error inicializando Odds-API: {e}")
    
    def get_live_odds(self, partido_local, partido_visitante):
        """
        Obtiene odds EN VIVO de Caliente.mx vía API
        """
        if not self.odds_client:
            print("⚠️ Odds-API no disponible")
            return None
            
        try:
            # Buscar el evento por nombre (MÉTODO CORREGIDO)
            print(f"🔍 Buscando: {partido_local} vs {partido_visitante}")
            
            # Opción 1: Búsqueda general (sin sport)
            events = self.odds_client.search_events(
                query=f"{partido_local} {partido_visitante}"
            )
            
            # Opción 2: Si no encuentra, intentar con get_events (con filtro de sport)
            if not events or len(events) == 0:
                events = self.odds_client.get_events(
                    sport="soccer",
                    query=f"{partido_local} {partido_visitante}"
                )
            
            if events and len(events) > 0:
                event_id = events[0]['id']
                event_name = events[0].get('name', 'Desconocido')
                print(f"✅ Evento encontrado: {event_name}")
                
                # Obtener odds de México/Caliente
                odds = self.odds_client.get_event_odds(
                    event_id=event_id,
                    region="mx",  # México
                    markets="h2h,spreads,totals"
                )
                return odds
            else:
                print(f"❌ No se encontró el evento")
                
        except Exception as e:
            print(f"⚠️ Error en odds-api: {e}")
        
        return None
    
    def get_partidos_hoy(self, liga=None):
        """
        Obtiene partidos de fútbol de hoy
        """
        if not self.odds_client:
            return None
            
        try:
            # Método correcto para eventos en vivo
            events = self.odds_client.get_live_events(sport="soccer")
            
            if events:
                return events
            
            # Si no hay live, buscar eventos programados
            events = self.odds_client.get_events(
                sport="soccer",
                date="today",
                region="mx"
            )
            return events
        except Exception as e:
            print(f"⚠️ Error obteniendo partidos: {e}")
            return None
    
    def get_team_stats_actualizadas(self, team_name):
        """
        Obtiene estadísticas ACTUALES del equipo
        """
        # Intento 1: Odds-API (datos de equipos)
        if self.odds_client:
            try:
                # Método correcto para participantes
                participants = self.odds_client.get_participants(
                    sport="soccer",
                    search=team_name
                )
                if participants and len(participants) > 0:
                    print(f"✅ Datos de {team_name} encontrados")
                    return participants[0]
            except Exception as e:
                print(f"⚠️ Error buscando participante: {e}")
        
        # Fallback: datos locales
        return self._get_local_stats(team_name)
    
    def _get_local_stats(self, team_name):
        """
        Obtiene estadísticas de la base local
        """
        from modules.team_database import TeamDatabase
        db = TeamDatabase()
        team_id = db.get_team_id(team_name)
        
        if team_id:
            return {
                'id': team_id,
                'name': team_name,
                'source': 'local',
                'goles_favor': 1.35,
                'goles_contra': 1.35
            }
        return None

# Test rápido
if __name__ == "__main__":
    provider = HybridDataProviderV2()
    
    print("\n🔍 Probando búsqueda de partidos de hoy...")
    partidos = provider.get_partidos_hoy()
    if partidos:
        print(f"✅ Encontrados {len(partidos)} partidos")
        for p in partidos[:3]:
            print(f"   {p.get('name', 'N/A')}")
    else:
        print("❌ No se encontraron partidos")
    
    print("\n🔍 Probando búsqueda de equipo...")
    stats = provider.get_team_stats_actualizadas("Real Madrid")
    print(stats)
