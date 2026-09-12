"""Tests du chargement/validation du corpus (benchmark/corpus.py)."""
from __future__ import annotations

import textwrap

import pytest

from benchmark.corpus import (
    GENRES_LONGFORM,
    ErreurCorpus,
    Phrase,
    TexteLong,
    charger_corpus,
    charger_longform,
)


# --- corpus réel du dépôt --------------------------------------------
def test_corpus_reel_se_charge_et_est_valide():
    phrases = charger_corpus()
    assert len(phrases) == 34
    assert all(isinstance(p, Phrase) for p in phrases)
    assert phrases[0].id == "p01"


def test_corpus_reel_expose_les_types_attendus():
    par_id = {p.id: p for p in charger_corpus()}
    assert par_id["p24"].est_titre is True
    assert par_id["p26"].type == "long_form"
    assert par_id["p27"].est_multi_voix is True
    assert par_id["p01"].type == "phrase"


# --- validation sur fichiers temporaires ------------------------
def _ecrire(tmp_path, contenu: str):
    f = tmp_path / "phrases.yaml"
    f.write_text(textwrap.dedent(contenu), encoding="utf-8")
    return f


def test_charge_une_entree_minimale(tmp_path):
    f = _ecrire(tmp_path, """
        x01:
          texte: "Bonjour."
          longueur: court
          registre: narration
          pieges: []
    """)
    (p,) = charger_corpus(f)
    assert p.id == "x01" and p.pieges == ()


@pytest.mark.parametrize(
    "corps, motif",
    [
        ("texte: \"a\"\n  longueur: court\n  registre: narration", "champs manquants"),
        ("texte: \"a\"\n  longueur: XXL\n  registre: narration\n  pieges: []", "longueur invalide"),
        ("texte: \"a\"\n  longueur: court\n  registre: sarcasme\n  pieges: []", "registre invalide"),
        ("texte: \"a\"\n  longueur: court\n  registre: narration\n  pieges: [zzz]", "pièges inconnus"),
        ("texte: \" \"\n  longueur: court\n  registre: narration\n  pieges: []", "texte vide"),
        ("texte: \"a\"\n  longueur: court\n  registre: narration\n  pieges: []\n  type: bizarre", "type invalide"),
    ],
)
def test_entree_invalide_leve(tmp_path, corps, motif):
    f = _ecrire(tmp_path, f"x01:\n  {corps}\n")
    with pytest.raises(ErreurCorpus, match=motif):
        charger_corpus(f)


def test_entree_non_dict_leve(tmp_path):
    f = tmp_path / "phrases.yaml"
    f.write_text("x01: juste une chaine\n", encoding="utf-8")
    with pytest.raises(ErreurCorpus, match="non-dict"):
        charger_corpus(f)


def test_corpus_vide_leve(tmp_path):
    f = tmp_path / "vide.yaml"
    f.write_text("", encoding="utf-8")
    with pytest.raises(ErreurCorpus, match="vide ou mal formé"):
        charger_corpus(f)


def test_phrase_est_immuable():
    p = Phrase("p", "t", "court", "narration", ())
    with pytest.raises(Exception):
        p.texte = "autre"  # type: ignore[misc]


# --- volet long-form (v2) ---------------------------------------------
def test_longform_reel_se_charge_et_est_valide():
    textes = charger_longform()
    assert len(textes) == 12
    assert all(isinstance(t, TexteLong) for t in textes)
    assert {t.genre for t in textes} <= GENRES_LONGFORM
    # podcast ET journalisme représentés (demande explicite)
    genres = {t.genre for t in textes}
    assert {"podcast_solo", "podcast_dialogue", "interview_reponse"} & genres
    assert {"journalisme_flash", "journalisme_reportage", "edito"} & genres
    assert all(t.fictif is True for t in textes)          # 100 % inventé
    assert all(t.texte.count("\n\n") >= 1 for t in textes)  # multi-paragraphe


def test_longform_compat_pipeline():
    """TexteLong doit traverser executer_corpus / le scoring comme une Phrase."""
    t = charger_longform()[0]
    assert t.est_titre is False and t.est_multi_voix is False
    assert t.longueur == "long"
    assert t.registre == t.genre and t.pieges == t.traits
    assert t.type == "long_form"


def _ecrire_lf(tmp_path, corps: str):
    f = tmp_path / "longform.yaml"
    f.write_text(textwrap.dedent(corps), encoding="utf-8")
    return f


def test_longform_entree_minimale(tmp_path):
    f = _ecrire_lf(tmp_path, """
        x01:
          titre: "T"
          genre: podcast_solo
          duree_cible_s: 90
          fictif: true
          traits: [disfluence]
          texte: |
            Un paragraphe.

            Un autre.
    """)
    (t,) = charger_longform(f)
    assert t.id == "x01" and t.genre == "podcast_solo" and t.traits == ("disfluence",)


@pytest.mark.parametrize(
    "corps, motif",
    [
        ('titre: T\n  genre: podcast_solo\n  fictif: true\n  traits: []\n  texte: "a"', "champs manquants"),
        ('titre: T\n  genre: tribune\n  duree_cible_s: 90\n  fictif: true\n  traits: []\n  texte: "a"', "genre invalide"),
        ('titre: T\n  genre: edito\n  duree_cible_s: 0\n  fictif: true\n  traits: []\n  texte: "a"', "duree_cible_s invalide"),
        ('titre: T\n  genre: edito\n  duree_cible_s: 90\n  fictif: false\n  traits: []\n  texte: "a"', "fictif doit valoir true"),
        ('titre: T\n  genre: edito\n  duree_cible_s: 90\n  fictif: true\n  traits: [zzz]\n  texte: "a"', "traits inconnus"),
        ('titre: T\n  genre: edito\n  duree_cible_s: 90\n  fictif: true\n  traits: []\n  texte: "  "', "texte vide"),
    ],
)
def test_longform_entree_invalide_leve(tmp_path, corps, motif):
    f = _ecrire_lf(tmp_path, f"x01:\n  {corps}\n")
    with pytest.raises(ErreurCorpus, match=motif):
        charger_longform(f)
