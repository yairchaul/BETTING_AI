# modules/ev_engine.py

from modules.ev_scanner import american_to_probability, calculate_ev   # importa las funciones que ya tienes

class EVEngine:
    def __init__(self):
        # Puedes poner aquí inicializaciones futuras (modelos, umbrales, etc.)
        self.min_ev_threshold = 0.05
        pass

    def build_parlay(self, games: list):
        """
        games: lista de dicts con keys: home, away, home_odd, draw_odd, away_odd
        """
        resultados = []
        parlay_picks = []

        for g in games:
            for outcome, odds_key in [("home", "home_odd"), ("draw", "draw_odd"), ("away", "away_odd")]:
                odds_str = g.get(odds_key)
                if not odds_str or odds_str.strip() == "":
                    continue

                try:
                    odds = float(odds_str)
                except (ValueError, TypeError):
                    continue

                implied_p = american_to_probability(odds)
                # Placeholder muy básico — cámbialo cuando tengas modelo real
                model_p = 0.38 if outcome == "draw" else 0.45

                ev = calculate_ev(model_p, odds)

                if ev > self.min_ev_threshold:
                    pick_name = (
                        f"{g['home']} gana" if outcome == "home" else
                        "Empate" if outcome == "draw" else
                        f"{g['away']} gana"
                    )
                    resultados.append({
                        "partido": f"{g['home']} vs {g['away']}",
                        "pick": pick_name,
                        "probabilidad": round(model_p * 100, 1),
                        "cuota": odds_str,
                        "ev": round(ev, 3)
                    })
                    parlay_picks.append({
                        "partido": f"{g['home']} vs {g['away']}",
                        "pick": pick_name
                    })

        # Orden descendente por EV
        resultados.sort(key=lambda x: x.get("ev", 0), reverse=True)

        # Parlay: tomamos los mejores (máx 5 legs por ahora)
        parlay_picks = parlay_picks[:5]

        return resultados[:8], parlay_picks   # mostramos hasta 8 análisis + parlay

    def simulate_parlay_profit(self, parlay: list, monto: float):
        """
        Simulador simple de parlay (producto de cuotas)
        """
        if not parlay:
            return {"cuota_total": 1.0, "pago_total": monto, "ganancia_neta": 0.0}

        cuota_total = 1.0
        for pick in parlay:
            # Buscamos la cuota real del pick (esto es aproximado por ahora)
            # En futuro: mapear pick → odds exacta
            cuota_total *= 1.85   # placeholder conservador — cámbialo por cálculo real

        pago_total = monto * cuota_total
        ganancia_neta = pago_total - monto

        return {
            "cuota_total": round(cuota_total, 2),
            "pago_total": round(pago_total, 2),
            "ganancia_neta": round(ganancia_neta, 2)
        }
