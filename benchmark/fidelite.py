#!/usr/bin/env python3
"""Fidélité au contenu — porté de avisol-api/runpod/transcription_check.py.

Compare le texte attendu à la transcription ASR et produit des signaux
*language-agnostic* (alignement de mots seul, aucune liste de mots-clés) :
recall, precision, ratio de longueur, troncature de fin, hallucination,
répétition. Deux sauvetages anti-faux-positifs FR : orthographique
(Levenshtein sur le suffixe manquant) puis phonétique (espeak-ng via
`phonemizer`, dégradation silencieuse si absent).

Toutes les fonctions de calcul sont PURES et sans modèle : la
transcription elle-même (Whisper) est produite ailleurs (runner ASR).

Historique des faux positifs FR que les sauvetages neutralisent (contexte
avisol) :
- suffixe : « Franfrelou » transcrit « Franc-Frelou » (sur-découpage sur
  le trait d'union) -> sauvetage orthographique ;
- pleine phrase : « S'écria Flo » transcrit « Ses cris à flots » (son
  quasi identique, segmentation en mots totalement différente, recall
  proche de 0) -> sauvetage phonétique.
"""
from __future__ import annotations

import logging
from difflib import SequenceMatcher

from benchmark.normalisation import normaliser_mots

# --- Seuils (les constantes SONT la configuration) ----------------------
SEUIL_RECALL_HALLUCINATION = 0.6     # sous ce recall : le modèle raconte autre chose
RATIO_LONGUEUR_EXTRA = 1.5           # transcription nettement plus longue = digression ajoutée
PRECISION_MAX_EXTRA = 0.5
MOTS_MIN_VERIFIABLE = 4              # < 4 mots attendus : bruit ASR disproportionné -> non vérifié
TRONCATURE_MIN_MOTS = 1             # suffixe de N mots consécutifs absents = troncature

TAIL_WORDS = 6                      # fenêtre de `tail_recall` (informatif, jamais un verdict)
TAIL_RECALL_SEUIL = 0.5

_SUFFIXE_MAX_MOTS = 2               # mots de suffixe réexaminés par les sauvetages
_SUFFIXE_FENETRE_MAX = 3           # mots transcrits joints par fenêtre candidate
_SUFFIXE_MIN_CARS = 3
_SUFFIXE_SIMILARITE_MIN = 0.75     # seuil sauvetage suffixe (ortho ET phonétique)
_PHRASE_PHONETIQUE_SIMILARITE_MIN = 0.85  # seuil sauvetage phonétique pleine phrase

REPEAT_RUN_MIN = 3                 # token répété N fois d'affilée
REPEAT_NGRAM_REPS = 2             # n-gramme répété N fois consécutives
REPEAT_RATIO_MAX = 0.45          # part max de trigrammes dupliqués
LOGPROB_MIN = -1.0              # confiance minimale d'un segment ASR

_ISO_VERS_ESPEAK = {"fr": "fr-fr", "en": "en-us", "zh": "cmn", "pt": "pt-br"}


# --- Distance d'édition ------------------------------------------------
def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            cout = 0 if ca == cb else 1
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cout)
        prev = cur
    return prev[-1]


def similarite_chaine(a: str, b: str) -> float:
    """1.0 = identiques, 0.0 = rien en commun (distance normalisée par la
    plus longue des deux chaînes)."""
    if not a and not b:
        return 1.0
    return 1.0 - _levenshtein(a, b) / max(len(a), len(b))


# --- Sauvetage orthographique du suffixe manquant --------------------
def _sauvetage_suffixe_ortho(suffixe_manquant: list[str], mots_transcrits: list[str]) -> list[str]:
    for n in range(min(_SUFFIXE_MAX_MOTS, len(suffixe_manquant)), 0, -1):
        attendu = "".join(suffixe_manquant[-n:])
        if len(attendu) < _SUFFIXE_MIN_CARS:
            continue
        meilleur = 0.0
        for w in range(1, _SUFFIXE_FENETRE_MAX + 1):
            if w > len(mots_transcrits):
                break
            meilleur = max(meilleur, similarite_chaine(attendu, "".join(mots_transcrits[-w:])))
        if meilleur >= _SUFFIXE_SIMILARITE_MIN:
            return suffixe_manquant[:-n]
    return suffixe_manquant


# --- Sauvetage phonétique (espeak-ng via phonemizer) ----------------
_backend_phonemizer_ok: bool | None = None  # None = jamais testé

_LOGGER_PHONEMIZER = logging.getLogger("benchmark.fidelite.phonemizer")
_LOGGER_PHONEMIZER.addHandler(logging.NullHandler())
_LOGGER_PHONEMIZER.setLevel(logging.ERROR)
_LOGGER_PHONEMIZER.propagate = False


def _espeak_lang(langue: str) -> str:
    iso = (langue or "fr").strip().lower()[:2]
    return _ISO_VERS_ESPEAK.get(iso, iso)


def _phonemiser(texte: str, espeak_lang: str) -> str | None:
    """Phonémise `texte`. None si le backend est indisponible ou échoue —
    ne lève JAMAIS (un sauvetage optionnel ne doit pas casser l'évaluation)."""
    global _backend_phonemizer_ok
    if _backend_phonemizer_ok is False or not texte.strip():
        return None
    try:
        from phonemizer import phonemize
        from phonemizer.separator import Separator

        res = phonemize(
            texte, language=espeak_lang, backend="espeak",
            separator=Separator(phone="", word=""), strip=True,
            with_stress=False, njobs=1, logger=_LOGGER_PHONEMIZER,
        )
        _backend_phonemizer_ok = True
        return res
    except Exception as e:  # phonemizer/espeak-ng absent, langue non gérée, etc.
        if _backend_phonemizer_ok is None:
            print(f"[fidelite] sauvetage phonétique désactivé : {type(e).__name__}: {e}", flush=True)
        _backend_phonemizer_ok = False
        return None


def similarite_phonetique(attendu: str, transcrit: str, langue: str = "fr") -> float | None:
    """1.0 = phonétiquement identiques ; None si le backend est absent."""
    lang = _espeak_lang(langue)
    p1 = _phonemiser(attendu, lang)
    p2 = _phonemiser(transcrit, lang)
    if p1 is None or p2 is None:
        return None
    return similarite_chaine(p1, p2)


def _sauvetage_suffixe_phonetique(
    suffixe_manquant: list[str], mots_transcrits: list[str], langue: str
) -> list[str]:
    lang = _espeak_lang(langue)
    for n in range(min(_SUFFIXE_MAX_MOTS, len(suffixe_manquant)), 0, -1):
        attendu = " ".join(suffixe_manquant[-n:])
        if len(attendu.replace(" ", "")) < _SUFFIXE_MIN_CARS:
            continue
        p_attendu = _phonemiser(attendu, lang)
        if p_attendu is None:
            return suffixe_manquant  # backend absent : rien à tenter
        meilleur = 0.0
        for w in range(1, _SUFFIXE_FENETRE_MAX + 1):
            if w > len(mots_transcrits):
                break
            p_cand = _phonemiser(" ".join(mots_transcrits[-w:]), lang)
            if p_cand is not None:
                meilleur = max(meilleur, similarite_chaine(p_attendu, p_cand))
        if meilleur >= _SUFFIXE_SIMILARITE_MIN:
            return suffixe_manquant[:-n]
    return suffixe_manquant


# --- Comparaison texte attendu / transcription ----------------------
def comparer(texte_attendu: str, texte_transcrit: str, langue: str = "fr") -> dict:
    """Aligne les mots (difflib, sous-séquences) et calcule recall /
    precision / length_ratio / tail_recall / missing_words /
    trailing_missing_words (ce dernier APRÈS sauvetage orthographique puis
    phonétique). Fonction d'INFO pure — aucun verdict."""
    attendus = normaliser_mots(texte_attendu, langue)
    transcrits = normaliser_mots(texte_transcrit, langue)

    if not attendus:
        return {
            "expected_words": [], "transcribed_words": transcrits,
            "missing_words": [], "recall": 1.0, "precision": 1.0,
            "length_ratio": 0.0, "tail_recall": 1.0, "likely_truncated": False,
            "trailing_missing_words": [],
        }

    matcher = SequenceMatcher(None, attendus, transcrits, autojunk=False)
    idx_attendus_ok: set[int] = set()
    idx_transcrits_ok: set[int] = set()
    for bloc in matcher.get_matching_blocks():
        idx_attendus_ok.update(range(bloc.a, bloc.a + bloc.size))
        idx_transcrits_ok.update(range(bloc.b, bloc.b + bloc.size))

    missing = [w for i, w in enumerate(attendus) if i not in idx_attendus_ok]
    recall = len(idx_attendus_ok) / len(attendus)
    precision = len(idx_transcrits_ok) / len(transcrits) if transcrits else 1.0
    length_ratio = len(transcrits) / len(attendus)

    debut_tail = max(0, len(attendus) - TAIL_WORDS)
    tail = range(debut_tail, len(attendus))
    tail_recall = sum(1 for i in tail if i in idx_attendus_ok) / len(tail) if tail else 1.0

    suffixe: list[str] = []
    for i in range(len(attendus) - 1, -1, -1):
        if i in idx_attendus_ok:
            break
        suffixe.append(attendus[i])
    suffixe.reverse()
    suffixe = _sauvetage_suffixe_ortho(suffixe, transcrits)
    if suffixe:
        suffixe = _sauvetage_suffixe_phonetique(suffixe, transcrits, langue)

    return {
        "expected_words": attendus,
        "transcribed_words": transcrits,
        "missing_words": missing,
        "recall": recall,
        "precision": precision,
        "length_ratio": length_ratio,
        "tail_recall": tail_recall,
        "likely_truncated": tail_recall < TAIL_RECALL_SEUIL,
        "trailing_missing_words": suffixe,
    }


# --- Détecteurs (verdicts) ----------------------------------------
def detecter_hallucination(
    recall: float, *, precision: float | None = None, length_ratio: float | None = None,
    seuil_recall: float = SEUIL_RECALL_HALLUCINATION,
) -> dict:
    if recall < seuil_recall:
        return {"hallucination": True, "kind": "recall", "detail": f"recall={recall:.0%}"}
    if (
        precision is not None and length_ratio is not None
        and length_ratio >= RATIO_LONGUEUR_EXTRA and precision < PRECISION_MAX_EXTRA
    ):
        return {
            "hallucination": True, "kind": "extra",
            "detail": f"transcription {length_ratio:.1f}x plus longue, precision={precision:.0%}",
        }
    return {"hallucination": False, "kind": "", "detail": ""}


def detecter_troncature(suffixe_manquant: list[str], *, min_mots: int = TRONCATURE_MIN_MOTS) -> dict:
    if len(suffixe_manquant) >= min_mots:
        return {
            "troncature": True, "kind": "tail",
            "detail": f"mot(s) de fin non détecté(s) : « {' '.join(suffixe_manquant)} »",
        }
    return {"troncature": False, "kind": "", "detail": ""}


def _run_consecutif(tokens: list[str], run_min: int) -> str | None:
    run = 1
    for i in range(1, len(tokens)):
        if tokens[i] == tokens[i - 1]:
            run += 1
            if run >= run_min:
                return tokens[i]
        else:
            run = 1
    return None


def _ngram_consecutif(tokens: list[str], reps: int) -> str | None:
    for n in (3, 2):
        i = 0
        while i + n * reps <= len(tokens):
            bloc = tokens[i:i + n]
            if all(tokens[i + k * n:i + (k + 1) * n] == bloc for k in range(1, reps)):
                return " ".join(bloc)
            i += 1
    return None


def _ratio_trigrammes_dupliques(tokens: list[str]) -> float:
    if len(tokens) < 6:
        return 0.0
    grams = [tuple(tokens[i:i + 3]) for i in range(len(tokens) - 2)]
    vus: set = set()
    dup = 0
    for g in grams:
        if g in vus:
            dup += 1
        else:
            vus.add(g)
    return dup / len(grams)


def detecter_repetitions(tokens: list[str], seg_logprobs: list[float] | None = None) -> dict:
    tok = _run_consecutif(tokens, REPEAT_RUN_MIN)
    if tok is not None:
        return {"repetition": True, "kind": "run", "detail": f"« {tok} » x{REPEAT_RUN_MIN}+"}
    ng = _ngram_consecutif(tokens, REPEAT_NGRAM_REPS)
    if ng is not None:
        return {"repetition": True, "kind": "ngram", "detail": f"« {ng} » x{REPEAT_NGRAM_REPS}+"}
    ratio = _ratio_trigrammes_dupliques(tokens)
    if ratio > REPEAT_RATIO_MAX:
        return {"repetition": True, "kind": "ratio", "detail": f"trigrammes dupliqués {ratio:.0%}"}
    if seg_logprobs and min(seg_logprobs) < LOGPROB_MIN:
        return {"repetition": True, "kind": "lowprob", "detail": f"avg_logprob {min(seg_logprobs):.2f}"}
    return {"repetition": False, "kind": "", "detail": ""}


# --- Orchestration sans modèle ------------------------------------
def evaluer_fidelite(
    texte_attendu: str, texte_transcrit: str, *, langue: str = "fr",
    seg_logprobs: list[float] | None = None, min_mots: int = MOTS_MIN_VERIFIABLE,
) -> dict:
    """Combine `comparer` + les 3 détecteurs + les anti-faux-positifs.

    - `verifie=False` (aucun verdict) si le texte attendu fait moins de
      `min_mots` mots (bruit ASR disproportionné) ;
    - sauvetage phonétique pleine-phrase sur un effondrement de recall ;
    - une répétition déjà présente dans le TEXTE SOURCE n'est pas comptée.
    """
    attendus = normaliser_mots(texte_attendu, langue)
    base = {
        "verifie": False, "recall": 1.0, "precision": 1.0, "length_ratio": 0.0,
        "tail_recall": 1.0, "hallucination": False, "repetition": False,
        "troncature": False, "kind": "", "detail": "", "missing_words": [],
        "trailing_missing_words": [], "phonetic_similarity": None,
    }
    if len(attendus) < min_mots:
        return base

    cmp = comparer(texte_attendu, texte_transcrit, langue)
    hall = detecter_hallucination(
        cmp["recall"], precision=cmp["precision"], length_ratio=cmp["length_ratio"]
    )
    sim_phon = None
    if hall["hallucination"] and hall["kind"] == "recall":
        sim_phon = similarite_phonetique(texte_attendu, texte_transcrit, langue)
        if sim_phon is not None and sim_phon >= _PHRASE_PHONETIQUE_SIMILARITE_MIN:
            hall = {"hallucination": False, "kind": "", "detail": f"sauvetage phonétique (sim={sim_phon:.0%})"}

    rep = detecter_repetitions(cmp["transcribed_words"], seg_logprobs)
    if rep["repetition"] and rep["kind"] in ("run", "ngram", "ratio"):
        if detecter_repetitions(attendus)["repetition"]:
            rep = {"repetition": False, "kind": "", "detail": "répétition déjà dans le texte source"}

    trunc = detecter_troncature(cmp["trailing_missing_words"])

    kinds = []
    if hall["hallucination"]:
        kinds.append(f"hallucination:{hall['kind']}")
    if trunc["troncature"]:
        kinds.append("troncature:tail")
    if rep["repetition"]:
        kinds.append(f"repetition:{rep['kind']}")

    return {
        "verifie": True,
        "recall": cmp["recall"],
        "precision": cmp["precision"],
        "length_ratio": cmp["length_ratio"],
        "tail_recall": cmp["tail_recall"],
        "hallucination": hall["hallucination"],
        "repetition": rep["repetition"],
        "troncature": trunc["troncature"],
        "kind": " + ".join(kinds),
        "detail": "; ".join(d for d in (hall["detail"], trunc["detail"], rep["detail"]) if d),
        "missing_words": cmp["missing_words"],
        "trailing_missing_words": cmp["trailing_missing_words"],
        "phonetic_similarity": sim_phon,
    }
