#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def analyze_text(text, prompt="", materia=""):
    words = (text or "").split()
    total = max(1, len(words))
    unique = len(set(words))

    length_score = min(1.0, total / 500.0)
    diversity_score = unique / total
    prompt_tokens = set((prompt or "").lower().split())
    text_tokens = set((text or "").lower().split())

    precision = 0.7
    if prompt_tokens:
        precision = len(prompt_tokens & text_tokens) / max(1, len(prompt_tokens))

    overall = round(
        0.30 * length_score +
        0.25 * diversity_score +
        0.25 * precision +
        0.20 * (1.0 if materia and materia.lower() in text.lower() else 0.5),
        4
    )

    return {
        "overall": overall,
        "metrics": {
            "coerencia": round(diversity_score, 4),
            "completude": round(length_score, 4),
            "clareza": round(min(1.0, total / 300.0), 4),
            "profundidade": round(min(1.0, total / 800.0), 4),
            "precisao": round(precision, 4),
            "formatacao": round(1.0 if "[" in text else 0.6, 4),
            "legibilidade": round(min(1.0, 300.0 / max(1, total / max(1, text.count(".")))), 4),
        }
    }
