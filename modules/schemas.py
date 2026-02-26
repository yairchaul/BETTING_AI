from dataclasses import dataclass


@dataclass
class Pick:
    match: str
    selection: str
    probability: float
    odd: float
