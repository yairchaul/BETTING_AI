from dataclasses import dataclass
from typing import List

@dataclass
class PickResult:
    match: str
    selection: str
    probability: float
    odd: float
    ev: float
    log: str = ""  # Agregamos el campo log con un valor por defecto
