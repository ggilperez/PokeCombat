from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List, Dict
from pydantic import BaseModel
from .poke_client import PokeClient
from .battle_engine import run_simulation_batch
from .models import Pokemon

from .database import get_pokemon, get_pokemons_by_type
from .battle_engine import run_simulation_batch, run_type_simulation

app = FastAPI(title="PokeCombat")

@app.get("/")
def read_root():
    return {"message": "Welcome to PokeCombat API! Visit /docs for documentation."}

@app.get("/pokemons")
def get_pokemons_list(): # Renamed to avoid name collision with database function
    from .database import get_all_pokemons
    pokemons = get_all_pokemons()
    return [{"id": p.id, "name": p.name} for p in pokemons]

@app.get("/battle/{p1_id}/{p2_id}")
def battle(p1_id: int, p2_id: int):
    p1 = get_pokemon(p1_id)
    p2 = get_pokemon(p2_id)
    
    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="Pokemon not found")
        
    stats = run_simulation_batch(p1, p2, n=100)
    return {
        "pokemon_1": p1.name,
        "pokemon_2": p2.name,
        "simulations": 100,
        "results": stats
    }

@app.post("/battle/stats/{pokemon_id}/vs_type/{type_name}")
def battle_vs_type(pokemon_id: int, type_name: str):
    attacker = get_pokemon(pokemon_id)
    if not attacker:
        raise HTTPException(status_code=404, detail="Pokemon not found")
        
    defenders = get_pokemons_by_type(type_name)
    if not defenders:
        return {"message": f"No pokemon found with type {type_name}"}
        
    # Remove attacker from defenders if present
    defenders = [d for d in defenders if d.id != attacker.id]
    
    stats = run_type_simulation(attacker, type_name, defenders)
    return stats
