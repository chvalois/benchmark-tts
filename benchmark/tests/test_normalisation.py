"""Tests de la normalisation ASR (benchmark/normalisation.py)."""
from __future__ import annotations

import pytest

from benchmark.normalisation import (
    developper_nombres,
    normaliser_mots,
    normaliser_texte,
    retirer_balises,
)


@pytest.mark.parametrize(
    "entree, attendu",
    [
        ("[pause 0.5s] mot", "  mot"),          # balise -> " " + espace déjà présent
        ("<voice:enfant>salut", " salut"),
        ("<lang:fr> bonjour", "  bonjour"),
        ("<fx:echo>boum", " boum"),
        ("<voice:a>un <voice:b>deux", " un  deux"),
    ],
)
def test_retirer_balises(entree, attendu):
    assert retirer_balises(entree) == attendu


@pytest.mark.parametrize(
    "entree, attendu",
    [
        ("73 marches", "soixante-treize marches"),
        ("le 14 juillet 1789", "le quatorze juillet mille sept cent quatre-vingt-neuf"),
        ("10,5 litres", "dix virgule cinq litres"),
        ("aucun nombre", "aucun nombre"),
    ],
)
def test_developper_nombres(entree, attendu):
    assert developper_nombres(entree) == attendu


def test_normaliser_texte_reference_et_hypothese_convergent():
    # « 73 » et « soixante-treize » convergent ; le trait d'union est un
    # séparateur de tokens (des deux côtés) -> "soixante treize".
    ref = normaliser_texte("Il gravit les 73 marches.")
    hyp = normaliser_texte("il gravit les soixante-treize marches")
    assert ref == hyp == "il gravit les soixante treize marches"


def test_normaliser_texte_retire_ponctuation_et_balises():
    assert normaliser_texte("« Bonjour ! » [pause 1.0s] dit-il.") == "bonjour dit il"


def test_normaliser_mots_liste():
    assert normaliser_mots("Deux mots.") == ["deux", "mots"]


def test_normaliser_mots_vide():
    assert normaliser_mots("   ") == []
    assert normaliser_mots("!?,;") == []
