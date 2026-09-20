#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib

BASE = pathlib.Path(__file__).resolve().parent
TRAINING = BASE / "training_input"
SUBJECTS = ["matematica", "portugues", "ingles", "fisica", "quimica", "biologia", "historia", "geografia", "filosofia", "sociologia", "artes", "educacao_fisica", "ciencias", "literatura", "redacao", "estatistica", "economia", "psicologia", "astronomia", "meio_ambiente", "programacao"]
NL = chr(10)


def main():
    for subject in SUBJECTS:
        folder = TRAINING / subject
        folder.mkdir(parents=True, exist_ok=True)

        file1 = folder / "01_conteudo.txt"
        file2 = folder / "02_atividades.txt"

        content1 = NL.join([
            f"AULA DE {subject.upper()}",
            "",
            f"Conteúdo educacional gerado para {subject}.",
            "Objetivo: apoiar estudo com explicações claras e exemplos.",
            ""
        ])

        content2 = NL.join([
            f"ATIVIDADES DE {subject.upper()}",
            "",
            "1. Defina o conceito principal.",
            "2. Dê um exemplo prático.",
            "3. Explique a importância do tema.",
            ""
        ])

        if not file1.exists():
            file1.write_text(content1, encoding="utf-8")

        if not file2.exists():
            file2.write_text(content2, encoding="utf-8")

    print("Dataset expandido.")


if __name__ == "__main__":
    main()
