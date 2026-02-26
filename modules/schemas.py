from dataclasses import dataclass

@dataclass
class PickResult:
    match: str
    selection: str
    probability: float
    odd: float  # <--- Asegúrate de que se llame 'odd'
    ev: float
