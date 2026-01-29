from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from typing import List, Dict
from pydantic import BaseModel
from .poke_client import PokeClient
from .battle_engine import run_simulation_batch
from .models import Pokemon

pokemons: List[Pokemon] = []
pokemon_map: Dict[int, Pokemon] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global pokemons, pokemon_map
    client = PokeClient()
    print("Loading Pokemon data...")
    # This will load from cache if available, or fetch if not.
    # Ideally we wait for the initial fetch script to finish so we have a full cache.
    pokemons = client.fetch_first_100_pokemons()
    pokemon_map = {p.id: p for p in pokemons}
    print(f"Loaded {len(pokemons)} Pokemons.")
    yield
    # Shutdown

app = FastAPI(title="PokeCombat", lifespan=lifespan)

@app.get("/pokemons")
def get_pokemons():
    return [{"id": p.id, "name": p.name} for p in pokemons]

@app.get("/battle/{p1_id}/{p2_id}")
def battle(p1_id: int, p2_id: int):
    p1 = pokemon_map.get(p1_id)
    p2 = pokemon_map.get(p2_id)
    
    if not p1 or not p2:
        raise HTTPException(status_code=404, detail="Pokemon not found")
        
    stats = run_simulation_batch(p1, p2, n=100)
    return {
        "pokemon_1": p1.name,
        "pokemon_2": p2.name,
        "simulations": 100,
        "results": stats
    }
