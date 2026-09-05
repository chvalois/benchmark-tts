#!/usr/bin/env python3
"""Stabilité — variance sur les N répétitions d'un même item.

APIAVISOL §3.6 / §4.3 / §9 : un modèle « instable en longueur » sort deux
durées très différentes pour le même texte et le même seed varié. On
mesure l'écart-type de la durée audio par `id_phrase`, normalisé en
coefficient de variation (CV = σ / µ) pour comparer entre items de
longueurs différentes.

Pur : consomme les lignes déjà chargées par `mesurer_vitesse.charger_timings`.
"""
from __future__ import annotations

import statistics
from collections import defaultdict

# Au-delà : la durée d'un même texte varie trop d'un run à l'autre.
CV_DUREE_SUSPECT = 0.15


def stabilite_duree(lignes: list[dict], *, cv_seuil: float = CV_DUREE_SUSPECT) -> dict:
    """Retour :
    ```
    {
      "par_phrase": {"p07": {"moyenne_s": .., "ecart_type_s": ..,
                             "cv": .., "n": .., "suspect": bool}, ...},
      "n_suspects": int,
      "cv_median": float,
    }
    ```
    Les items avec moins de 2 runs sont ignorés (variance indéfinie).
    """
    par_phrase: dict[str, list[float]] = defaultdict(list)
    for x in lignes:
        d = x.get("audio_s")
        if d:
            par_phrase[x.get("id_phrase", "?")].append(float(d))

    resultat: dict[str, dict] = {}
    cvs: list[float] = []
    for pid, durees in sorted(par_phrase.items()):
        if len(durees) < 2:
            continue
        moy = statistics.fmean(durees)
        ect = statistics.pstdev(durees)
        cv = ect / moy if moy else 0.0
        cvs.append(cv)
        resultat[pid] = {
            "moyenne_s": moy,
            "ecart_type_s": ect,
            "cv": cv,
            "n": len(durees),
            "suspect": cv > cv_seuil,
        }

    return {
        "par_phrase": resultat,
        "n_suspects": sum(1 for v in resultat.values() if v["suspect"]),
        "cv_median": statistics.median(cvs) if cvs else 0.0,
    }
