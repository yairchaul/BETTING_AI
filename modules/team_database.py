# -*- coding: utf-8 -*-
"""
Módulo para gestionar la base de datos de equipos descargada
"""
import json
import os

class TeamDatabase:
    """
    Gestiona la base de datos local de equipos
    """
    
    def __init__(self, db_file='data/teams_database.json'):
        self.db_file = db_file
        self.data = self._load_database()
        
    def _load_database(self):
        """Carga la base de datos desde el archivo JSON"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ Base de datos cargada: {data.get('total_teams', 0)} equipos")
                    return data
            except Exception as e:
                print(f"❌ Error cargando base de datos: {e}")
        else:
            print(f"⚠️ No se encontró {self.db_file}")
        return None
    
    def get_team_id(self, team_name):
        """
        Busca el ID de un equipo por su nombre
        
        Args:
            team_name: Nombre del equipo a buscar
            
        Returns:
            ID del equipo o None si no se encuentra
        """
        if not self.data:
            return None
        
        # Normalizar nombre
        normalized = team_name.lower().strip()
        
        # Buscar en el índice
        indexes = self.data.get('indexes', {}).get('by_name', {})
        
        # Búsqueda exacta
        if normalized in indexes:
            return indexes[normalized]
        
        # Búsqueda por coincidencia parcial
        for name_key, team_id in indexes.items():
            if normalized in name_key or name_key in normalized:
                return team_id
        
        return None
    
    def get_team_info(self, team_name):
        """
        Obtiene toda la información de un equipo
        
        Args:
            team_name: Nombre del equipo
            
        Returns:
            Diccionario con info del equipo o None
        """
        team_id = self.get_team_id(team_name)
        if not team_id or not self.data:
            return None
        
        # Buscar en la lista de equipos
        for team in self.data.get('teams', []):
            if team['id'] == team_id:
                return team
        
        return None
    
    def get_teams_by_country(self, country):
        """
        Obtiene todos los equipos de un país
        
        Args:
            country: Nombre del país
            
        Returns:
            Lista de equipos de ese país
        """
        if not self.data:
            return []
        
        result = []
        for team in self.data.get('teams', []):
            if team.get('country', '').lower() == country.lower():
                result.append(team)
        
        return result
    
    def search_teams(self, query, limit=10):
        """
        Busca equipos por nombre (coincidencia parcial)
        
        Args:
            query: Texto a buscar
            limit: Máximo número de resultados
            
        Returns:
            Lista de equipos que coinciden
        """
        if not self.data:
            return []
        
        query = query.lower()
        results = []
        
        for team in self.data.get('teams', []):
            if query in team['name'].lower():
                results.append(team)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_all_team_names(self):
        """Obtiene todos los nombres de equipos"""
        if not self.data:
            return []
        
        return [team['name'] for team in self.data.get('teams', [])]

# =============================================================================
# EJEMPLO DE USO
# =============================================================================
if __name__ == "__main__":
    db = TeamDatabase()
    
    if db.data:
        print("\n🔍 Probando búsquedas:")
        equipos_prueba = ['Cienciano', 'Melgar', 'Orense SC', 'Macara', 'Bucaramanga']
        
        for equipo in equipos_prueba:
            team_id = db.get_team_id(equipo)
            if team_id:
                info = db.get_team_info(equipo)
                print(f"✅ {equipo}: ID {team_id} ({info.get('country', '?')})")
            else:
                print(f"❌ {equipo}: No encontrado")
