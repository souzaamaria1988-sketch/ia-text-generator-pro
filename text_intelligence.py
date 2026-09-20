#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent
MEMORY = BASE / "memory"
MEMORY.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def save_json(path, data):
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def record_feedback(prompt, materia, quality, mode):
    stats_path = MEMORY / "stats.json"
    stats = load_json(stats_path, {"gerados": 0, "total_qualidade": 0.0, "qualidade_media": 0.0})

    stats["gerados"] += 1
    stats["total_qualidade"] += quality
    stats["qualidade_media"] = round(stats["total_qualidade"] / stats["gerados"], 4)
    save_json(stats_path, stats)

    if quality >= 0.7:
        path = MEMORY / "successes.json"
    else:
        path = MEMORY / "errors.json"

    entries = load_json(path, [])
    entries.append({
        "data": datetime.datetime.now().isoformat(),
        "prompt": prompt,
        "materia": materia,
        "quality": quality,
        "mode": mode,
    })
    entries = entries[-500:]
    save_json(path, entries)

    return stats
