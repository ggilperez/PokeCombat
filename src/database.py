import sqlite3
import json
import os
from typing import List, Optional
from .models import Pokemon, PokemonStats, Move

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pokecombat.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Pokemon Table
    # We store types as a comma-separated string or JSON string to simplify
    # Stats also stored as JSON or separate columns
    c.execute('''
    CREATE TABLE IF NOT EXISTS pokemons (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        types TEXT,  -- JSON list of strings
        hp INTEGER,
        attack INTEGER,
        defense INTEGER,
        speed INTEGER
    )
    ''')
    
    # Moves Table
    c.execute('''
    CREATE TABLE IF NOT EXISTS moves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pokemon_id INTEGER,
        name TEXT,
        power INTEGER,
        accuracy INTEGER,
        type TEXT,
        damage_class TEXT,
        FOREIGN KEY(pokemon_id) REFERENCES pokemons(id)
    )
    ''')
    
    conn.commit()
    conn.close()

def save_pokemon(pokemon: Pokemon):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Insert Pokemon
    c.execute('''
    INSERT OR REPLACE INTO pokemons (id, name, types, hp, attack, defense, speed)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        pokemon.id,
        pokemon.name,
        json.dumps(pokemon.types),
        pokemon.stats.hp,
        pokemon.stats.attack,
        pokemon.stats.defense,
        pokemon.stats.speed
    ))
    
    # Delete old moves for this pokemon to ensure clean state on re-save
    c.execute('DELETE FROM moves WHERE pokemon_id = ?', (pokemon.id,))
    
    # Insert Moves
    for m in pokemon.moves:
        c.execute('''
        INSERT INTO moves (pokemon_id, name, power, accuracy, type, damage_class)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            pokemon.id,
            m.name,
            m.power,
            m.accuracy,
            m.type,
            m.damage_class
        ))
        
    conn.commit()
    conn.close()

def get_pokemon(pokemon_id: int) -> Optional[Pokemon]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('SELECT * FROM pokemons WHERE id = ?', (pokemon_id,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return None
        
    # Row: id, name, types, hp, attack, defense, speed
    p_id, name, types_json, hp, attack, defense, speed = row
    
    # Get Moves
    c.execute('SELECT name, power, accuracy, type, damage_class FROM moves WHERE pokemon_id = ?', (p_id,))
    moves_rows = c.fetchall()
    moves = []
    for m_row in moves_rows:
        moves.append(Move(
            name=m_row[0],
            power=m_row[1],
            accuracy=m_row[2],
            type=m_row[3],
            damage_class=m_row[4]
        ))
        
    conn.close()
    
    return Pokemon(
        id=p_id,
        name=name,
        types=json.loads(types_json),
        stats=PokemonStats(hp=hp, attack=attack, defense=defense, speed=speed),
        moves=moves
    )

def get_all_pokemons() -> List[Pokemon]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id FROM pokemons')
    ids = [row[0] for row in c.fetchall()]
    conn.close()
    
    # This might be slow if we have many, but for 100 it's fine.
    # A more optimized query would join tables, but keeping it simple for now.
    return [get_pokemon(i) for i in ids if i is not None]

def get_pokemons_by_type(type_name: str) -> List[Pokemon]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Search in JSON string is a bit hacky but works for SQLite simple usage: LIKE '%"grass"%'
    c.execute('SELECT id FROM pokemons WHERE types LIKE ?', (f'%"{type_name}"%',))
    ids = [row[0] for row in c.fetchall()]
    conn.close()
    
    return [get_pokemon(i) for i in ids if i is not None]
