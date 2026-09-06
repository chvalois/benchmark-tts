#!/usr/bin/env python3
"""Tableau comparatif inter-modèles à partir des `resultats/<modele>.json`
produits par `rapport.py`.

    python3 benchmark/comparatif.py resultats/chatterbox_v3.json resultats/kokoro_82m.json \
        --out resultats/comparatif.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _pct(x) -> str:
    return f"{x * 100:.1f}%" if isinstance(x, (int, float)) else str(x)


def _lignes_modele(chemin: Path) -> list[dict]:
    data = json.loads(chemin.read_text(encoding="utf-8"))
    modele = chemin.stem
    out = []
    for voix, r in data.items():
        s = r["synthese"]
        v = r["vitesse"]["global"]
        st = r["stabilite"]
        meta = r["meta"]
        clonage = meta.get("params", {}).get("clonage", True)
        out.append({
            "modele": modele,
            "voix": voix + ("" if clonage else " (voix interne)"),
            "clonage": "oui" if clonage else "non",
            "wer": s["wer_moyen"],
            "wer_sigma": s["wer_ecart_type"],
            "hallucination": s["taux_hallucination"],
            "repetition": s["taux_repetition"],
            "troncature": s["taux_troncature"],
            "rtf": v["rtf"]["moyenne"],
            "cv_duree": st["cv_median"],
            "wer_narration": s["wer_par_registre"].get("narration", {}).get("wer_moyen", 0.0),
            "wer_onomatopee": s["wer_par_piege"].get("onomatopee", {}).get("wer_moyen", 0.0),
        })
    return out


def markdown(lignes: list[dict]) -> str:
    L = ["# Comparatif TTS open source — français", "",
         "Métriques automatiques uniquement (WER via whisper-large-v3-french,",
         "détecteurs de fidélité language-agnostic). **Pas encore d'écoute MOS.**",
         "WER brut (aucun plancher humain soustrait).", "",
         "| modèle | voix | clonage | WER | ±σ | hallu. | rép. | tronc. | RTF | CV durée | WER narration | WER onomatopée |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in sorted(lignes, key=lambda d: d["wer"]):
        L.append(
            f"| {x['modele']} | {x['voix']} | {x['clonage']} | {_pct(x['wer'])} | "
            f"{_pct(x['wer_sigma'])} | {_pct(x['hallucination'])} | {_pct(x['repetition'])} | "
            f"{_pct(x['troncature'])} | {x['rtf']:.2f} | {_pct(x['cv_duree'])} | "
            f"{_pct(x['wer_narration'])} | {_pct(x['wer_onomatopee'])} |"
        )
    L.append("")
    L.append("- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).")
    L.append("- **CV durée** = écart-type / moyenne de la durée sur les 3 reps du même texte (stabilité).")
    L.append("- Détail par catégorie : `resultats/<modele>.md`.")
    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("json", nargs="+", help="fichiers resultats/<modele>.json")
    p.add_argument("--out", default="resultats/comparatif.md")
    args = p.parse_args()

    lignes: list[dict] = []
    for j in args.json:
        lignes.extend(_lignes_modele(Path(j)))
    md = markdown(lignes)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(md, encoding="utf-8")
    print(md)
    print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
