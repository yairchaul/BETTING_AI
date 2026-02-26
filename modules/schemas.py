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
    odd: float  # <--- Este nombre debe ser exacto para corregir el AttributeError
    ev: float
