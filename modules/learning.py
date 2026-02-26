import json
from pathlib import Path

DB_FILE = "learning_db.json"


def load_db():
    path = Path(DB_FILE)
    if path.exists():
        return json.loads(path.read_text())
    return []


def save_result(pick, resultado):
    db = load_db()

    db.append({
        "partido": pick.partido,
        "pick": pick.pick,
        "cuota": pick.cuota,
        "probabilidad": pick.probabilidad,
        "resultado": resultado
    })

    Path(DB_FILE).write_text(json.dumps(db, indent=2))


def success_rate():
    db = load_db()
    if not db:
        return 0

    wins = sum(1 for x in db if x["resultado"] == "win")
    return round((wins / len(db)) * 100, 2)
