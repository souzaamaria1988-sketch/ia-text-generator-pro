#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import pathlib
import re
import zlib

BASE = pathlib.Path(__file__).resolve().parent
TRAINING = BASE / "training_input"
MODELS = BASE / "models"
MODELS.mkdir(parents=True, exist_ok=True)

try:
    import numpy as np
    from autoencoder import Autoencoder
    NUMPY_OK = True
except Exception:
    NUMPY_OK = False


def collect_files():
    files = []
    if TRAINING.exists():
        for path in TRAINING.rglob("*"):
            if path.is_file() and path.suffix in {".txt", ".py", ".md"}:
                files.append(path)
    return files


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def vectorize(text, dim=256):
    vec = np.zeros(dim, dtype=np.float32)
    for token in tokenize(text):
        idx = zlib.crc32(token.encode("utf-8")) % dim
        vec[idx] += 1.0

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm

    return vec


def main():
    parser = argparse.ArgumentParser(description="Treino simples para IA Text Generator Pro")
    parser.add_argument("--epochs", type=int, default=3)
    args = parser.parse_args()

    files = collect_files()

    log = {
        "timestamp": datetime.datetime.now().isoformat(),
        "epochs_requested": args.epochs,
        "files_found": len(files),
    }

    if not NUMPY_OK:
        log["status"] = "skipped: numpy not installed"
        (MODELS / "training_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Numpy indisponível. Treino pulado com segurança.")
        return

    texts = []
    subjects = []

    for file_path in files:
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if len(text.strip()) > 20:
            texts.append(text)
            subject = file_path.parent.name
            subjects.append(subject if subject != "training_input" else "geral")

    if not texts:
        texts = ["Conteúdo educacional padrão sobre matemática, ciências e programação."]
        subjects = ["geral"]

    X = np.vstack([vectorize(text) for text in texts])

    autoencoder = Autoencoder(input_dim=X.shape[1], latent_dim=16)
    best_loss = 1e18
    patience = 0

    for epoch in range(max(1, args.epochs)):
        loss = autoencoder.train_batch(X, lr=0.01)
        log["last_loss"] = float(loss)

        if loss < best_loss - 1e-6:
            best_loss = loss
            patience = 0
            autoencoder.save(MODELS / "autoencoder" / "model.npz", quantize=True)
        else:
            patience += 1
            if patience > 5:
                break

    latents = autoencoder.encode(X)
    experts = {}

    for subject, latent in zip(subjects, latents):
        if subject not in experts:
            experts[subject] = {"sum": np.zeros(latent.shape[0], dtype=np.float32), "count": 0}

        experts[subject]["sum"] += latent
        experts[subject]["count"] += 1

    experts_output = {}

    for subject, data in experts.items():
        centroid = data["sum"] / max(1, data["count"])
        experts_output[subject] = {
            "count": int(data["count"]),
            "centroid_preview": [float(x) for x in centroid[:8]],
        }

    moe_dir = MODELS / "moe"
    moe_dir.mkdir(parents=True, exist_ok=True)
    (moe_dir / "experts.json").write_text(json.dumps(experts_output, indent=2, ensure_ascii=False), encoding="utf-8")

    log["status"] = "ok"
    log["experts"] = len(experts_output)

    (MODELS / "training_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Treino concluído.")


if __name__ == "__main__":
    main()
