#!/usr/bin/env python3
"""WER français — calcul (jiwer) + agrégation par catégorie de corpus.

Le calcul (`wer`) est PUR : il prend deux chaînes et renvoie un dict. La
transcription elle-même (Whisper large-v3-french) est produite par un
runner ASR séparé (Phase 3), jamais ici — `benchmark/` ne charge aucun
modèle.

Référence commune ref/hypothèse : `normalisation.normaliser_texte` (même
convention des deux côtés, sinon le WER mesure la normalisation).

Plancher d'erreur : le WER d'une **vraie voix humaine** transcrite par le
même ASR n'est pas nul (erreurs propres à Whisper). `plancher_wer()`
calcule ce plancher à partir des enregistrements humains de
`corpus/voix_reference/` ; les WER modèles se lisent **au-dessus** de ce
plancher, jamais dans l'absolu (APIAVISOL §3.3, §9).
"""
from __future__ import annotations

import statistics
from collections import defaultdict

from benchmark.normalisation import normaliser_texte


def wer(reference: str, hypothese: str, langue: str = "fr") -> dict:
    """WER + décompte hits / substitutions / suppressions / insertions.

    Les deux chaînes sont normalisées à l'identique avant comparaison.
    """
    ref = normaliser_texte(reference, langue)
    hyp = normaliser_texte(hypothese, langue)
    n_ref = len(ref.split())

    if not ref:
        n_ins = len(hyp.split())
        return {
            "wer": 0.0 if not hyp else 1.0, "hits": 0, "substitutions": 0,
            "deletions": 0, "insertions": n_ins, "n_ref": 0,
        }

    import jiwer  # import tardif : dépendance du module commun, pas de la lib appelante

    out = jiwer.process_words(ref, hyp)
    return {
        "wer": float(out.wer),
        "hits": int(out.hits),
        "substitutions": int(out.substitutions),
        "deletions": int(out.deletions),
        "insertions": int(out.insertions),
        "n_ref": n_ref,
    }


def _moyenne_ecart_type(valeurs: list[float]) -> tuple[float, float]:
    if not valeurs:
        return 0.0, 0.0
    moy = statistics.fmean(valeurs)
    ect = statistics.pstdev(valeurs) if len(valeurs) > 1 else 0.0
    return moy, ect


def agreger_wer(mesures: list[dict]) -> dict:
    """Agrège une liste de mesures en vues globale + par catégorie.

    Chaque mesure : `{"wer": float, "longueur": str, "registre": str,
    "pieges": list[str], ...}` (typiquement une (phrase, répétition)).

    Retour :
    ```
    {
      "global": {"wer_moyen": .., "wer_ecart_type": .., "n": ..},
      "par_longueur": {"court": {...}, ...},
      "par_registre": {...},
      "par_piege":    {...},   # une phrase à K pièges compte dans K groupes
    }
    ```
    """
    def _bloc(sous: list[dict]) -> dict:
        moy, ect = _moyenne_ecart_type([m["wer"] for m in sous])
        return {"wer_moyen": moy, "wer_ecart_type": ect, "n": len(sous)}

    par_longueur: dict[str, list[dict]] = defaultdict(list)
    par_registre: dict[str, list[dict]] = defaultdict(list)
    par_piege: dict[str, list[dict]] = defaultdict(list)
    for m in mesures:
        par_longueur[m["longueur"]].append(m)
        par_registre[m["registre"]].append(m)
        for p in m.get("pieges") or []:
            par_piege[p].append(m)

    return {
        "global": _bloc(mesures),
        "par_longueur": {k: _bloc(v) for k, v in sorted(par_longueur.items())},
        "par_registre": {k: _bloc(v) for k, v in sorted(par_registre.items())},
        "par_piege": {k: _bloc(v) for k, v in sorted(par_piege.items())},
    }


def plancher_wer(mesures_humaines: list[dict]) -> float:
    """Plancher = WER moyen d'enregistrements HUMAINS transcrits par le
    même ASR. Aucune valeur inventée : renvoie 0.0 si rien fourni."""
    moy, _ = _moyenne_ecart_type([m["wer"] for m in mesures_humaines])
    return moy
