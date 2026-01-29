import sys
import os

# Ensure src can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models import Pokemon, PokemonStats, Move
from src.battle_engine import Battle, run_simulation_batch

def test_battle():
    p1 = Pokemon(
        id=1, name="Bulbasaur", types=["grass", "poison"],
        stats=PokemonStats(hp=45, attack=49, defense=49, speed=45),
        moves=[Move(name="Tackle", power=40, type="normal", damage_class="physical")]
    )
    p2 = Pokemon(
        id=4, name="Charmander", types=["fire"],
        stats=PokemonStats(hp=39, attack=52, defense=43, speed=65),
        moves=[Move(name="Scratch", power=40, type="normal", damage_class="physical")]
    )
    
    print("Running single battle (Bulbasaur vs Charmander)...")
    b = Battle(p1, p2)
    winner = b.run()
    print(f"Winner: {winner}")
    print("Log:")
    for l in b.log:
        print(l)
        
    print("\nRunning batch simulation (n=100)...")
    stats = run_simulation_batch(p1, p2, n=100)
    print(stats)
    
    # Validation: Charmander should win most because Fire > Grass and Speed
    win_rate_p2 = stats["Charmander"] / 100.0
    print(f"Charmander win rate: {win_rate_p2}")

if __name__ == "__main__":
    test_battle()
