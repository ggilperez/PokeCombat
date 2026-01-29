import requests
import json
import os
from typing import List, Dict
from .models import Pokemon, PokemonStats, Move

from .database import init_db, save_pokemon, get_all_pokemons

BASE_URL = "https://pokeapi.co/api/v2"

class PokeClient:
    def __init__(self):
        self.move_cache = {}  # temporary memory cache for moves during fetch
        init_db() # Ensure DB exists

    def fetch_first_100_pokemons(self) -> List[Pokemon]:
        # Check if we have data in DB
        existing = get_all_pokemons()
        if len(existing) >= 100:
            print("Loading from database...")
            return existing

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
            
            p = Pokemon(
                id=p_id,
                name=name,
                types=types,
                stats=stats,
                moves=moves
            )
            pokemons.append(p)
            save_pokemon(p) # Save progressively

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
