"""
ESPN LEAGUE CODES - Base de datos completa de códigos de ligas
VERSIÓN FINAL CON UEFA CONFERENCE LEAGUE CORREGIDA
"""
import streamlit as st

class ESPNLeagueCodes:
    """
    Contiene todos los códigos de ligas para ESPN
    """
    
    # Códigos verificados y probados
    CODIGOS_CONFIRMADOS = {
        # 🇲🇽 MÉXICO
        "México - Liga MX": "mex.1",
        "México - Liga de Expansión MX": "mex.2",
        "México - Liga MX Femenil": "mex.women",
        
        # 🌎 CONCACAF
        "CONCACAF Champions Cup": "concacaf.champions",
        
        # 🌎 CONMEBOL
        "Copa Libertadores": "conmebol.libertadores",
        "Copa Sudamericana": "conmebol.sudamericana",
        
        # 🇺🇸 USA
        "MLS - Major League Soccer": "usa.1",
        "USA - US Open Cup": "usa.open",
        
        # 🇪🇸 ESPAÑA
        "La Liga": "esp.1",
        "Segunda División": "esp.2",
        "Copa del Rey": "esp.copa",
        
        # 🏴󠁧󠁢󠁥󠁮󠁧󠁿 INGLATERRA
        "Inglaterra - Premier League": "eng.1",
        "Inglaterra - Championship": "eng.2",
        "Inglaterra - League One": "eng.3",
        "Inglaterra - League Two": "eng.4",
        "Inglaterra - EFL Cup": "eng.cup",
        "Inglaterra - Copa FA": "eng.fa",
        
        # 🏴󠁧󠁢󠁳󠁣󠁴󠁿 ESCOCIA
        "Escocia - Premiership": "sco.1",
        
        # 🇮🇹 ITALIA
        "Serie A": "ita.1",
        "Serie B": "ita.2",
        "Coppa Italia": "ita.cup",
        
        # 🇫🇷 FRANCIA
        "Ligue 1": "fra.1",
        "Ligue 2": "fra.2",
        "Copa de Francia": "fra.cup",
        
        # 🇩🇪 ALEMANIA
        "Bundesliga 1": "ger.1",
        "Bundesliga 2": "ger.2",
        "Bundesliga 3": "ger.3",
        "DFB Pokal": "ger.cup",
        
        # 🇳🇱 HOLANDA
        "Holanda - Eredivisie": "ned.1",
        "Holanda - Eerste Divisie": "ned.2",
        
        # 🇵🇹 PORTUGAL
        "Portugal - Primeira Liga": "por.1",
        "Portugal - Segunda Liga": "por.2",
        
        # 🇧🇷 BRASIL
        "Brasil - Serie A": "bra.1",
        "Brasil - Serie B": "bra.2",
        "Brasil - Copa do Brasil": "bra.cup",
        
        # 🇦🇷 ARGENTINA
        "Argentina - Liga Profesional": "arg.1",
        "Argentina - Primera Nacional": "arg.2",
        "Argentina - Copa Argentina": "arg.cup",
        
        # 🇨🇴 COLOMBIA
        "Colombia - Primera A": "col.1",
        "Colombia - Primera B": "col.2",
        
        # 🇺🇾 URUGUAY
        "Uruguay - Primera División": "uru.1",
        
        # 🇵🇾 PARAGUAY
        "Paraguay - Primera División": "par.1",
        
        # 🇨🇱 CHILE
        "Chile - Primera B": "chi.2",
        
        # 🇪🇨 ECUADOR
        "Ecuador - Primera A": "ecu.1",
        
        # 🇵🇪 PERÚ
        "Perú - Primera División": "per.1",
        
        # 🇨🇷 COSTA RICA
        "Costa Rica - Primera División": "crc.1",
        
        # 🇸🇻 EL SALVADOR
        "El Salvador - Primera Division": "slv.1",
        
        # 🇬🇹 GUATEMALA
        "Guatemala - Liga Nacional": "gua.1",
        
        # 🇭🇳 HONDURAS
        "Honduras - Liga Nacional": "hon.1",
        
        # 🇪🇺 UEFA
        "UEFA - Champions League": "uefa.champions",
        "UEFA - Europa League": "uefa.europa",
        "UEFA - Europa Conference League": "uefa.europa.conf",  # 🔥 CÓDIGO CORRECTO
        "Eliminatorias UEFA": "fifa.worldq.uefa",
        
        # 🇹🇷 TURQUÍA
        "Turquía - Superliga": "tur.1",
        
        # 🇦🇹 AUSTRIA
        "Austria - Bundesliga": "aut.1",
        
        # 🇧🇪 BÉLGICA
        "Bélgica - 1ra División A": "bel.1",
        
        # 🇬🇷 GRECIA
        "Grecia - Super League": "gre.1",
        
        # 🇵🇱 POLONIA
        "Polonia - Ekstraklasa": "pol.1",
        
        # 🇨🇭 SUIZA
        "Suiza - Super Liga": "sui.1",
        
        # 🇺🇦 UCRANIA
        "Ucrania - Premier League": "ukr.1",
        
        # 🇯🇵 JAPÓN
        "Japón - Liga J": "jpn.1",
        
        # 🇰🇷 COREA
        "Corea del Sur - K-League 1": "kor.1",
        
        # 🇨🇳 CHINA
        "China - Super Liga": "chn.1",
        
        # 🇦🇺 AUSTRALIA
        "Australia - A-League": "aus.1",
        
        # 🇿🇦 SUDÁFRICA
        "Sudáfrica - Premier League": "rsa.1",
    }
    
    # Códigos que requieren investigación adicional
    CODIGOS_PENDIENTES = [
        "Mexico - Segunda Division",
        "Mexico - Liga MX U21",
        "Panama - Liga Prom",
        "Panama - Liga Panamena",
        "Copa Libertadores U20",
        "Costa Rica - Liga de Ascenso",
        "El Salvador - Reserve League",
        "Jamaica - Premier League",
        "Nicaragua - Nicaragua Cup",
        "Paraguay - Primera Division Reserves",
        "Argentina - Primera Division Reserves",
        "Argentina - Primera B Metropolitana",
        "Brasil - Copa do Nordeste",
        "Chile - Primera B",
        "Escocia - Championship",
        "Escocia - League One",
        "Escocia - League Two",
        "Irlanda del Norte - IFA Premiership",
        "Gales - Premier League",
        "Serie C",
        "Nacional",
        "Regionalliga",
        "Armenia - Premier League",
        "Austria - 2. Liga",
        "Azerbaiyán - Premier League",
        "Bélgica - Primera División B",
        "Bulgaria - First League",
        "Croacia - HNL",
        "Chipre - Division 1",
        "República Checa - Liga 2",
        "Faroe Islands - Premier League",
        "Faroe Islands - 1. deild",
        "Copa de Grecia",
        "Hungría - NB1",
        "Copa de Islandia",
        "Kazajistán - Premier League",
        "Letonia - Virsliga",
        "Lituania - A Lyga",
        "Rumanía - Liga 1",
        "Rumania - Liga 2",
        "Serbia - Super Liga",
        "Eslovaquia - Super Liga",
        "Eslovenia - Prva Liga",
        "Eslovenia - División 2",
        "Suiza - Challenge League",
        "Turquía - TFF League 1",
        "Mundial 2026 – Partidos",
        "World Cup 2026 - Int-Conf. Playoff",
        "Mundial 2026 - Clasificatorios Europa",
        "Australia - Victoria Premier League",
        "Australia - NSW Premier League",
        "Australia - Queensland Premier League",
        "Dinamarca - Superliga",
        "Dinamarca - Division 1",
        "Noruega - Eliteserien",
        "Noruega - Copa NM",
        "Egipto - Premier League",
        "Rwanda - Peace Cup",
        "Sierra Leone - Premier League",
        "Uganda - Cup",
        "India - Super League",
        "Tailandia - Premier League",
        "Japan - J2/J3 League",
        "South Korea - K-League 2",
        "South Korea - K-League 3",
        "Irlanda - Premier Division",
        "Irlanda - 1st Division",
    ]
    
    @classmethod
    def obtener_codigo(cls, nombre_liga):
        """
        Obtiene el código ESPN para una liga por su nombre
        """
        return cls.CODIGOS_CONFIRMADOS.get(nombre_liga, None)
    
    @classmethod
    def obtener_todas(cls):
        """
        Obtiene todas las ligas confirmadas
        """
        return list(cls.CODIGOS_CONFIRMADOS.keys())
    
    @classmethod
    def obtener_pendientes(cls):
        """
        Obtiene ligas que requieren investigación
        """
        return cls.CODIGOS_PENDIENTES
