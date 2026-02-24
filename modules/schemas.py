from dataclasses import dataclass

@dataclass
class Match:
    local: str
    visitante: str

@dataclass
class MatchResult:
    partido: str
    pick: str
    probabilidad: int

@dataclass
class EVResult:
    ev: float
    edge: float
