from dataclasses import dataclass

@dataclass
class Match:
    home: str
    away: str

@dataclass
class Pick:
    partido: str
    pick: str
    probabilidad: int
    cuota: float
