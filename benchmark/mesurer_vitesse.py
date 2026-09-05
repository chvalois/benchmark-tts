#!/usr/bin/env python3
"""Vitesse — lecture des `timings.csv` produits par les adaptateurs.

Aucune mesure ici : les scripts `models/<nom>/generer.py` écrivent les
timings (contrat, cf. benchmark/CONTRAT_MODELE.md). Ce module agrège.

- TTFA : temps au premier échantillon audio.
- RTF  : `gen_s / audio_s` (APIAVISOL §4.3) — < 1 = plus rapide que le temps réel.
- RTFx : `audio_s / gen_s` (REFLEXIONCLAUDE) — « x fois le temps réel ».
- Cold start : NON inclus dans `gen_s` (mesuré et reporté à part, cf. contrat).
"""
from __future__ import annotations

import csv
import statistics
from pathlib import Path

CHAMPS_FLOAT = ("ttfa_s", "gen_s", "audio_s")
CHAMPS_INT = ("repetition", "seed", "vram_pic_mo")


def _caster(row: dict) -> dict:
    for c in CHAMPS_FLOAT:
        if row.get(c) not in ("", None):
            row[c] = float(row[c])
    for c in CHAMPS_INT:
        if row.get(c) not in ("", None):
            row[c] = int(float(row[c]))
    return row


def charger_timings(chemin: Path | str) -> list[dict]:
    """Lit un `timings.csv`, caste les champs numériques, ignore les
    lignes dont le `statut` n'est pas `ok`."""
    with open(chemin, newline="", encoding="utf-8") as f:
        return [
            _caster(row)
            for row in csv.DictReader(f)
            if (row.get("statut") or "ok").strip() == "ok"
        ]


def _stats(valeurs: list[float]) -> dict:
    valeurs = [v for v in valeurs if v is not None]
    if not valeurs:
        return {"moyenne": 0.0, "ecart_type": 0.0, "min": 0.0, "max": 0.0, "n": 0}
    return {
        "moyenne": statistics.fmean(valeurs),
        "ecart_type": statistics.pstdev(valeurs) if len(valeurs) > 1 else 0.0,
        "min": min(valeurs),
        "max": max(valeurs),
        "n": len(valeurs),
    }


def _rtf(ligne: dict) -> float | None:
    a, g = ligne.get("audio_s"), ligne.get("gen_s")
    if not a or not g:
        return None
    return g / a


def agreger_vitesse(lignes: list[dict]) -> dict:
    """Vue globale + par `categorie_chunk`."""
    def _bloc(sous: list[dict]) -> dict:
        rtf = [r for r in (_rtf(x) for x in sous) if r is not None]
        return {
            "ttfa_s": _stats([x.get("ttfa_s") for x in sous]),
            "rtf": _stats(rtf),
            "rtfx": _stats([1.0 / r for r in rtf if r]),
            "audio_s_total": sum(x.get("audio_s") or 0.0 for x in sous),
            "n_runs": len(sous),
        }

    par_categorie: dict[str, list[dict]] = {}
    for x in lignes:
        par_categorie.setdefault(x.get("categorie_chunk") or "inconnu", []).append(x)

    return {
        "global": _bloc(lignes),
        "par_categorie": {k: _bloc(v) for k, v in sorted(par_categorie.items())},
    }
