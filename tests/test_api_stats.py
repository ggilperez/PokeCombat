import requests
import json

def test_api_stats():
    url = "http://127.0.0.1:8000/battle/stats/4/vs_type/grass"
    print(f"Testing POST {url}...")
    try:
        res = requests.post(url)
        res.raise_for_status()
        data = res.json()
        print("Success!")
        print(json.dumps(data, indent=2))
        
        # Simple validation
        if data["attacker"] == "charmander" and data["vs_type"] == "grass":
            print("Validation passed: Attacker and Type match.")
            if float(data["global_win_rate"].strip('%')) > 50:
                 print("Validation passed: Charmander has high win rate against Grass.")
            else:
                 print("Warning: Charmander win rate seems low? Check logic.")
        else:
             print("Validation failed: Unexpected response fields.")
             
    except Exception as e:
        print(f"Failed: {e}")
        if hasattr(e, 'response') and e.response:
             print(e.response.text)

if __name__ == "__main__":
    test_api_stats()
