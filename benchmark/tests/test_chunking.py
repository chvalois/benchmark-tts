"""Tests du découpage en chunks (benchmark/chunking.py)."""
from __future__ import annotations

from benchmark.chunking import (
    FAMILLE_CHATTERBOX,
    FAMILLE_DEFAUT,
    ParamsChunk,
    categorie_globale,
    decouper,
    segmenter_en_phrases,
)


def test_segmenter_en_phrases():
    assert segmenter_en_phrases("Un. Deux ! Trois ?") == ["Un.", "Deux !", "Trois ?"]


def test_phrase_courte_reste_un_seul_chunk():
    (c,) = decouper("Une phrase simple et posée.")
    assert c.categorie == "narration"
    assert c.silence_apres_ms == 0  # dernier chunk : rien après


def test_replique_courte_categorisee():
    (c,) = decouper("Non.")
    assert c.categorie == "replique_courte"


def test_dialogue_detecte_sur_tiret_cadratin():
    (c,) = decouper("— Tu viens avec nous ce soir, ou pas du tout ?")
    assert c.categorie == "dialogue"


def test_borne_de_mots_force_le_decoupage():
    params = ParamsChunk(max_mots=6, max_cars=1000)
    texte = "Alpha bravo charlie delta echo. Foxtrot golf hotel india juliett."
    chunks = decouper(texte, params)
    assert len(chunks) == 2
    assert all(len(c.texte.split()) <= 6 for c in chunks)


def test_bascule_narration_dialogue_coupe():
    texte = "Il ouvrit lentement la porte du grenier poussiéreux. — Il y a quelqu'un ici ?"
    chunks = decouper(texte)
    assert len(chunks) == 2
    assert chunks[0].categorie == "narration"
    assert chunks[1].categorie == "dialogue"


def test_saut_de_paragraphe_coupe_et_silence_paragraphe():
    texte = "Premier paragraphe, assez court mais complet.\n\nSecond paragraphe distinct."
    chunks = decouper(texte)
    assert len(chunks) == 2
    assert chunks[0].silence_apres_ms == FAMILLE_DEFAUT.silence_paragraphe_ms


def test_silence_fort_apres_exclamation():
    texte = "Attention, c'est dangereux ! On continue quand même la descente maintenant."
    chunks = decouper(texte, ParamsChunk(max_mots=5, max_cars=1000))
    assert chunks[0].silence_apres_ms == FAMILLE_DEFAUT.silence_forte_ms


def test_famille_chatterbox_borne_caracteres_plus_stricte():
    assert FAMILLE_CHATTERBOX.max_cars == 160
    long = " ".join(["mot"] * 80) + "."          # ~320 cars, < 60 mots
    chunks = decouper(long, FAMILLE_CHATTERBOX)
    assert len(chunks) >= 2
    assert all(len(c.texte) <= FAMILLE_CHATTERBOX.max_cars for c in chunks)


def test_categorie_globale():
    assert categorie_globale(decouper("Une simple phrase de narration ici.")) == "narration"
    mixte = decouper("Il entra dans la vaste salle vide et sombre. — Bonjour, il y a quelqu'un ?")
    assert categorie_globale(mixte) == "mixte"
    assert categorie_globale([]) == "inconnu"
