"""Tests de la fidélité au contenu (benchmark/fidelite.py).

Le sauvetage phonétique dépend d'espeak-ng : les tests qui le touchent
tolèrent son absence (similarité None) plutôt que de la supposer.
"""
from __future__ import annotations

import benchmark.fidelite as fidelite
from benchmark.fidelite import (
    comparer,
    detecter_hallucination,
    detecter_repetitions,
    detecter_troncature,
    evaluer_fidelite,
    similarite_chaine,
    similarite_phonetique,
    _phonemiser,
    _sauvetage_suffixe_ortho,
)


# --- similarite_chaine ------------------------------------------------
def test_similarite_chaine():
    assert similarite_chaine("abc", "abc") == 1.0
    assert similarite_chaine("", "") == 1.0
    assert similarite_chaine("chat", "chien") < 0.6


def test_similarite_chaine_avec_chaine_vide():
    assert similarite_chaine("", "abc") == 0.0
    assert similarite_chaine("abc", "") == 0.0


# --- comparer -------------------------------------------------------
def test_comparer_match_parfait():
    c = comparer("le chat dort sur le mur", "le chat dort sur le mur")
    assert c["recall"] == 1.0
    assert c["precision"] == 1.0
    assert c["trailing_missing_words"] == []


def test_comparer_troncature_de_fin():
    c = comparer(
        "il gravit les marches du vieux clocher de pierre",
        "il gravit les marches",
    )
    assert c["trailing_missing_words"] == ["du", "vieux", "clocher", "de", "pierre"]
    assert c["recall"] < 1.0


def test_comparer_texte_attendu_vide():
    c = comparer("", "quelque chose")
    assert c["recall"] == 1.0 and c["trailing_missing_words"] == []


def test_comparer_expansion_nombres_evite_faux_positif():
    # « 73 » côté attendu, « soixante-treize » côté ASR : aucun mot manquant
    c = comparer("il compte 73 moutons ce soir", "il compte soixante-treize moutons ce soir")
    assert c["recall"] == 1.0
    assert c["missing_words"] == []


# --- detecter_hallucination ----------------------------------------
def test_hallucination_recall_effondre():
    d = detecter_hallucination(0.3)
    assert d["hallucination"] and d["kind"] == "recall"


def test_hallucination_contenu_ajoute():
    d = detecter_hallucination(0.95, precision=0.3, length_ratio=2.4)
    assert d["hallucination"] and d["kind"] == "extra"


def test_hallucination_absente():
    assert detecter_hallucination(0.9, precision=0.9, length_ratio=1.05)["hallucination"] is False


# --- detecter_troncature -----------------------------------------
def test_troncature_seuil():
    assert detecter_troncature(["clocher"])["troncature"] is True
    assert detecter_troncature([])["troncature"] is False


# --- detecter_repetitions --------------------------------------
def test_repetition_run():
    d = detecter_repetitions(["du", "du", "du", "pain"])
    assert d["repetition"] and d["kind"] == "run"


def test_repetition_ngram():
    d = detecter_repetitions(["encore", "le", "crabe", "encore", "le", "crabe", "fin"])
    assert d["repetition"] and d["kind"] == "ngram"


def test_repetition_bigramme():
    d = detecter_repetitions(["ah", "bon", "ah", "bon", "vraiment"])
    assert d["repetition"] and d["kind"] == "ngram"


def test_repetition_lowprob():
    d = detecter_repetitions(["texte", "normal", "ici"], seg_logprobs=[-0.2, -2.5])
    assert d["repetition"] and d["kind"] == "lowprob"


def test_repetition_absente():
    assert detecter_repetitions(["une", "phrase", "tout", "a", "fait", "normale"])["repetition"] is False


# --- sauvetage orthographique du suffixe ------------------------
def test_sauvetage_suffixe_ortho_nom_propre_mal_transcrit():
    # « Franfrelou » attendu, « franc frelou » transcrit (sur-découpage)
    assert _sauvetage_suffixe_ortho(["franfrelou"], ["le", "sorcier", "franc", "frelou"]) == []


def test_sauvetage_suffixe_ortho_vraie_troncature_non_masquee():
    # « clocher » jamais prononcé : aucun candidat proche -> reste manquant
    assert _sauvetage_suffixe_ortho(["clocher"], ["il", "gravit", "les", "marches"]) == ["clocher"]


# --- sauvetage phonétique : ne lève jamais -------------------
def test_phonemiser_ne_leve_jamais():
    # espeak-ng présent -> str ; absent -> None. Jamais d'exception.
    res = _phonemiser("bonjour", "fr-fr")
    assert res is None or isinstance(res, str)


def test_similarite_phonetique_tolerante_a_l_absence_de_backend():
    sim = similarite_phonetique("bonjour", "bonjour", "fr")
    assert sim is None or sim >= 0.99


def test_sauvetages_court_circuites_si_backend_absent(monkeypatch):
    # Force l'état « backend indisponible » : les sauvetages phonétiques
    # doivent renvoyer None / laisser le suffixe intact, sans lever.
    monkeypatch.setattr(fidelite, "_backend_phonemizer_ok", False)
    assert similarite_phonetique("s'écria flo", "ses cris à flots", "fr") is None
    c = comparer("elle poussa la porte du grenier poussiereux", "elle poussa la porte")
    assert c["trailing_missing_words"] == ["du", "grenier", "poussiereux"]


# --- evaluer_fidelite (orchestration) -------------------------
def test_evaluer_fidelite_texte_trop_court_non_verifie():
    r = evaluer_fidelite("Oui.", "oui")
    assert r["verifie"] is False


def test_evaluer_fidelite_match_parfait():
    r = evaluer_fidelite(
        "le vieux moulin tournait lentement dans le vent du soir",
        "le vieux moulin tournait lentement dans le vent du soir",
    )
    assert r["verifie"] is True
    assert r["hallucination"] is False and r["repetition"] is False and r["troncature"] is False


def test_evaluer_fidelite_repetition_du_source_non_penalisee():
    src = "non non non je ne veux pas y aller"
    r = evaluer_fidelite(src, src)
    assert r["repetition"] is False


def test_evaluer_fidelite_troncature_detectee():
    r = evaluer_fidelite(
        "elle poussa la lourde porte de chene massif du grenier",
        "elle poussa la lourde porte",
    )
    assert r["verifie"] and r["troncature"] is True
    assert "troncature:tail" in r["kind"]
