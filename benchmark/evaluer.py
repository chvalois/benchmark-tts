#!/usr/bin/env python3
"""Évaluation d'un modèle : croise transcriptions + corpus -> scores.

PUR et sans modèle : la transcription (Whisper) est produite en amont par
`benchmark/transcrire.py`. Ici on combine, par (phrase, répétition), le
WER FR (`mesurer_wer.wer`) et la fidélité language-agnostic
(`fidelite.evaluer_fidelite`), puis on agrège en synthèse modèle.
"""
from __future__ import annotations

from benchmark.corpus import Phrase
from benchmark.fidelite import evaluer_fidelite
from benchmark.mesurer_wer import agreger_wer, wer


def evaluer_runs(
    transcriptions: list[dict], phrases: list[Phrase], *, langue: str = "fr",
    perceptuel: list[dict] | None = None,
) -> list[dict]:
    """`transcriptions` : `[{"id_phrase", "repetition", "texte_transcrit",
    "seg_logprobs"?}, ...]`. Une ligne de sortie par transcription
    rattachée à une phrase connue (les autres sont ignorées).

    `perceptuel` (optionnel) : `[{"id_phrase", "repetition", "utmos",
    "sim"}, ...]` — joint par (id, rep), ajoute `utmos`/`sim` aux lignes.
    """
    par_id = {p.id: p for p in phrases}
    perc = {(x["id_phrase"], x.get("repetition")): x for x in (perceptuel or [])}
    lignes: list[dict] = []
    for t in transcriptions:
        ph = par_id.get(t.get("id_phrase"))
        if ph is None:
            continue
        transcrit = (t.get("texte_transcrit") or "").strip()
        pp = perc.get((t.get("id_phrase"), t.get("repetition")), {})
        w = wer(ph.texte, transcrit, langue)
        f = evaluer_fidelite(
            ph.texte, transcrit, langue=langue, seg_logprobs=t.get("seg_logprobs")
        )
        lignes.append({
            "id_phrase": ph.id,
            "repetition": t.get("repetition"),
            "longueur": ph.longueur,
            "registre": ph.registre,
            "pieges": list(ph.pieges),
            "type": ph.type,
            "wer": w["wer"],
            "wer_substitutions": w["substitutions"],
            "wer_deletions": w["deletions"],
            "wer_insertions": w["insertions"],
            "n_ref": w["n_ref"],
            "fidelite_verifiee": f["verifie"],
            "hallucination": f["hallucination"],
            "repetition_audio": f["repetition"],
            "troncature": f["troncature"],
            "recall": f["recall"],
            "precision": f["precision"],
            "anomalie_kind": f["kind"],
            "anomalie_detail": f["detail"],
            "texte_transcrit": transcrit,
            "utmos": pp.get("utmos"),
            "sim": pp.get("sim"),
        })
    return lignes


def synthese(lignes: list[dict], *, plancher_wer: float = 0.0) -> dict:
    """Agrège les lignes de `evaluer_runs` en synthèse modèle : WER (global
    + par longueur / registre / piège), WER net du plancher humain, taux
    d'anomalies (sur les runs réellement vérifiés) et listes de phrases
    concernées (pour prioriser l'écoute)."""
    if not lignes:
        return {"n_runs": 0, "n_verifiees": 0}

    verifiees = [l for l in lignes if l["fidelite_verifiee"]]
    n_v = len(verifiees) or 1
    utmos = [l["utmos"] for l in lignes if l.get("utmos") is not None]
    sim = [l["sim"] for l in lignes if l.get("sim") is not None]
    agg = agreger_wer([
        {"wer": l["wer"], "longueur": l["longueur"],
         "registre": l["registre"], "pieges": l["pieges"]}
        for l in lignes
    ])

    def _phrases(cle: str) -> list[str]:
        return sorted({l["id_phrase"] for l in verifiees if l[cle]})

    return {
        "n_runs": len(lignes),
        "n_verifiees": len(verifiees),
        "utmos_moyen": (sum(utmos) / len(utmos)) if utmos else None,
        "sim_moyen": (sum(sim) / len(sim)) if sim else None,
        "wer_moyen": agg["global"]["wer_moyen"],
        "wer_ecart_type": agg["global"]["wer_ecart_type"],
        "wer_net_plancher": max(0.0, agg["global"]["wer_moyen"] - plancher_wer),
        "wer_par_longueur": agg["par_longueur"],
        "wer_par_registre": agg["par_registre"],
        "wer_par_piege": agg["par_piege"],
        "taux_hallucination": sum(1 for l in verifiees if l["hallucination"]) / n_v,
        "taux_repetition": sum(1 for l in verifiees if l["repetition_audio"]) / n_v,
        "taux_troncature": sum(1 for l in verifiees if l["troncature"]) / n_v,
        "phrases_hallucination": _phrases("hallucination"),
        "phrases_repetition": _phrases("repetition_audio"),
        "phrases_troncature": _phrases("troncature"),
    }
