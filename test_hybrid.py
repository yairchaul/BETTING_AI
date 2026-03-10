from modules.hybrid_data_provider import HybridDataProvider
import streamlit as st

print("🔍 PROBANDO PROVEEDOR HÍBRIDO")
print("=" * 60)

provider = HybridDataProvider()

equipos = [
    'Puebla',
    'Tigres UANL',
    'América',
    'Tottenham',
    'Arsenal',
    'Real Madrid'
]

for equipo in equipos:
    print(f"\n📊 {equipo}:")
    stats = provider.get_team_stats(equipo)
    print(f"  GF: {stats['avg_goals_scored']:.2f} | GA: {stats['avg_goals_conceded']:.2f} (fuente: {stats.get('source', 'desconocida')})")

print("\n" + "=" * 60)
