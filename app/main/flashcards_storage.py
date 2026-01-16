import json
import os
from datetime import datetime, timezone

from flask import current_app


def _storage_paths():
    instance_dir = current_app.instance_path
    os.makedirs(instance_dir, exist_ok=True)
    store_path = os.path.join(instance_dir, "flashcards.json")
    seed_path = os.path.join(current_app.root_path, "static", "data", "flashcards_seed.json")
    return store_path, seed_path


def load_flashcard_store():
    store_path, seed_path = _storage_paths()
    if not os.path.exists(store_path):
        with open(seed_path, "r", encoding="utf-8") as seed_file:
            data = json.load(seed_file)
        _stamp_last_updated(data)
        _write_store(store_path, data)
        return data

    with open(store_path, "r", encoding="utf-8") as store_file:
        data = json.load(store_file)
    _ensure_stats(data)
    return data


def save_flashcard_store(data):
    store_path, _ = _storage_paths()
    _stamp_last_updated(data)
    _write_store(store_path, data)


def _write_store(store_path, data):
    with open(store_path, "w", encoding="utf-8") as store_file:
        json.dump(data, store_file, indent=2, ensure_ascii=False)


def _ensure_stats(data):
    data.setdefault(
        "stats",
        {
            "total_points": 0,
            "sessions": 0,
            "best_streak": 0,
            "last_played": None,
        },
    )


def _stamp_last_updated(data):
    _ensure_stats(data)
    data["stats"]["last_played"] = datetime.now(timezone.utc).isoformat()
