#!/usr/bin/env python3
"""Naturalité — **contre-vérification** secondaire : NISQA-TTS
(Mittag & Möller, TU-Berlin).

Prédicteur de *Naturalness* par énoncé pour la parole synthétique
(sans référence), scalaire ~1–5. Tenu en second rideau derrière TTSDS2
(`mesurer_ttsds2.py`, principal) : il partage avec UTMOS le biais
anglophone, mais avec un entraînement TTS explicite et une échelle
« naturalité » dédiée, il sert de garde-fou sur le classement.

- Poids `nisqa_tts.tar` : dépôt `gabrielmittag/NISQA` (hors PyPI),
  licence **CC BY-NC-SA 4.0** → usage recherche non commercial (instrument
  de mesure du benchmark, pas un composant produit). Défaut :
  `$TTSB_ROOT/nisqa-weights/weights/nisqa_tts.tar`.
- Sortie : `<audio-dir>/nisqa.csv` (`id_phrase,repetition,nisqa`), à côté
  de `perceptuel.csv`. `rapport.py` la joint par `(id, rep)`.

Modèle-dépendant (`nisqa` épingle torch 2.2 / numpy 1.26) → venv **dédié**
`$TTSB_VENVS/_nisqa`. Seuls les helpers d'I/O sont purs/testés.

    source env.sh
    uv run --python "$TTSB_VENVS/_nisqa/bin/python" benchmark/mesurer_nisqa.py \
        --audio-dir "$TTSB_AUDIO_OUT/firered_tts3/papa_narration"
"""
from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path

from benchmark.mesurer_perceptuel import _lister_wavs

RACINE = Path(__file__).resolve().parent.parent
COLONNES_NISQA = ("id_phrase", "repetition", "nisqa")
# Colonnes candidates pour la prédiction de naturalité dans le df NISQA.
_COLS_PRED = ("mos_pred", "nat_pred", "naturalness_pred", "NAT_pred")


def _poids_defaut() -> Path:
    racine = os.environ.get("TTSB_ROOT", str(RACINE))
    return Path(racine) / "nisqa-weights" / "weights" / "nisqa_tts.tar"


def _num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def ecrire_nisqa(chemin: Path | str, lignes: list[dict]) -> None:
    p = Path(chemin)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES_NISQA)
        w.writeheader()
        w.writerows(lignes)


def lire_nisqa(chemin: Path | str) -> list[dict]:
    """Relit `nisqa.csv`. `nisqa` absent / vide / `nan` -> `None`
    (traité comme « pas de mesure » en aval, jamais propagé aux moyennes)."""
    with open(chemin, newline="", encoding="utf-8") as f:
        out = []
        for row in csv.DictReader(f):
            out.append({
                "id_phrase": row["id_phrase"],
                "repetition": int(row["repetition"]) if row.get("repetition") else None,
                "nisqa": _num(row.get("nisqa")),
            })
        return out


def _colonne_pred(df) -> str:
    for c in _COLS_PRED:
        if c in df.columns:
            return c
    preds = [c for c in df.columns if str(c).endswith("_pred")]
    if not preds:
        raise SystemExit(f"[FAIL] aucune colonne de prédiction dans NISQA df : {list(df.columns)}")
    return preds[0]


def nisqa_dossier(audio_dir: Path | str, poids: Path | str) -> list[dict]:
    """NISQA-TTS sur chaque `<id>_<rep>.wav` de `audio_dir`."""
    from nisqa.NISQA_model import nisqaModel

    audio_dir, poids = Path(audio_dir), Path(poids)
    wavs = _lister_wavs(audio_dir)
    if not wavs:
        raise SystemExit(f"[FAIL] aucun <id>_<rep>.wav dans {audio_dir}")
    if not poids.is_file():
        raise SystemExit(f"[FAIL] poids NISQA introuvables : {poids} "
                         f"(cloner gabrielmittag/NISQA -> weights/nisqa_tts.tar)")

    # Mêmes clés que run_predict.py : le reste (ms_*, td_*, model, dim,
    # tr_parallel…) vient du checkpoint via `checkpoint['args'].update(args)`.
    args = {
        "mode": "predict_dir",
        "pretrained_model": str(poids),
        "deg": None,
        "data_dir": str(audio_dir),
        "output_dir": "",          # pas de NISQA_results.csv : on récupère le df
        "csv_file": None, "csv_deg": None,
        "num_workers": 0, "bs": 10,
        "tr_bs_val": 10, "tr_num_workers": 0,
        "ms_channel": None,
    }
    df = nisqaModel(args).predict()
    col = _colonne_pred(df)

    par_fichier = {Path(str(d)).name: v for d, v in zip(df["deg"], df[col])}
    lignes: list[dict] = []
    for pid, rep, chemin in wavs:
        val = par_fichier.get(chemin.name)
        n = _num(val)
        lignes.append({
            "id_phrase": pid, "repetition": rep,
            "nisqa": round(n, 3) if n is not None else "",
        })
    manquants = sum(1 for x in lignes if x["nisqa"] == "")
    if manquants:
        print(f"[nisqa] {manquants}/{len(lignes)} fichiers sans score", flush=True)
    return lignes


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--audio-dir", required=True)
    p.add_argument("--weights", default="", help=f"défaut : {_poids_defaut()}")
    p.add_argument("--out", default="", help="défaut : <audio-dir>/nisqa.csv")
    args = p.parse_args()

    audio_dir = Path(args.audio_dir)
    poids = Path(args.weights) if args.weights else _poids_defaut()
    out = Path(args.out) if args.out else audio_dir / "nisqa.csv"

    lignes = nisqa_dossier(audio_dir, poids)
    ecrire_nisqa(out, lignes)
    ok = [x["nisqa"] for x in lignes if x["nisqa"] != ""]
    moy = f"{sum(ok) / len(ok):.2f}" if ok else "—"
    print(f"[nisqa] {len(lignes)} lignes (moy {moy}) -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
