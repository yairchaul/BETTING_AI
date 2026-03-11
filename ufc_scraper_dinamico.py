"""
UFC Scraper Dinámico - Captura TODA la cartelera (Main + Prelims)
"""
import pandas as pd
import requests
from typing import List, Dict

class UFCDynamicScraper:
    """Extrae la cartelera COMPLETA de UFC desde ESPN"""
    
    def __init__(self):
        self.url = "https://www.espn.com.mx/mma/cartelera"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    def get_next_event(self) -> List[Dict]:
        """Obtiene TODAS las peleas (Main Card + Prelims + Early Prelims)"""
        print("📡 Extrayendo cartelera UFC completa desde ESPN...")
        
        try:
            # ESPN tiene múltiples tablas (Main, Prelims, Early Prelims)
            tables = pd.read_html(self.url)
            cartelera_completa = []
            
            for idx, tabla in enumerate(tables):
                # Determinar tipo de tarjeta
                if idx == 0:
                    tipo = "PRINCIPAL"
                elif idx == 1:
                    tipo = "PRELIMINAR"
                else:
                    tipo = "PRELIMINAR TEMPRANO"
                
                # Procesar cada fila de la tabla
                for _, row in tabla.iterrows():
                    pelea_texto = str(row[0])
                    
                    if " vs " in pelea_texto:
                        p1, p2 = pelea_texto.split(" vs ")
                        
                        combate = {
                            'evento': 'UFC Próximo Evento',
                            'fecha': 'Próximamente',
                            'tipo_tarjeta': tipo,
                            'peso': row.get('PESO', 'N/A') if 'PESO' in row else 'N/A',
                            'peleador1': {
                                'nombre': p1.strip(),
                                'record': row.get('RÉCORD', '0-0-0') if 'RÉCORD' in row else '0-0-0',
                                'pais': row.get('PAÍS', 'N/A') if 'PAÍS' in row else 'N/A'
                            },
                            'peleador2': {
                                'nombre': p2.strip(),
                                'record': '0-0-0',
                                'pais': 'N/A'
                            }
                        }
                        cartelera_completa.append(combate)
            
            print(f"✅ {len(cartelera_completa)} combates encontrados")
            return cartelera_completa
            
        except Exception as e:
            print(f"❌ Error extrayendo UFC: {e}")
            return self._get_simulated_ufc()
    
    def _get_simulated_ufc(self):
        """Datos de respaldo con TODAS las peleas del próximo evento"""
        return [
            # MAIN CARD (6 peleas)
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRINCIPAL',
             'peleador1': {'nombre': 'Josh Emmett', 'record': '19-6-0', 'pais': 'USA'},
             'peleador2': {'nombre': 'Kevin Vallejos', 'record': '17-1-0', 'pais': 'Argentina'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRINCIPAL',
             'peleador1': {'nombre': 'Amanda Lemos', 'record': '15-5-1', 'pais': 'Brasil'},
             'peleador2': {'nombre': 'Gillian Robertson', 'record': '16-8-0', 'pais': 'Canadá'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRINCIPAL',
             'peleador1': {'nombre': 'Ion Cutelaba', 'record': '19-11-1', 'pais': 'Moldavia'},
             'peleador2': {'nombre': 'Oumar Sy', 'record': '12-1-0', 'pais': 'Francia'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRINCIPAL',
             'peleador1': {'nombre': 'Andre Fili', 'record': '25-12-0', 'pais': 'USA'},
             'peleador2': {'nombre': 'Jose Delgado', 'record': '10-2-0', 'pais': 'USA'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRINCIPAL',
             'peleador1': {'nombre': 'Marwan Rahiki', 'record': '7-0-0', 'pais': 'Australia'},
             'peleador2': {'nombre': 'Harry Hardwick', 'record': '13-4-1', 'pais': 'Inglaterra'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRINCIPAL',
             'peleador1': {'nombre': 'Vitor Petrino', 'record': '13-2-0', 'pais': 'Brasil'},
             'peleador2': {'nombre': 'Steven Asplund', 'record': '7-1-0', 'pais': 'USA'}},
            
            # PRELIMS (8 peleas)
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRELIMINAR',
             'peleador1': {'nombre': 'Charles Johnson', 'record': '18-8-0', 'pais': 'USA'},
             'peleador2': {'nombre': 'Bruno Silva', 'record': '15-7-2', 'pais': 'Brasil'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRELIMINAR',
             'peleador1': {'nombre': 'Brad Tavares', 'record': '21-12-0', 'pais': 'USA'},
             'peleador2': {'nombre': 'Eryk Anders', 'record': '17-9-0', 'pais': 'USA'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRELIMINAR',
             'peleador1': {'nombre': 'Chris Curtis', 'record': '32-12-0', 'pais': 'USA'},
             'peleador2': {'nombre': 'Myktybek Orolbai', 'record': '15-2-1', 'pais': 'Kirguistán'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRELIMINAR',
             'peleador1': {'nombre': 'Bolaji Oki', 'record': '10-3-0', 'pais': 'Bélgica'},
             'peleador2': {'nombre': 'Manoel Sousa', 'record': '13-1-0', 'pais': 'Brasil'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRELIMINAR',
             'peleador1': {'nombre': 'Luan Lacerda', 'record': '13-3-0', 'pais': 'Brasil'},
             'peleador2': {'nombre': 'Hecher Sosa', 'record': '14-1-0', 'pais': 'España'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRELIMINAR',
             'peleador1': {'nombre': 'Bia Mesquita', 'record': '6-0-0', 'pais': 'Brasil'},
             'peleador2': {'nombre': 'Montserrat Rendon', 'record': '7-1-0', 'pais': 'México'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRELIMINAR',
             'peleador1': {'nombre': 'Elijah Smith', 'record': '9-1-0', 'pais': 'USA'},
             'peleador2': {'nombre': 'Su Young You', 'record': '16-3-0', 'pais': 'Corea'}},
            {'evento': 'UFC Fight Night: Emmett vs. Vallejos', 'fecha': '14 Mar 2026', 'tipo_tarjeta': 'PRELIMINAR',
             'peleador1': {'nombre': 'Piera Rodriguez', 'record': '11-2-0', 'pais': 'Venezuela'},
             'peleador2': {'nombre': 'Sam Hughes', 'record': '11-6-0', 'pais': 'USA'}},
        ]
