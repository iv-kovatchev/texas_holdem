import json
import os

PLAYER_FILE = "players.json"

def load_players():
    if not os.path.exists(PLAYER_FILE):
        return []
    with open(PLAYER_FILE, 'r') as f:
        return json.load(f)
    
def save_players(players):
    with open(PLAYER_FILE, 'w') as f:
        json.dump(players, f, indent=2)

def update_player(name, chips):
    players = load_players()
    for player in players:
        if player["name"] == name:
            player["chips"] = chips
            break
    else:
        players.append({"name": name, "chips": chips})
    save_players(players)

def get_valid_players():
    return [p for p in load_players() if p["chips"] > 0]