def build_team_rating(last5):

    goals_for = sum(m["gf"] for m in last5) / len(last5)
    goals_against = sum(m["ga"] for m in last5) / len(last5)
    shots_on_target = sum(m["shots"] for m in last5) / len(last5)

    attack = (goals_for * 35) + (shots_on_target * 5)
    defense = 100 - (goals_against * 30)

    # limitar rango
    attack = max(30, min(80, attack))
    defense = max(30, min(80, defense))

    return {
        "attack": attack,
        "defense": defense
    }
