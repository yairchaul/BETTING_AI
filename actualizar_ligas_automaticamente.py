"""
ACTUALIZAR LIGAS AUTOMÁTICAMENTE - Script para generar espn_league_codes.py
"""
import json

# Intenta descubrir ligas desde RapidAPI
try:
    import requests
    from espn_league_discovery import ESPNLeagueDiscovery
    
    discovery = ESPNLeagueDiscovery()
    ligas_rapidapi = discovery.descubrir_desde_rapidapi()
except:
    ligas_rapidapi = {}

# Nuestras ligas confirmadas manualmente
ligas_manuales = {
    "México - Liga MX": "mex.1",
    "México - Liga de Expansión MX": "mex.2",
    "México - Liga MX Femenil": "mex.women",
    "CONCACAF Champions Cup": "concacaf.champions",
    "Copa Libertadores": "conmebol.libertadores",
    "Copa Sudamericana": "conmebol.sudamericana",
    "MLS - Major League Soccer": "usa.1",
    "USA - US Open Cup": "usa.open",
    "La Liga": "esp.1",
    "Segunda División": "esp.2",
    "Copa del Rey": "esp.copa",
    "Inglaterra - Premier League": "eng.1",
    "Inglaterra - Championship": "eng.2",
    "Inglaterra - League One": "eng.3",
    "Inglaterra - League Two": "eng.4",
    "Inglaterra - EFL Cup": "eng.cup",
    "Inglaterra - Copa FA": "eng.fa",
    "Escocia - Premiership": "sco.1",
    "Serie A": "ita.1",
    "Serie B": "ita.2",
    "Coppa Italia": "ita.cup",
    "Ligue 1": "fra.1",
    "Ligue 2": "fra.2",
    "Copa de Francia": "fra.cup",
    "Bundesliga 1": "ger.1",
    "Bundesliga 2": "ger.2",
    "Bundesliga 3": "ger.3",
    "DFB Pokal": "ger.cup",
    "Holanda - Eredivisie": "ned.1",
    "Holanda - Eerste Divisie": "ned.2",
    "Portugal - Primeira Liga": "por.1",
    "Portugal - Segunda Liga": "por.2",
    "Brasil - Serie A": "bra.1",
    "Brasil - Serie B": "bra.2",
    "Brasil - Copa do Brasil": "bra.cup",
    "Argentina - Liga Profesional": "arg.1",
    "Argentina - Primera Nacional": "arg.2",
    "Argentina - Copa Argentina": "arg.cup",
    "Colombia - Primera A": "col.1",
    "Colombia - Primera B": "col.2",
    "Uruguay - Primera División": "uru.1",
    "Paraguay - Primera División": "par.1",
    "Chile - Primera B": "chi.2",
    "Ecuador - Primera A": "ecu.1",
    "Perú - Primera División": "per.1",
    "Costa Rica - Primera División": "crc.1",
    "El Salvador - Primera Division": "slv.1",
    "Guatemala - Liga Nacional": "gua.1",
    "Honduras - Liga Nacional": "hon.1",
    "UEFA - Champions League": "uefa.champions",
    "UEFA - Europa League": "uefa.europa",
    "UEFA - Europa Conference League": "uefa.europa.conf",  # 🔥 ¡CORREGIDO!
    "Eliminatorias UEFA": "fifa.worldq.uefa",
    "Turquía - Superliga": "tur.1",
    "Austria - Bundesliga": "aut.1",
    "Bélgica - 1ra División A": "bel.1",
    "Grecia - Super League": "gre.1",
    "Polonia - Ekstraklasa": "pol.1",
    "Suiza - Super Liga": "sui.1",
    "Ucrania - Premier League": "ukr.1",
    "Japón - Liga J": "jpn.1",
    "Corea del Sur - K-League 1": "kor.1",
    "China - Super Liga": "chn.1",
    "Australia - A-League": "aus.1",
    "Sudáfrica - Premier League": "rsa.1",
}

# Combinar (prioridad a las manuales)
ligas_combinadas = {**ligas_rapidapi, **ligas_manuales}

# Generar archivo Python
with open('espn_league_codes_auto.py', 'w', encoding='utf-8') as f:
    f.write('"""\n')
    f.write('ESPN LEAGUE CODES - Generado automáticamente\n')
    f.write('"""\n\n')
    f.write('class ESPNLeagueCodes:\n')
    f.write('    """\n')
    f.write('    Códigos de ligas ESPN generados automáticamente\n')
    f.write('    """\n\n')
    f.write('    CODIGOS_CONFIRMADOS = {\n')
    
    for nombre, codigo in sorted(ligas_combinadas.items()):
        f.write(f'        "{nombre}": "{codigo}",\n')
    
    f.write('    }\n\n')
    f.write('    @classmethod\n')
    f.write('    def obtener_todas(cls):\n')
    f.write('        return list(cls.CODIGOS_CONFIRMADOS.keys())\n')

print(f"✅ Archivo generado con {len(ligas_combinadas)} ligas")
