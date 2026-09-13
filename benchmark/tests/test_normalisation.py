"""Tests de la normalisation ASR (benchmark/normalisation.py)."""
from __future__ import annotations

import pytest

from benchmark.normalisation import (
    developper_heures,
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


@pytest.mark.parametrize(
    "entree, attendu",
    [
        ("le train de 10 h 45", "le train de 10 heures 45"),   # espacé (corpus)
        ("le train de 10h45", "le train de 10 heures 45"),      # collé (ASR fréquent)
        ("le train de 10h 45", "le train de 10 heures 45"),     # espacement mixte
        ("le train de 10 h45", "le train de 10 heures 45"),
        ("il est 8h", "il est 8 heures"),                       # sans minutes
        ("le train de 10 heures 45", "le train de 10 heures 45"),  # déjà en clair -> idempotent
        ("aucune heure ici", "aucune heure ici"),
    ],
)
def test_developper_heures(entree, attendu):
    assert developper_heures(entree) == attendu


def test_normaliser_texte_convergence_heure_espacee_collee_et_en_clair():
    # Les 3 formes qu'on rencontre en pratique (texte de référence écrit
    # avec espaces, ASR qui colle "10h45", ASR qui développe "10 heures 45")
    # doivent produire EXACTEMENT la même normalisation -> WER = 0 pour un
    # modèle qui lit l'heure correctement, quelle que soit la graphie.
    formes = ["10 h 45", "10h45", "10 heures 45"]
    normalisees = {normaliser_texte(f"Il attendit le train de {f} du soir.") for f in formes}
    assert len(normalisees) == 1
    assert "dix heures quarante cinq" in next(iter(normalisees))


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
