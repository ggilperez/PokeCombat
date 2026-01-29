from pydantic import BaseModel
from typing import List, Optional

class PokemonStats(BaseModel):
    hp: int
    attack: int
    defense: int
    speed: int

class Move(BaseModel):
    name: str
    power: int
    accuracy: Optional[int] = 100
    type: str
    damage_class: str  # physical or special

class Pokemon(BaseModel):
    id: int
    name: str
    types: List[str]
    stats: PokemonStats
    moves: List[Move]
