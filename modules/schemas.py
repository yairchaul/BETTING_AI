from dataclasses import dataclass

@dataclass
class Match:
    home: str
    away: str

@dataclass
class PickResult:
    match: str
    selection: str
    probability: float
    odd: float  # <--- Crucial: Debe llamarse 'odd' para corregir el AttributeError
    ev: float
