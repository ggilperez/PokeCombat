# PokeCombat ⚔️

A Python-based Pokemon Battle Simulator and API.

**This project is a Proof of Concept created to test Antigravity and Vibe Coding capabilities.**

## Features
- **FastAPI** backend for high-performance API endpoints.
- **SQLite** database for persisting Pokemon data and battle stats.
- **Battle Engine** simulating turn-based combat with Type Effectiveness logic.
- **Analysis Tools**: Calculate win rates against specific Pokemon types (e.g. Charmander vs Grass).

## Quick Start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   python -m uvicorn src.main:app --reload
   ```
3. Visit `http://127.0.0.1:8000/docs` for the interactive API documentation.
