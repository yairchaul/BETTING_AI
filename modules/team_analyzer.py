from modules.form_analyzer import analyze_last5


def build_team_profile(team_name: str):

    # 🔥 SIMULACIÓN (luego se conecta API real)
    fake_matches = [
        {"gf":2,"ga":1,"corners":5},
        {"gf":1,"ga":1,"corners":4},
        {"gf":3,"ga":2,"corners":6},
        {"gf":0,"ga":1,"corners":3},
        {"gf":2,"ga":0,"corners":5},
    ]

    form = analyze_last5(fake_matches)

    return {
        "team": team_name,
        "matches": fake_matches,
        "attack": form["attack"],
        "defense": form["defense"],
        "form_score": form["form_score"],
        "corners": form["corners"]
    }
