# modules/stats_fetch.py
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_last_5_matches(team_name: str):
    """
    Scraping simple de últimos 5 partidos (Sofascore o similar).
    Retorna lista de dicts: {'date': str, 'opponent': str, 'score': str, 'result': 'W/D/L'}
    """
    try:
        # Búsqueda aproximada - en real usa API con team_id
        url = f"https://www.sofascore.com/search/teams/{team_name.replace(' ', '%20')}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Esto es aproximado - busca primer link de equipo y ve a fixtures
        team_link = soup.find('a', href=re.compile(r'/team/football/'))
        if not team_link:
            return []
        
        team_url = "https://www.sofascore.com" + team_link['href']
        r2 = requests.get(team_url, headers=HEADERS, timeout=10)
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        
        matches = []
        for item in soup2.find_all('div', class_=re.compile(r'match|fixture'))[:5]:
            date = item.find(string=re.compile(r'\d{1,2} \w+'))
            opponent = item.find('span', class_=re.compile(r'opponent'))
            score = item.find(string=re.compile(r'\d-\d'))
            
            if date and opponent:
                matches.append({
                    'date': date.strip() if date else 'N/A',
                    'opponent': opponent.get_text(strip=True) if opponent else 'N/A',
                    'score': score.strip() if score else 'N/A',
                    'result': 'W' if 'W' in item.get_text() else 'D' if 'D' in item.get_text() else 'L'
                })
        
        return matches[:5]
    
    except Exception as e:
        print(f"Error fetching last 5 for {team_name}: {e}")
        return []

def get_injuries(team_name: str):
    """
    Scraping lesiones de Transfermarkt o BeSoccer (aproximado).
    Retorna lista de strings: ['Jugador (lesión, hasta fecha)']
    """
    try:
        search = team_name.replace(' ', '+')
        url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={search}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        team_link = soup.find('a', href=re.compile(r'/startseite/verein/'))
        if not team_link:
            return []
        
        injuries_url = "https://www.transfermarkt.com" + team_link['href'] + "/verletztespieler"
        r_inj = requests.get(injuries_url, headers=HEADERS, timeout=10)
        soup_inj = BeautifulSoup(r_inj.text, 'html.parser')
        
        injuries = []
        rows = soup_inj.find_all('tr', class_=re.compile(r'injury'))
        for row in rows[:6]:  # top 6 lesiones
            player = row.find('td', class_='hauptlink')
            injury_type = row.find('td', string=re.compile(r'injury|ankle|hamstring|knee'))
            until = row.find(string=re.compile(r'\d{1,2}\.\d{1,2}\.\d{4}'))
            
            if player and injury_type:
                desc = f"{player.get_text(strip=True)} ({injury_type.get_text(strip=True)}"
                if until:
                    desc += f", hasta {until.strip()}"
                desc += ")"
                injuries.append(desc)
        
        return injuries or ["Sin lesiones reportadas recientemente"]
    
    except Exception:
        return ["Error al obtener lesiones (intenta API real)"]

# Ejemplo de uso (para debug)
if __name__ == "__main__":
    print(get_last_5_matches("PSV Eindhoven"))
    print(get_injuries("AZ Alkmaar"))
