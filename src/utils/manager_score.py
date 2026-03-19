import json
import os

FILE = "assets/data/leaderboard.json"


def load_scores():
    if not os.path.exists(FILE):
        return {"facile": [], "moyen": [], "difficile": []}

    with open(FILE, "r") as f:
        return json.load(f)


def save_scores(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_score(name, time, difficulty):
    data = load_scores()

    data[difficulty].append({
        "name": name,
        "time": time
    })

    # Trier (meilleur temps en premier)
    data[difficulty].sort(key=lambda x: x["time"])

    # Garder top 5
    data[difficulty] = data[difficulty][:5]

    save_scores(data)