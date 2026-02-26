from dataclasses import dataclass

@dataclass
class PickResult:
    match: str
    selection: str
    probability: float
    odd: float
    ev: float


@dataclass
class ParlayResult:
    picks: list
    total_odds: float
    combined_probability: float
    total_ev: float
