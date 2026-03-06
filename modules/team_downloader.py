# -*- coding: utf-8 -*-
"""
Módulo para descargar y mantener actualizada la base de datos de equipos
Descarga todos los equipos disponibles en la API y los guarda localmente
"""
import requests
import json
import os
import time
from datetime import datetime

class TeamDownloader:
    """
    Descarga y mantiene una base de datos local de equipos con sus IDs
    """
    
    def __init__(self, api_key=None, data_file='data/teams_database.json'):
        """
        Inicializa el descargador de equipos
        
        Args:
            api_key: Tu API key de Football-API
            data_file: Ruta donde guardar la base de datos
        """
        self.api_key = api_key
        self.data_file = data_file
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {'x-apisports-key': api_key} if api_key else {}
        self.last_request_time = 0
        self.request_interval = 0.5  # 2 requests por segundo
        
    def _rate_limit(self):
        """Controla el rate limiting"""
        now = time.time()
        if now - self.last_request_time < self.request_interval:
            time.sleep(self.request_interval - (now - self.last_request_time))
        self.last_request_time = now
    
    def get_countries(self):
        """
        Obtiene la lista de todos los países disponibles
        
        Returns:
            Lista de países con sus nombres
        """
        if not self.api_key:
            print("⚠️ No hay API key configurada")
            return []
        
        self._rate_limit()
        try:
            url = f"{self.base_url}/countries"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                countries = data.get('response', [])
                print(f"✅ Países encontrados: {len(countries)}")
                return [c['name'] for c in countries]
            else:
                print(f"❌ Error obteniendo países: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_teams_by_country(self, country):
        """
        Obtiene todos los equipos de un país específico
        
        Args:
            country: Nombre del país
            
        Returns:
            Lista de equipos con sus IDs y datos
        """
        if not self.api_key:
            return []
        
        self._rate_limit()
        try:
            url = f"{self.base_url}/teams"
            params = {"country": country}
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                teams = data.get('response', [])
                print(f"  → {country}: {len(teams)} equipos")
                
                result = []
                for team_data in teams:
                    team = team_data['team']
                    result.append({
                        'id': team['id'],
                        'name': team['name'],
                        'country': country,
                        'code': team.get('code', ''),
                        'founded': team.get('founded', 0)
                    })
                return result
            else:
                print(f"  → {country}: Error {response.status_code}")
                return []
        except Exception as e:
            print(f"  → {country}: Error {e}")
            return []
    
    def download_all_teams(self):
        """
        Descarga TODOS los equipos de TODOS los países
        Guarda el resultado en un archivo JSON
        """
        print("🔍 DESCARGANDO BASE DE DATOS DE EQUIPOS")
        print("=" * 60)
        
        # 1. Obtener lista de países
        countries = self.get_countries()
        if not countries:
            print("❌ No se pudieron obtener países")
            return None
        
        # 2. Descargar equipos de cada país
        all_teams = []
        total_countries = len(countries)
        
        for i, country in enumerate(countries):
            print(f"📡 [{i+1}/{total_countries}] Procesando {country}...")
            teams = self.get_teams_by_country(country)
            all_teams.extend(teams)
        
        # 3. Crear índices para búsqueda rápida
        print("\n📊 Creando índices...")
        
        # Índice por nombre (para búsqueda rápida)
        name_index = {}
        for team in all_teams:
            # Versión normalizada del nombre (minúsculas, sin espacios extras)
            normalized = team['name'].lower().strip()
            name_index[normalized] = team['id']
            
            # También guardar variantes comunes (sin acentos)
            unaccented = (normalized.replace('á', 'a').replace('é', 'e')
                                    .replace('í', 'i').replace('ó', 'o')
                                    .replace('ú', 'u').replace('ü', 'u')
                                    .replace('ñ', 'n'))
            if unaccented != normalized:
                name_index[unaccented] = team['id']
        
        # Índice por país
        country_index = {}
        for team in all_teams:
            country = team['country']
            if country not in country_index:
                country_index[country] = []
            country_index[country].append(team['id'])
        
        # 4. Guardar todo
        database = {
            'last_update': datetime.now().isoformat(),
            'total_teams': len(all_teams),
            'total_countries': len(countries),
            'teams': all_teams,
            'indexes': {
                'by_name': name_index,
                'by_country': country_index
            }
        }
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print(f"✅ DESCARGA COMPLETADA")
        print(f"📁 Archivo guardado: {self.data_file}")
        print(f"📊 Total equipos: {len(all_teams)}")
        print(f"🌍 Total países: {len(countries)}")
        
        return database
    
    def load_teams_database(self):
        """
        Carga la base de datos de equipos desde el archivo local
        
        Returns:
            Diccionario con la base de datos o None si no existe
        """
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def get_team_id(self, team_name, database=None):
        """
        Busca el ID de un equipo por su nombre
        
        Args:
            team_name: Nombre del equipo a buscar
            database: Base de datos cargada (opcional)
            
        Returns:
            ID del equipo o None si no se encuentra
        """
        if database is None:
            database = self.load_teams_database()
        
        if not database:
            return None
        
        # Buscar en el índice por nombre
        normalized = team_name.lower().strip()
        indexes = database.get('indexes', {}).get('by_name', {})
        
        # Búsqueda exacta
        if normalized in indexes:
            return indexes[normalized]
        
        # Búsqueda por coincidencia parcial (si no hay match exacto)
        for name_key, team_id in indexes.items():
            if normalized in name_key or name_key in normalized:
                return team_id
        
        return None
    
    def get_teams_by_country_local(self, country, database=None):
        """
        Obtiene todos los equipos de un país desde la base local
        
        Args:
            country: Nombre del país
            database: Base de datos cargada
            
        Returns:
            Lista de IDs de equipos de ese país
        """
        if database is None:
            database = self.load_teams_database()
        
        if not database:
            return []
        
        country_index = database.get('indexes', {}).get('by_country', {})
        return country_index.get(country, [])

# =============================================================================
# EJEMPLO DE USO
# =============================================================================
if __name__ == "__main__":
    # Para probar el módulo directamente
    import streamlit as st
    
    api_key = st.secrets.get("FOOTBALL_API_KEY", "")
    if not api_key:
        print("❌ No hay API key configurada en secrets.toml")
    else:
        downloader = TeamDownloader(api_key=api_key)
        
        # Descargar todos los equipos (esto puede tomar varios minutos)
        print("¿Quieres descargar todos los equipos? (s/n)")
        respuesta = input()
        if respuesta.lower() == 's':
            downloader.download_all_teams()
        
        # Probar búsqueda
        db = downloader.load_teams_database()
        if db:
            equipos_prueba = ['Cienciano', 'Melgar', 'Orense SC', 'Macara']
            for equipo in equipos_prueba:
                team_id = downloader.get_team_id(equipo, db)
                if team_id:
                    print(f"✅ {equipo} → ID: {team_id}")
                else:
                    print(f"❌ {equipo} → No encontrado")
