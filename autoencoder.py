#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import pathlib

try:
    import numpy as np
except Exception:
    np = None


class Autoencoder:
    def __init__(self, input_dim=256, latent_dim=16, seed=42):
        if np is None:
            raise RuntimeError("Numpy é necessário para usar o Autoencoder.")

        rng = np.random.default_rng(seed)
        self.W = rng.normal(0, 0.01, size=(input_dim, latent_dim)).astype(np.float32)
        self.V = rng.normal(0, 0.01, size=(latent_dim, input_dim)).astype(np.float32)

    def train_batch(self, X, lr=0.01):
        Z = X @ self.W
        R = Z @ self.V
        error = R - X
        loss = float(np.mean(error ** 2))

        n = max(1, len(X))
        grad_W = (X.T @ (error @ self.V.T)) / n
        grad_V = (Z.T @ error) / n

        self.W -= lr * grad_W
        self.V -= lr * grad_V

        return loss

    def encode(self, X):
        return X @ self.W

    def decode(self, Z):
        return Z @ self.V

    def save(self, path, quantize=True):
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        config = {
            "input_dim": int(self.W.shape[0]),
            "latent_dim": int(self.W.shape[1]),
            "quantized": bool(quantize),
        }

        path.with_suffix(".json").write_text(json.dumps(config, indent=2), encoding="utf-8")

        if quantize:
            scale_w = float(max(np.abs(self.W).max(), 1e-6)) / 127.0
            scale_v = float(max(np.abs(self.V).max(), 1e-6)) / 127.0

            qw = np.round(self.W / scale_w).clip(-127, 127).astype(np.int8)
            qv = np.round(self.V / scale_v).clip(-127, 127).astype(np.int8)

            np.savez_compressed(
                path,
                qw=qw,
                qv=qv,
                scale_w=np.float32(scale_w),
                scale_v=np.float32(scale_v),
                quantized=np.int8(1)
            )
        else:
            np.savez_compressed(
                path,
                W=self.W,
                V=self.V,
                quantized=np.int8(0)
            )

    @classmethod
    def load(cls, path):
        path = pathlib.Path(path)
        config = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
        model = cls(config["input_dim"], config["latent_dim"])

        data = np.load(path)
        quantized = int(data["quantized"]) if "quantized" in data else 0

        if quantized == 1:
            model.W = data["qw"].astype(np.float32) * float(data["scale_w"])
            model.V = data["qv"].astype(np.float32) * float(data["scale_v"])
        else:
            model.W = data["W"].astype(np.float32)
            model.V = data["V"].astype(np.float32)

        return model
