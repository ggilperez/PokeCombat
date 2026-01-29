import random
from typing import List, Tuple, Dict
from .models import Pokemon, Move

# Simplified Type Chart (AttackerRow vs DefenderCol)
TYPE_CHART = {
    "normal": {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 2.0, "bug": 2.0, "rock": 0.5, "dragon": 0.5, "steel": 2.0},
    "water": {"fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0, "rock": 2.0, "dragon": 0.5},
    "grass": {"fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5, "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0, "dragon": 0.5, "steel": 0.5},
    "electric": {"water": 2.0, "electric": 0.5, "grass": 0.5, "ground": 0.0, "flying": 2.0, "dragon": 0.5},
    "ice": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 0.5, "ground": 2.0, "flying": 2.0, "dragon": 2.0, "steel": 0.5},
    "fighting": {"normal": 2.0, "ice": 2.0, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "rock": 2.0, "ghost": 0.0, "dark": 2.0, "steel": 2.0, "fairy": 0.5},
    "poison": {"grass": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0.0, "fairy": 2.0},
    "ground": {"fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0, "flying": 0.0, "bug": 0.5, "rock": 2.0, "steel": 2.0},
    "flying": {"electric": 0.5, "grass": 2.0, "fighting": 2.0, "bug": 2.0, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0.0, "steel": 0.5},
    "bug": {"fire": 0.5, "grass": 2.0, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2.0, "ghost": 0.5, "dark": 2.0, "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2.0, "ice": 2.0, "fighting": 0.5, "ground": 0.5, "flying": 2.0, "bug": 2.0, "steel": 0.5},
    "ghost": {"normal": 0.0, "psychic": 2.0, "ghost": 2.0, "dark": 0.5},
    "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2.0, "rock": 2.0, "steel": 0.5, "fairy": 2.0},
    "dark": {"fighting": 0.5, "psychic": 2.0, "ghost": 2.0, "dark": 0.5, "fairy": 0.5},
    "fairy": {"fire": 0.5, "fighting": 2.0, "poison": 0.5, "dragon": 2.0, "dark": 2.0, "steel": 0.5}
}

def get_type_effectiveness(move_type: str, defender_types: List[str]) -> float:
    multiplier = 1.0
    for dt in defender_types:
        if move_type in TYPE_CHART:
            multiplier *= TYPE_CHART[move_type].get(dt, 1.0)
    return multiplier

class Battle:
    def __init__(self, pokemon_a: Pokemon, pokemon_b: Pokemon):
        # Create deep copies to avoid modifying original caching state
        self.p1 = pokemon_a.model_copy(deep=True)
        self.p2 = pokemon_b.model_copy(deep=True)
        self.log = []
        self.turn = 1

    def calculate_damage(self, attacker: Pokemon, defender: Pokemon, move: Move) -> int:
        level = 50
        a = attacker.stats.attack
        d = defender.stats.defense
        
        # Base Damage Formula
        base_damage = (((2 * level / 5 + 2) * move.power * a / d) / 50 + 2)
        
        # STAB
        stab = 1.5 if move.type in attacker.types else 1.0
        
        # Type Effectiveness
        type_eff = get_type_effectiveness(move.type, defender.types)
        
        # Random Factor
        random_factor = random.uniform(0.85, 1.0)
        
        final_damage = int(base_damage * stab * type_eff * random_factor)
        return final_damage

    def execute_turn(self):
        # Determine order
        if self.p1.stats.speed > self.p2.stats.speed:
            first, second = self.p1, self.p2
        elif self.p2.stats.speed > self.p1.stats.speed:
            first, second = self.p2, self.p1
        else:
            first, second = (self.p1, self.p2) if random.random() > 0.5 else (self.p2, self.p1)
            
        self.perform_move(first, second)
        if second.stats.hp <= 0: return 
        
        self.perform_move(second, first)
        
        self.turn += 1

    def perform_move(self, attacker: Pokemon, defender: Pokemon):
        if not attacker.moves:
             self.log.append(f"{attacker.name} tried to attack but has no moves!")
             # Struggle damage or 1?
             defender.stats.hp -= 1
             return

        move = random.choice(attacker.moves)
        
        damage = self.calculate_damage(attacker, defender, move)
        defender.stats.hp -= damage
        self.log.append(f"{attacker.name} used {move.name}! Dealt {damage} damage. {defender.name} HP: {max(0, defender.stats.hp)}")

    def run(self) -> str:
        while self.p1.stats.hp > 0 and self.p2.stats.hp > 0:
            self.execute_turn()
            if self.turn > 50: # Avoid infinite loops
                break
        
        if self.p1.stats.hp > 0 and self.p2.stats.hp <= 0:
            return self.p1.name
        elif self.p2.stats.hp > 0 and self.p1.stats.hp <= 0:
            return self.p2.name
        else:
            return "Draw"

def run_simulation_batch(p1: Pokemon, p2: Pokemon, n=100) -> Dict[str, int]:
    results = {p1.name: 0, p2.name: 0, "Draw": 0}
    for _ in range(n):
        battle = Battle(p1, p2)
        winner = battle.run()
        results[winner] += 1
    return results
