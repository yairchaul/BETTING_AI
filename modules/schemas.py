from dataclasses import dataclass

@dataclass
class Game:
    market: str
    home: str
    home_odd: str
    draw_odd: str
    away: str
    away_odd: str


@dataclass
class Pick:
    match: str
    selection: str
    probability: float
    odd: float
