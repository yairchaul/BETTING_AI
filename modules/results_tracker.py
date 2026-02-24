import json
from datetime import datetime
from pathlib import Path

RESULTS_FILE = Path("betting_results.json")


def load_results():
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    return []


def save_result(bet_data, prediction):
    results = load_results()

    record = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "teams": bet_data.get("teams"),
        "market": bet_data.get("market"),
        "odds": bet_data.get("odds"),
        "prediction": prediction,
        "result": "PENDING"
    }

    results.append(record)

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)


def update_result(index, outcome):
    results = load_results()

    if 0 <= index < len(results):
        results[index]["result"] = outcome

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)
