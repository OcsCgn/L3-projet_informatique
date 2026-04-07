import json
import os

FILE = "assets/data/leaderboard.json"


def load_scores():
    default_data = {
        "facile": {"time": [], "energy": []},
        "moyen": {"time": [], "energy": []},
        "difficile": {"time": [], "energy": []}
    }
    if not os.path.exists(FILE):
        return default_data

    try:
        with open(FILE, "r") as f:
            data = json.load(f)
            # Sécurité : si l'ancien format est détecté, on le remet à zéro
            if isinstance(data.get("facile"), list):
                return default_data
            return data
    except:
        return default_data


def save_scores(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_score(name, time, energy, difficulty):
    data = load_scores()

    entry = {
        "name": name,
        "time": time,
        "energy": energy
    }

    # 1. Mise à jour du Top 5 TEMPS (Tri croissant)
    data[difficulty]["time"].append(entry)
    data[difficulty]["time"].sort(key=lambda x: x["time"])
    data[difficulty]["time"] = data[difficulty]["time"][:5]

    # 2. Mise à jour du Top 5 ENERGIE (Tri décroissant : reverse=True)
    data[difficulty]["energy"].append(entry)
    data[difficulty]["energy"].sort(key=lambda x: x["energy"], reverse=True)
    data[difficulty]["energy"] = data[difficulty]["energy"][:5]

    save_scores(data)