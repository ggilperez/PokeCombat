import requests
import json
import os
from typing import List, Dict
from .models import Pokemon, PokemonStats, Move

CACHE_FILE = os.path.join("PokeCombat", "data", "pokemon_cache.json")
BASE_URL = "https://pokeapi.co/api/v2"

class PokeClient:
    def __init__(self):
        self.move_cache = {}  # temporary memory cache for moves during fetch

    def fetch_first_100_pokemons(self) -> List[Pokemon]:
        # Check if local cache exists
        # Ensure path is handled correctly if running from root C:\projects
        # If running from C:\projects, CACHE_FILE would be PokeCombat\data\pokemon_cache.json which is correct for C:\projects\PokeCombat\data\pokemon_cache.json if we are careful?
        # Actually in the previous setup, we ran from parent folder.
        # Now the files are in C:\projects\PokeCombat.
        # If I run python -m src.poke_client inside C:\projects\PokeCombat, then CWD is C:\projects\PokeCombat.
        # So "PokeCombat/data/..." would look for C:\projects\PokeCombat\PokeCombat\data... which is WRONG.
        # I should fix the path to be relative to the file or just "data/pokemon_cache.json".
        
        # FIXING PATH FOR ROBUSTNESS
        current_dir = os.path.dirname(os.path.abspath(__file__)) # src/
        project_root = os.path.dirname(current_dir) # PokeCombat/
        data_dir = os.path.join(project_root, "data")
        cache_path = os.path.join(data_dir, "pokemon_cache.json")
        
        if os.path.exists(cache_path):
            print("Loading from cache...")
            with open(cache_path, "r") as f:
                data = json.load(f)
                return [Pokemon(**p) for p in data]

        print("Fetching data from PokeAPI (this may take a while)...")
        pokemons = []
        
        # 1. Get list
        res = requests.get(f"{BASE_URL}/pokemon?limit=100")
        res.raise_for_status()
        results = res.json()["results"]

        for i, item in enumerate(results):
            print(f"Fetching {item['name']} ({i+1}/100)...")
            p_res = requests.get(item["url"])
            p_data = p_res.json()
            
            # Parse basics
            p_id = p_data["id"]
            name = p_data["name"]
            types = [t["type"]["name"] for t in p_data["types"]]
            
            # Parse Stats
            stats_dict = {s["stat"]["name"]: s["base_stat"] for s in p_data["stats"]}
            stats = PokemonStats(
                hp=stats_dict.get("hp", 0),
                attack=stats_dict.get("attack", 0),
                defense=stats_dict.get("defense", 0),
                speed=stats_dict.get("speed", 0)
            )

            # Parse Moves (Limit to top 4 level-up moves for simplicity)
            # We filter for moves that have power (attack moves)
            moves = []
            chosen_moves = p_data["moves"][:15] # Take a chunk to search through
            
            count = 0
            for m_entry in chosen_moves:
                if count >= 4:
                    break
                
                move_url = m_entry["move"]["url"]
                move_data = self._get_move_data(move_url)
                
                if move_data and move_data.power is not None:
                    moves.append(move_data)
                    count += 1
            
            pokemons.append(Pokemon(
                id=p_id,
                name=name,
                types=types,
                stats=stats,
                moves=moves
            ))

        # Save to cache
        print("Saving to cache...")
        with open(cache_path, "w") as f:
            json.dump([p.model_dump() for p in pokemons], f, indent=2)
            
        return pokemons

    def _get_move_data(self, url: str) -> Move | None:
        if url in self.move_cache:
            return self.move_cache[url]
        
        try:
            res = requests.get(url)
            if res.status_code != 200:
                return None
            data = res.json()
            
            move = Move(
                name=data["name"],
                power=data["power"] if data["power"] else 0,
                accuracy=data["accuracy"] if data["accuracy"] else 100,
                type=data["type"]["name"],
                damage_class=data["damage_class"]["name"]
            )
            self.move_cache[url] = move
            return move
        except Exception:
            return None

if __name__ == "__main__":
    client = PokeClient()
    client.fetch_first_100_pokemons()
