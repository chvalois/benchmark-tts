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

Tolérance phonétique des noms propres (§3.9bis, 2026-09-13) : un nom
propre (réel ou inventé) mal orthographié par l'ASR mais phonétiquement
proche de la référence (« Grzegorz » -> « Gregor », « Franfrelou » ->
« Franc-Frelou ») n'est pas un défaut du modèle TTS — c'est une ambiguïté
de graphie qu'un humain ne lève pas non plus à l'oreille seule. Quand
`wer()` reçoit `noms_propres` (liste des tokens annotés dans
`corpus/phrases.yaml`), les blocs de substitution/suppression/insertion
qui ne portent QUE sur ces tokens sont reclassés en « hit » si leur
similarité phonétique (`fidelite.similarite_phonetique`, espeak-ng) passe
`_SEUIL_SIMILARITE_NOM_PROPRE`. Le WER brut (sans tolérance) reste
disponible sous `wer_brut` — la tolérance ne doit jamais être invisible.
"""
from __future__ import annotations

import statistics
from collections import defaultdict

from benchmark.normalisation import normaliser_mots, normaliser_texte

_SEUIL_SIMILARITE_NOM_PROPRE = 0.75  # même seuil que le sauvetage suffixe de fidelite.py


def _fusionner_blocs_erreur(alignment) -> list[dict]:
    """Fusionne les chunks jiwer non-'equal' consécutifs en blocs d'erreur.

    jiwer peut scinder un remplacement multi-mots en plusieurs chunks
    adjacents (ex. « franfrelou » -> « franc frelou » = insert + substitute
    contigus) : on les traite comme UN seul bloc pour la comparaison
    phonétique, sinon la fenêtre serait tronquée.
    """
    blocs: list[dict] = []
    courant: dict | None = None
    for chunk in alignment:
        if chunk.type == "equal":
            if courant:
                blocs.append(courant)
                courant = None
            continue
        if courant is None:
            courant = {
                "ref_start": chunk.ref_start_idx, "ref_end": chunk.ref_end_idx,
                "hyp_start": chunk.hyp_start_idx, "hyp_end": chunk.hyp_end_idx,
                "substitutions": 0, "deletions": 0, "insertions": 0,
            }
        else:
            courant["ref_end"] = chunk.ref_end_idx
            courant["hyp_end"] = chunk.hyp_end_idx
        n_ref = chunk.ref_end_idx - chunk.ref_start_idx
        n_hyp = chunk.hyp_end_idx - chunk.hyp_start_idx
        if chunk.type == "substitute":
            courant["substitutions"] += n_ref
        elif chunk.type == "delete":
            courant["deletions"] += n_ref
        elif chunk.type == "insert":
            courant["insertions"] += n_hyp
    if courant:
        blocs.append(courant)
    return blocs


def _rescaper_noms_propres(
    alignment, ref_mots: list[str], hyp_mots: list[str],
    noms_propres_norm: set[str], langue: str,
) -> dict:
    """Reclasse en « hit » les blocs d'erreur ne portant QUE sur des tokens
    de `noms_propres_norm`, si leur similarité phonétique dépasse le seuil.

    Retourne les décomptes à SOUSTRAIRE de substitutions/deletions/insertions
    (et le nombre de mots rescapés, pour transparence)."""
    from benchmark.fidelite import similarite_phonetique  # évite tout cycle d'import au chargement

    delta = {"substitutions": 0, "deletions": 0, "insertions": 0, "rescapes": 0}
    for bloc in _fusionner_blocs_erreur(alignment):
        ref_span = ref_mots[bloc["ref_start"]:bloc["ref_end"]]
        if not ref_span or not all(m in noms_propres_norm for m in ref_span):
            continue
        hyp_span = hyp_mots[bloc["hyp_start"]:bloc["hyp_end"]]
        if not hyp_span:
            continue  # suppression pure : rien à comparer phonétiquement
        sim = similarite_phonetique(" ".join(ref_span), " ".join(hyp_span), langue)
        if sim is not None and sim >= _SEUIL_SIMILARITE_NOM_PROPRE:
            delta["substitutions"] += bloc["substitutions"]
            delta["deletions"] += bloc["deletions"]
            delta["insertions"] += bloc["insertions"]
            delta["rescapes"] += len(ref_span)
    return delta


def wer(
    reference: str, hypothese: str, langue: str = "fr",
    noms_propres: list[str] | None = None,
) -> dict:
    """WER + décompte hits / substitutions / suppressions / insertions.

    Les deux chaînes sont normalisées à l'identique avant comparaison.
    `noms_propres` (optionnel) active la tolérance phonétique (cf. docstring
    de module) ; `wer_brut` conserve toujours la valeur sans tolérance.
    """
    ref = normaliser_texte(reference, langue)
    hyp = normaliser_texte(hypothese, langue)
    n_ref = len(ref.split())

    if not ref:
        n_ins = len(hyp.split())
        return {
            "wer": 0.0 if not hyp else 1.0, "wer_brut": 0.0 if not hyp else 1.0,
            "hits": 0, "substitutions": 0, "deletions": 0, "insertions": n_ins,
            "n_ref": 0, "noms_propres_rescapes": 0,
        }

    import jiwer  # import tardif : dépendance du module commun, pas de la lib appelante

    out = jiwer.process_words(ref, hyp)
    substitutions, deletions, insertions = int(out.substitutions), int(out.deletions), int(out.insertions)
    wer_brut = float(out.wer)

    rescapes = 0
    noms_propres_norm = {m for n in (noms_propres or []) for m in normaliser_mots(n, langue)}
    if noms_propres_norm:
        delta = _rescaper_noms_propres(
            out.alignments[0], ref.split(), hyp.split(), noms_propres_norm, langue
        )
        substitutions -= delta["substitutions"]
        deletions -= delta["deletions"]
        insertions -= delta["insertions"]
        rescapes = delta["rescapes"]

    return {
        "wer": (substitutions + deletions + insertions) / n_ref,
        "wer_brut": wer_brut,
        "hits": n_ref - substitutions - deletions,
        "substitutions": substitutions,
        "deletions": deletions,
        "insertions": insertions,
        "n_ref": n_ref,
        "noms_propres_rescapes": rescapes,
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
