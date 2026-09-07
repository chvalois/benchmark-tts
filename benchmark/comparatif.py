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


def _lignes_modele(chemin: Path, voix_filtre: set | None = None) -> list[dict]:
    data = json.loads(chemin.read_text(encoding="utf-8"))
    modele = chemin.stem
    out = []
    for voix, r in data.items():
        if voix_filtre is not None and voix not in voix_filtre and voix.split()[0] not in voix_filtre:
            continue
        s = r["synthese"]
        v = r["vitesse"]["global"]
        st = r["stabilite"]
        meta = r["meta"]
        clonage = meta.get("params", {}).get("clonage", True)
        out.append({
            "modele": modele,
            "voix": voix + ("" if clonage else " (voix interne)"),
            "clonage": "oui" if clonage else "non",
            "ttsds2": (s.get("ttsds2") or {}).get("score_global"),
            "nisqa": s.get("nisqa_moyen"),
            "sim": s.get("sim_moyen"),
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
         "Métriques **automatiques** : WER (whisper-large-v3-french), fidélité",
         "language-agnostic, **TTSDS2** (naturalité distributionnelle vs vraie",
         "parole FR, ↑ mieux), **NISQA** (naturalité prédite par énoncé, contre-",
         "vérification, ↑ mieux), **SIM** (similarité au locuteur de réf, ↑ mieux).",
         "**Pas encore d'écoute MOS humaine.** WER brut (aucun plancher humain",
         "soustrait).", "",
         "| modèle | voix | clon. | WER | ±σ | TTSDS2 | NISQA | SIM | hallu. | rép. | tronc. | RTF | CV dur. |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in sorted(lignes, key=lambda d: d["wer"]):
        t2 = f"{x['ttsds2']:.1f}" if x.get("ttsds2") is not None else "—"
        nq = f"{x['nisqa']:.2f}" if x.get("nisqa") is not None else "—"
        sm = f"{x['sim']:.3f}" if x.get("sim") is not None else "—"
        L.append(
            f"| {x['modele']} | {x['voix']} | {x['clonage']} | {_pct(x['wer'])} | "
            f"{_pct(x['wer_sigma'])} | {t2} | {nq} | {sm} | {_pct(x['hallucination'])} | "
            f"{_pct(x['repetition'])} | {_pct(x['troncature'])} | {x['rtf']:.2f} | "
            f"{_pct(x['cv_duree'])} |"
        )
    L.append("")
    L.append("- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).")
    L.append("- **TTSDS2** = score distributionnel (0–100) vs corpus de vraie parole FR "
             "(MLS-French) ; principal pour la naturalité. UTMOS retiré (non calibré FR : "
             "les voix humaines de réf y scoraient 1,5–2,9, sous les TTS).")
    L.append("- **NISQA** ~1–5 (NISQA-TTS, naturalness) — biais anglophone connu, "
             "tenu en contre-vérification seulement.")
    L.append("- **SIM** = cosinus embeddings **ECAPA-TDNN** (`speechbrain/spkrec-ecapa-voxceleb`) "
             "gén. vs voix de réf, silences rognés (0–1).")
    L.append("- **CV durée** = écart-type / moyenne de la durée sur les 3 reps (stabilité).")
    L.append("- Détail par catégorie + WER par piège : `resultats/<modele>.md`.")
    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("json", nargs="+", help="fichiers resultats/<modele>.json")
    p.add_argument("--out", default="resultats/comparatif.md")
    p.add_argument("--voix", default="papa_narration,johnny,ff_siwis",
                   help="voix à inclure (défaut : run principal) ; 'all' = toutes")
    args = p.parse_args()

    vf = None if args.voix == "all" else {v.strip() for v in args.voix.split(",")}
    lignes: list[dict] = []
    for j in args.json:
        lignes.extend(_lignes_modele(Path(j), vf))
    md = markdown(lignes)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(md, encoding="utf-8")
    print(md)
    print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
