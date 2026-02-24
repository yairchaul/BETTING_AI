from modules.schemas import BetData
from modules.ev_engine import calculate_ev


def analyze_betting_image(image):
    """
    Simulated OCR + AI parsing
    """

    # ⚠️ luego aquí conectas OpenAI Vision / OCR
    extracted_team = "Team A"
    extracted_odds = 2.10
    predicted_probability = 0.55

    bet = BetData(
        team=extracted_team,
        odds=extracted_odds,
        probability=predicted_probability
    )

    result = calculate_ev(bet)

    return bet, result
