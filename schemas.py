# schemas.py - Definiciones de estructura JSON para cada deporte

FUTBOL_SCHEMA = {
    "type": "object",
    "properties": {
        "partidos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "local": {"type": "string"},
                    "odds_local": {"type": "string"},
                    "empate": {"type": "string", "const": "Empate"},
                    "odds_empate": {"type": "string"},
                    "visitante": {"type": "string"},
                    "odds_visitante": {"type": "string"}
                },
                "required": ["local", "odds_local", "empate", "odds_empate", "visitante", "odds_visitante"]
            }
        }
    }
}

NBA_SCHEMA = {
    "type": "object",
    "properties": {
        "juegos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "local": {"type": "object", "properties": {
                        "equipo": {"type": "string"},
                        "moneyline": {"type": "string"},
                        "over_under": {"type": "string"},
                        "odds_ou": {"type": "string"},
                        "handicap": {"type": "string"},
                        "odds_spread": {"type": "string"}
                    }},
                    "visitante": {"type": "object", "properties": {
                        "equipo": {"type": "string"},
                        "moneyline": {"type": "string"},
                        "over_under": {"type": "string"},
                        "odds_ou": {"type": "string"},
                        "handicap": {"type": "string"},
                        "odds_spread": {"type": "string"}
                    }}
                },
                "required": ["local", "visitante"]
            }
        }
    }
}

UFC_SCHEMA = {
    "type": "object",
    "properties": {
        "peleas": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "peleador1": {"type": "string"},
                    "odds1": {"type": "string"},
                    "peleador2": {"type": "string"},
                    "odds2": {"type": "string"}
                },
                "required": ["peleador1", "odds1", "peleador2", "odds2"]
            }
        }
    }
}
