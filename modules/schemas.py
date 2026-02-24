from dataclasses import dataclass

@dataclass
class BetData:
    team: str
    odds: float
    probability: float

@dataclass
class EVResult:
    ev: float
    edge: float
