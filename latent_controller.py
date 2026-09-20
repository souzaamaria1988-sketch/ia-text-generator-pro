#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class LatentController:
    def params_from_latent(self, latent):
        if not latent:
            return {
                "formalidade": 0.5,
                "complexidade": 0.5,
                "detalhamento": 0.5,
                "tom_academico": 0.5,
                "tom_conversacional": 0.5,
                "uso_exemplos": True,
                "uso_analogias": True,
                "tamanho": "medio",
            }

        latent = list(latent)
        n = max(1, len(latent))
        avg = sum(latent) / n

        return {
            "formalidade": round(min(1.0, max(0.0, 0.5 + avg)), 4),
            "complexidade": round(min(1.0, max(0.0, 0.5 + avg / 2)), 4),
            "detalhamento": round(min(1.0, max(0.0, 0.5 + avg / 3)), 4),
            "tom_academico": round(min(1.0, max(0.0, 0.6 + avg / 4)), 4),
            "tom_conversacional": round(min(1.0, max(0.0, 0.4 - avg / 4)), 4),
            "uso_exemplos": True,
            "uso_analogias": True,
            "tamanho": "longo" if avg > 0.2 else "curto" if avg < -0.2 else "medio",
        }
