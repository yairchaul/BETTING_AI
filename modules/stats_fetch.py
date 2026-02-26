import re

def clean_name(name):
    name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
    suffixes = [' SE', ' FC', ' ES', ' UNPFM', ' United', ' U20', ' CD']
    for s in suffixes:
        name = re.sub(rf'{s}$', '', name, flags=re.IGNORECASE)
    return name.strip()

def build_team_rating(last5):
    if not last5:
        return {"attack": 50, "defense": 50}
    
    goals_for = sum(m["gf"] for m in last5) / len(last5)
    goals_against = sum(m["ga"] for m in last5) / len(last5)
    shots_on_target = sum(m["shots"] for m in last5) / len(last5)

    attack = max(30, min(80, (goals_for * 35) + (shots_on_target * 5)))
    defense = max(30, min(80, 100 - (goals_against * 30)))

    return {"attack": attack, "defense": defense}

def get_team_stats(home, away):
    # Por ahora simulamos datos para que el sistema corra
    mock_last5 = [{"gf": 1, "ga": 1, "shots": 4}]
    
    return {
        "home": build_team_rating(mock_last5),
        "away": build_team_rating(mock_last5)
    }
