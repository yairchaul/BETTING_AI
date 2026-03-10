from modules.team_database import TeamDatabase
from modules.hybrid_data_provider import HybridDataProvider

print("🔍 PROBANDO BASE DE DATOS DE EQUIPOS")
print("=" * 60)

# Probar base de datos
db = TeamDatabase()
if db.data:
    print(f"\n📊 Total equipos: {db.data.get('total_teams', 0)}")
    
    equipos_prueba = ['Cienciano', 'Melgar', 'Orense SC', 'Macara', 'Bucaramanga']
    for equipo in equipos_prueba:
        team_id = db.get_team_id(equipo)
        if team_id:
            info = db.get_team_info(equipo)
            print(f"✅ {equipo}: ID {team_id} ({info.get('country', '?')})")
        else:
            print(f"❌ {equipo}: No encontrado")

# Probar proveedor híbrido
print("\n📊 PROBANDO PROVEEDOR HÍBRIDO")
provider = HybridDataProvider()
for equipo in equipos_prueba:
    stats = provider.get_team_stats(equipo)
    print(f"{equipo}: GF={stats['avg_goals_scored']:.2f} GA={stats['avg_goals_conceded']:.2f} ({stats['source']})")

print("\n" + "=" * 60)
