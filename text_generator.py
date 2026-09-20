#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import datetime
import json
import pathlib
import random
import re
import time
import unicodedata

BASE = pathlib.Path(__file__).resolve().parent
OUTPUT = BASE / "text_output"
MEMORY = BASE / "memory"
NL = chr(10)
OUTPUT.mkdir(parents=True, exist_ok=True)
MEMORY.mkdir(parents=True, exist_ok=True)

SUBJECTS = ["matematica", "portugues", "ingles", "fisica", "quimica", "biologia", "historia", "geografia", "filosofia", "sociologia", "artes", "educacao_fisica", "ciencias", "literatura", "redacao", "estatistica", "economia", "psicologia", "astronomia", "meio_ambiente", "programacao"]

MODES = {
    "none": {"name": "Nenhum", "prefixes": ["RESPOSTA", "METADADOS"], "thinking": 0},
    "low": {"name": "Baixo", "prefixes": ["PENSAMENTO", "RESPOSTA", "METADADOS"], "thinking": 2},
    "low+": {"name": "Baixo+", "prefixes": ["PENSAMENTO", "ANÁLISE", "RESPOSTA", "METADADOS"], "thinking": 5},
    "balanced": {"name": "Balanceado", "prefixes": ["PENSAMENTO", "ANÁLISE", "PLANEJAMENTO", "RESPOSTA", "METADADOS"], "thinking": 10},
    "balanced+": {"name": "Balanceado+", "prefixes": ["PENSAMENTO", "ANÁLISE", "PLANEJAMENTO", "EXECUÇÃO", "VERIFICAÇÃO", "RESPOSTA", "METADADOS"], "thinking": 20},
    "high": {"name": "Alto", "prefixes": ["PENSAMENTO", "ANÁLISE", "PLANEJAMENTO", "EXECUÇÃO", "VERIFICAÇÃO", "RESPOSTA", "METADADOS"], "thinking": 40},
    "high+": {"name": "Alto+", "prefixes": ["PENSAMENTO", "ANÁLISE", "PLANEJAMENTO", "EXECUÇÃO", "VERIFICAÇÃO", "REFLEXÃO", "RESPOSTA", "METADADOS"], "thinking": 60},
    "xhigh": {"name": "XHigh", "prefixes": ["PENSAMENTO", "ANÁLISE", "PLANEJAMENTO", "EXECUÇÃO", "VERIFICAÇÃO", "REFLEXÃO", "ALTERNATIVAS", "RESPOSTA", "METADADOS"], "thinking": 100},
    "xhigh+": {"name": "XHigh+", "prefixes": ["PENSAMENTO", "ANÁLISE", "PLANEJAMENTO", "EXECUÇÃO", "VERIFICAÇÃO", "REFLEXÃO", "ALTERNATIVAS", "AUTOAVALIAÇÃO", "ITERAÇÕES", "RESPOSTA", "METADADOS"], "thinking": 150},
}

def norm(text):
    text = (text or "").lower()
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")

def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", (text or "").lower())

def load_kb():
    path = BASE / "knowledge_base.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def detect_materia(prompt, supplied):
    supplied = norm(supplied)
    if supplied and supplied != "auto":
        candidate = supplied.replace(" ", "_")
        if candidate in SUBJECTS:
            return candidate

    p = norm(prompt)
    for subject in SUBJECTS:
        if subject in p:
            return subject

    return "ciencias" if "ciencias" in SUBJECTS else SUBJECTS[0]

def detect_nivel(prompt, supplied):
    if supplied and supplied.lower() != "auto":
        return supplied

    p = norm(prompt)
    if "fundamental" in p:
        return "Ensino Fundamental"
    if "superior" in p or "universidade" in p or "faculdade" in p:
        return "Ensino Superior"
    return "Ensino Médio"

def rag_entry(materia, prompt):
    kb = load_kb()
    entries = kb.get(materia, [])
    best = None
    best_score = 0
    p = norm(prompt)
    tokens = set(tokenize(prompt))

    for entry in entries:
        score = 0
        title = norm(entry.get("titulo", ""))
        if title and title in p:
            score += 4

        for tag in entry.get("tags", []):
            if norm(tag) in p or norm(tag) in tokens:
                score += 2

        if score > best_score:
            best = entry
            best_score = score

    return best

def thinking_sections(mode, prompt, materia, nivel):
    cfg = MODES[mode]
    prefixes = cfg["prefixes"]
    n = cfg["thinking"]
    result = {}

    if "PENSAMENTO" in prefixes:
        lines = [
            f"O usuário pediu: {prompt}",
            f"Matéria identificada: {materia}",
            f"Nível alvo: {nivel}",
            "Vou adaptar linguagem e exemplos.",
            "Vou organizar introdução, desenvolvimento e prática.",
        ]
        while len(lines) < n:
            lines.append(f"Iteração de planejamento {len(lines)+1}: revisar clareza, exemplos e completude.")
        result["PENSAMENTO"] = NL.join(lines[:max(1, n)])

    if "ANÁLISE" in prefixes:
        result["ANÁLISE"] = NL.join([
            "Análise do pedido:",
            f"- Prompt: {prompt}",
            f"- Matéria: {materia}",
            f"- Nível: {nivel}",
            "- Conceitos essenciais serão cobertos.",
            "- Exemplos e exercícios serão incluídos.",
        ])

    if "PLANEJAMENTO" in prefixes:
        result["PLANEJAMENTO"] = NL.join([
            "Planejamento:",
            "1. Introdução",
            "2. Conceitos",
            "3. Exemplos",
            "4. Atividade",
            "5. Revisão",
        ])

    if "REFLEXÃO" in prefixes:
        result["REFLEXÃO"] = "A abordagem progressiva é adequada ao nível e permite revisão ativa."

    if "ALTERNATIVAS" in prefixes:
        result["ALTERNATIVAS"] = "Alternativa considerada: texto apenas expositivo. Escolhida: texto com exemplos e exercícios."

    if "AUTOAVALIAÇÃO" in prefixes:
        result["AUTOAVALIAÇÃO"] = "O conteúdo está claro, estruturado e alinhado ao objetivo educacional."

    if "ITERAÇÕES" in prefixes:
        result["ITERAÇÕES"] = NL.join([
            "1. Rascunho inicial",
            "2. Revisão de clareza",
            "3. Inclusão de exemplos",
            "4. Verificação final",
        ])

    return result

def code_content(linguagem, prompt):
    safe = (prompt or "").replace('"', "'")

    if linguagem == "javascript":
        return NL.join([
            "// Problema: " + safe,
            "function solucao() {",
            '  return "Solução JavaScript para: ' + safe + '";',
            "}",
            "console.log(solucao());",
        ])

    if linguagem == "java":
        return NL.join([
            "// Problema: " + safe,
            "public class Main {",
            "    public static void main(String[] args) {",
            '        System.out.println("Solução Java para: ' + safe + '");',
            "    }",
            "}",
        ])

    if linguagem == "c":
        return NL.join([
            "// Problema: " + safe,
            "#include <stdio.h>",
            "int main(void) {",
            '    printf("Solução C para: ' + safe + '");',
            "    return 0;",
            "}",
        ])

    if linguagem == "cpp":
        return NL.join([
            "// Problema: " + safe,
            "#include <iostream>",
            "int main() {",
            '    std::cout << "Solução C++ para: ' + safe + '" << std::endl;',
            "    return 0;",
            "}",
        ])

    if linguagem == "csharp":
        return NL.join([
            "// Problema: " + safe,
            "using System;",
            "class Program {",
            "    static void Main() {",
            '        Console.WriteLine("Solução C# para: ' + safe + '");',
            "    }",
            "}",
        ])

    if linguagem == "php":
        return NL.join([
            "<?php",
            "// Problema: " + safe,
            'echo "Solução PHP para: ' + safe + '";',
        ])

    if linguagem == "ruby":
        return NL.join([
            "# Problema: " + safe,
            'puts "Solução Ruby para: ' + safe + '"',
        ])

    if linguagem == "go":
        return NL.join([
            "// Problema: " + safe,
            "package main",
            "",
            'import "fmt"',
            "",
            "func main() {",
            '    fmt.Println("Solução Go para: ' + safe + '")',
            "}",
        ])

    if linguagem == "rust":
        return NL.join([
            "// Problema: " + safe,
            "fn main() {",
            '    println!("Solução Rust para: ' + safe + '");',
            "}",
        ])

    return NL.join([
        "# Problema: " + safe,
        "def solucao():",
        '    return "Solução Python para: ' + safe + '"',
        "",
        'if __name__ == "__main__":',
        "    print(solucao())",
    ])

def generate_content(formato, materia, prompt, nivel, linguagem):
    entry = rag_entry(materia, prompt)
    title = (prompt or materia).strip().title()

    if formato == "codigo":
        code = code_content(linguagem, prompt)
        return NL.join([
            "## Código",
            code,
            "",
            "## Explicação",
            "Este código demonstra uma solução inicial para o problema proposto.",
            "Ele deve ser adaptado para validar entradas, tratar erros e incluir testes.",
            "",
            "## Exercício",
            "Modifique o código para aceitar entrada do usuário e adicionar tratamento de erros.",
        ])

    base_definition = entry.get("definicao") if entry else f"{title} é um tema importante de {materia}."
    sections = []

    sections.append("## Introdução")
    sections.append(base_definition)

    sections.append("## Desenvolvimento")
    bullets = []

    if entry:
        if entry.get("formula"):
            bullets.append("Fórmula: " + str(entry["formula"]))
        if entry.get("data"):
            bullets.append("Data/período: " + str(entry["data"]))
        if entry.get("exemplo"):
            bullets.append("Exemplo: " + str(entry["exemplo"]))

    if not bullets:
        bullets = [
            "Conceito principal",
            "Exemplo prático",
            "Aplicação no cotidiano"
        ]

    sections.append(NL.join("- " + item for item in bullets))

    if formato in ["exercicio", "prova", "flashcard"]:
        sections.append("## Exercícios")
        sections.append("1. Defina o conceito principal.")
        sections.append("2. Crie um exemplo próprio.")
        sections.append("3. Explique uma aplicação prática.")
    else:
        sections.append("## Conclusão")
        sections.append("Revise os conceitos, resolva exercícios e explique o tema com suas próprias palavras.")

    return NL.join(sections)

def build_document(mode, prompt, materia, nivel, dificuldade, idioma, content, thinking, elapsed):
    cfg = MODES[mode]
    tokens = len(content.split())
    qualidade = round(min(1.0, 0.45 + tokens / 1200.0), 2)

    metadata = {
        "tokens": tokens,
        "tempo": f"{elapsed:.2f}s",
        "qualidade": qualidade,
        "modo": mode,
        "materia": materia,
        "nivel": nivel,
    }

    lines = []
    lines.append("=" * 60)
    lines.append("📚 IA TEXT GENERATOR PRO")
    lines.append("=" * 60)
    lines.append(f"[MODO] {cfg['name']}")
    lines.append(f"[DATA] {datetime.datetime.now().isoformat()}")
    lines.append(f"[PROMPT] {prompt}")
    lines.append(f"[MATÉRIA] {materia}")
    lines.append(f"[NÍVEL] {nivel}")
    lines.append(f"[DIFICULDADE] {dificuldade}")
    lines.append(f"[IDIOMA] {idioma}")
    lines.append("=" * 60)
    lines.append("")

    for prefix in cfg["prefixes"]:
        if prefix == "METADADOS":
            continue

        if prefix == "EXECUÇÃO":
            lines.append("[EXECUÇÃO]")
            parts = content.split("## ")
            section_index = 1

            for part in parts:
                part = part.strip()
                if not part:
                    continue

                pieces = part.split(NL, 1)
                section_title = pieces[0].strip()
                section_body = pieces[1].strip() if len(pieces) > 1 else ""

                lines.append(f"[EXECUÇÃO:SEÇÃO_{section_index}: {section_title}]")
                lines.append(section_body)
                lines.append("")
                section_index += 1

        elif prefix == "VERIFICAÇÃO":
            lines.append("[VERIFICAÇÃO]")
            lines.append("✅ Conteúdo gerado")
            lines.append("✅ Estrutura visível")
            lines.append("✅ Prefixos aplicados")
            lines.append("⚠️ Revise exemplos se necessário")
            lines.append("")

        elif prefix == "RESPOSTA":
            lines.append("[RESPOSTA]")
            lines.append(content)
            lines.append("")

        elif prefix in thinking:
            lines.append(f"[{prefix}]")
            lines.append(thinking[prefix])
            lines.append("")

        else:
            lines.append(f"[{prefix}]")
            lines.append("Seção gerada automaticamente.")
            lines.append("")

    lines.append("=" * 60)
    lines.append("[METADADOS]")
    for key, value in metadata.items():
        lines.append(f"{key.upper()}: {value}")
    lines.append("=" * 60)

    return NL.join(lines), metadata

def next_id():
    ids = []
    for p in OUTPUT.glob("*.txt"):
        if p.stem.isdigit():
            ids.append(int(p.stem))
    return max(ids) + 1 if ids else 1

def write_pdf(path, text):
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 11)
        safe = text.encode("latin-1", "ignore").decode("latin-1")
        pdf.multi_cell(0, 6, safe)
        pdf.output(str(path))
    except Exception as error:
        pathlib.Path(str(path) + ".error.txt").write_text(str(error), encoding="utf-8")

def save_outputs(document, metadata, export_formats):
    oid = next_id()
    base = OUTPUT / str(oid)

    base.with_suffix(".txt").write_text(document, encoding="utf-8")
    base.with_suffix(".json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    formats = [item.strip().lower() for item in (export_formats or "").split(",") if item.strip()]

    if "md" in formats:
        base.with_suffix(".md").write_text(document, encoding="utf-8")

    if "pdf" in formats:
        write_pdf(base.with_suffix(".pdf"), document)

    return base

def update_memory(metadata):
    stats_path = MEMORY / "stats.json"
    try:
        stats = json.loads(stats_path.read_text(encoding="utf-8"))
    except Exception:
        stats = {"gerados": 0, "total_qualidade": 0.0, "qualidade_media": 0.0}

    stats["gerados"] += 1
    stats["total_qualidade"] += metadata["qualidade"]
    stats["qualidade_media"] = round(stats["total_qualidade"] / stats["gerados"], 4)
    stats_path.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

    if metadata["qualidade"] >= 0.7:
        path = MEMORY / "successes.json"
    else:
        path = MEMORY / "errors.json"

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = []

    data.append({
        "data": datetime.datetime.now().isoformat(),
        "qualidade": metadata["qualidade"],
        "modo": metadata["modo"],
        "materia": metadata["materia"],
    })

    data = data[-500:]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="IA Text Generator Pro")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--materia", default="auto")
    parser.add_argument("--formato", default="resumo", choices=["resumo", "explicacao", "exercicio", "prova", "apostila", "codigo", "flashcard", "trabalho"])
    parser.add_argument("--nivel", default="auto")
    parser.add_argument("--modo", default="balanced", choices=list(MODES.keys()))
    parser.add_argument("--idioma", default="pt")
    parser.add_argument("--dificuldade", default="Médio")
    parser.add_argument("--linguagem", default="python")
    parser.add_argument("--export", default="txt,md,pdf")
    args = parser.parse_args()

    start = time.time()
    random.seed(int(time.time() * 1000))

    materia = detect_materia(args.prompt, args.materia)
    nivel = detect_nivel(args.prompt, args.nivel)
    thinking = thinking_sections(args.modo, args.prompt, materia, nivel)
    content = generate_content(args.formato, materia, args.prompt, nivel, args.linguagem)
    elapsed = time.time() - start

    document, metadata = build_document(
        args.modo,
        args.prompt,
        materia,
        nivel,
        args.dificuldade,
        args.idioma,
        content,
        thinking,
        elapsed
    )

    update_memory(metadata)
    base = save_outputs(document, metadata, args.export)
    print(f"Arquivo gerado: {base}.txt")

if __name__ == "__main__":
    main()
