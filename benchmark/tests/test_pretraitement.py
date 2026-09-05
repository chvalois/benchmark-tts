"""Tests du pré-traitement texte FR (benchmark/pretraitement.py).

Chaque étape §3.9 est couverte isolément, plus le pipeline complet et les
cas limites (faux positifs FR : abréviations, incise impersonnelle,
signe degré, élisions).
"""
from __future__ import annotations

import pytest

from benchmark.pretraitement import (
    ajouter_ponctuation_finale,
    desamorcer_onomatopees,
    normaliser_apostrophes,
    normaliser_points_suspension,
    pretraiter,
    retirer_structure_markdown,
    retirer_virgule_incise,
    segmenter_phrases,
    supprimer_emojis,
)


# --- Étape 0 : apostrophes -------------------------------------------------
def test_apostrophes_typographiques_normalisees():
    assert normaliser_apostrophes("qu’il l‘a vu") == "qu'il l'a vu"


# --- Étape 1 : structure markdown --------------------------------------
@pytest.mark.parametrize(
    "entree, attendu",
    [
        ("# Titre\nTexte", "Titre\nTexte"),
        ("### Sous-titre", "Sous-titre"),
        ("- premier point", "premier point"),
        ("1. étape une", "étape une"),
        ("> citation", "citation"),
        ("---", ""),
    ],
)
def test_structure_markdown_retiree(entree, attendu):
    assert retirer_structure_markdown(entree) == attendu


def test_structure_markdown_preserve_les_asterisques_onomatopee():
    assert retirer_structure_markdown("*Vroum* dit-il") == "*Vroum* dit-il"


# --- Étape 2 : virgule d'incise --------------------------------------
@pytest.mark.parametrize(
    "entree, attendu",
    [
        ('« Bonjour », répond Juliette.', '« Bonjour » répond Juliette.'),
        ("« Assez ! », s'écria Flo.", "« Assez ! » s'écria Flo."),
        ("« Oui », dit-il.", "« Oui » dit-il."),
        ("« Quoi », demanda-t-elle.", "« Quoi » demanda-t-elle."),
    ],
)
def test_virgule_incise_retiree(entree, attendu):
    assert retirer_virgule_incise(entree) == attendu


def test_virgule_incise_ne_touche_pas_dis_moi():
    # « dis-moi » n'est pas une incise de parole rapportée
    assert retirer_virgule_incise("Non, dis-moi tout.") == "Non, dis-moi tout."


def test_virgule_incise_insensible_a_la_casse():
    assert retirer_virgule_incise("« Stop », Dit le garde.") == "« Stop » Dit le garde."


# --- Étape 3 : points de suspension --------------------------------------
@pytest.mark.parametrize(
    "entree, attendu",
    [
        ("mot... mot", "mot. mot"),
        ("mot… mot", "mot. mot"),
        ("mot . . . mot", "mot . mot"),
        ("fin....", "fin."),
        ("deux points .. ici", "deux points . ici"),
    ],
)
def test_points_suspension_normalises(entree, attendu):
    assert normaliser_points_suspension(entree) == attendu


def test_points_suspension_laisse_un_point_simple():
    assert normaliser_points_suspension("Fin. Suite.") == "Fin. Suite."


# --- Étape 4 : onomatopées -----------------------------------------------
@pytest.mark.parametrize(
    "entree, attendu",
    [
        ("*Vroum!*", "*Vroum*"),
        ("*Bam !!*", "*Bam*"),
        ("un *Boum!* soudain", "un *Boum* soudain"),
        ("*Vroum* intact", "*Vroum* intact"),
    ],
)
def test_onomatopees_desamorcees(entree, attendu):
    assert desamorcer_onomatopees(entree) == attendu


def test_onomatopees_ne_touche_pas_hors_asterisques():
    assert desamorcer_onomatopees("Attention !") == "Attention !"


# --- Étape 5 : segmentation --------------------------------------------
def test_segmentation_insere_saut_de_ligne_entre_phrases():
    assert segmenter_phrases("Il partit. Elle resta.") == "Il partit.\nElle resta."


def test_segmentation_ne_coupe_pas_apres_abreviation():
    assert segmenter_phrases("Dit M. Dupont hier.") == "Dit M. Dupont hier."
    assert segmenter_phrases("etc. Voilà.") == "etc. Voilà."


def test_segmentation_ne_coupe_pas_en_milieu_de_phrase():
    assert segmenter_phrases("un chat noir et blanc") == "un chat noir et blanc"


def test_segmentation_coupe_avant_un_chiffre():
    assert segmenter_phrases("Fin. 1789 arriva.") == "Fin.\n1789 arriva."


# --- Étape 6 : émojis --------------------------------------------------
@pytest.mark.parametrize(
    "entree, attendu",
    [
        ("Bravo 🎉 !", "Bravo  !"),
        ("👍🏽 ok", " ok"),
        ("drapeau 🇫🇷 ici", "drapeau  ici"),
        ("cœur ❤️ battant", "cœur  battant"),
    ],
)
def test_emojis_supprimes(entree, attendu):
    assert supprimer_emojis(entree) == attendu


def test_emojis_preserve_texte_et_ponctuation_fr():
    texte = "À 20°C, il fait « bon » ; n° 26, coût 5 €."
    assert supprimer_emojis(texte) == texte


# --- §3.1 : ponctuation finale ---------------------------------------
def test_ponctuation_finale_ajoutee_si_absente():
    assert ajouter_ponctuation_finale("La danse du Kabuki") == "La danse du Kabuki."


@pytest.mark.parametrize("texte", ["Déjà ponctué.", "Vraiment ?", "Stop !", "Fin…"])
def test_ponctuation_finale_inchangee_si_presente(texte):
    assert ajouter_ponctuation_finale(texte) == texte


# --- Pipeline complet -----------------------------------------------
def test_pipeline_ordre_et_composition():
    entree = "# Chapitre\n« Vas-y ! », s’écria-t-il... *Go!* 🎉"
    sortie = pretraiter(entree)
    assert sortie.startswith("Chapitre")
    assert "s'écria-t-il." in sortie  # apostrophe ASCII + suspension -> point
    assert "*Go*" in sortie           # onomatopée désamorcée
    assert "🎉" not in sortie
    assert "," not in sortie.split("s'écria")[0][-3:]  # virgule d'incise partie


def test_pipeline_est_titre_ajoute_le_point():
    assert pretraiter("La danse mystérieuse du Kabuki", est_titre=True) == (
        "La danse mystérieuse du Kabuki."
    )


def test_pipeline_idempotent_sur_texte_propre():
    propre = "Une phrase simple et correcte."
    assert pretraiter(propre) == propre


def test_pipeline_texte_long_multi_phrases_segmente():
    entree = "Il gravit les 73 marches. Puis il attendit. Le train arriva."
    sortie = pretraiter(entree)
    assert sortie.count("\n") == 2
