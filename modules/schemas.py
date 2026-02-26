from dataclasses import dataclass
from typing import List

@dataclass
class PickResult:
    match: str
    selection: str
    probability: float
    odd: float
    ev: float

@dataclass
class ParlayResult:
    matches: List[str]
    total_odd: float
    combined_prob: float
    total_ev: float
