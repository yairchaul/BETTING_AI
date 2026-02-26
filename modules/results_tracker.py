import json
import os

DB_FILE = "betting_history.json"

def save_parlay(data):
    history = get_history()
    history.append(data)
    with open(DB_FILE, "w") as f:
        json.dump(history, f, indent=4)

def get_history():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []
