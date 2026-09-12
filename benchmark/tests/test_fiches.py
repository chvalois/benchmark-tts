"""Garde-fous du registre de fiches modèles (`benchmark/fiches_modeles.yaml`).

Le registre est une donnée DÉCLARÉE : ces tests ne vérifient pas la véracité des
textes (impossible automatiquement) mais la discipline qui la rend vérifiable —
tout modèle publié a une fiche, toute fiche cite au moins une source https et
porte une date de vérification.
"""
from __future__ import annotations

import json

import pytest
import yaml

from benchmark.fiches import (
    ErreurFiche,
    charger_fiches,
    modeles_scorables,
    verifier_coherence_lock,
)


def test_registre_reel_valide():
    reg = charger_fiches()
    assert reg, "registre vide"


def test_registre_reel_coherent_avec_le_lock():
    assert verifier_coherence_lock() == []


def test_tout_modele_score_a_une_fiche():
    manquants = sorted(modeles_scorables() - set(charger_fiches()))
    assert manquants == [], f"modèles scorés sans fiche : {manquants}"


def test_chaque_fiche_cite_une_source_https_et_une_date():
    for nom, e in charger_fiches().items():
        assert e["sources"], f"{nom} sans source"
        assert all(s["url"].startswith("https://") for s in e["sources"]), nom
        assert str(e["verifie_le"]).count("-") == 2, f"{nom} : date non ISO"


def test_chaque_fiche_documente_au_moins_un_choix_technique():
    for nom, e in charger_fiches().items():
        assert e["choix_techniques"], f"{nom} sans choix technique"
        for bloc in e["choix_techniques"]:
            assert bloc["titre"].strip() and bloc["texte"].strip(), nom


def test_chaque_fiche_declare_ses_langues_avec_une_source():
    for nom, e in charger_fiches().items():
        assert e["langues"]["resume"].strip(), f"{nom} : résumé des langues vide"
        assert e["langues"]["source"].strip(), f"{nom} : source des langues absente"


def test_chaque_fiche_documente_les_parametres_reglables():
    for nom, e in charger_fiches().items():
        assert e["parametres"], f"{nom} : aucun paramètre documenté"
        for p in e["parametres"]:
            assert str(p["nom"]).strip() and str(p["role"]).strip(), nom


def test_refuse_fiche_sans_langues(tmp_path):
    sans = {k: v for k, v in BASE.items() if k != "langues"}
    with pytest.raises(ErreurFiche, match="champs manquants"):
        charger_fiches(_ecrire(tmp_path, {"m": sans}))


def test_refuse_langues_sans_source(tmp_path):
    flou = {**BASE, "langues": {"resume": "2 langues"}}
    with pytest.raises(ErreurFiche, match="langues.source"):
        charger_fiches(_ecrire(tmp_path, {"m": flou}))


def test_refuse_parametre_sans_role(tmp_path):
    flou = {**BASE, "parametres": [{"nom": "speed"}]}
    with pytest.raises(ErreurFiche, match="parametres"):
        charger_fiches(_ecrire(tmp_path, {"m": flou}))


def _ecrire(tmp_path, data):
    p = tmp_path / "fiches.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


BASE = {
    "une_phrase": "x", "particularite": "y",
    "choix_techniques": [{"titre": "t", "texte": "tx"}],
    "langues": {"resume": "2 langues", "source": "model card"},
    "parametres": [{"nom": "speed", "role": "vitesse"}],
    "a_savoir": [],
    "sources": [{"label": "l", "url": "https://example.org"}],
    "verifie_le": "2026-01-01",
}


def test_refuse_champ_manquant(tmp_path):
    manque = {k: v for k, v in BASE.items() if k != "sources"}
    with pytest.raises(ErreurFiche, match="champs manquants"):
        charger_fiches(_ecrire(tmp_path, {"m": manque}))


def test_refuse_source_non_https(tmp_path):
    mauvais = {**BASE, "sources": [{"label": "l", "url": "http://example.org"}]}
    with pytest.raises(ErreurFiche, match="non https"):
        charger_fiches(_ecrire(tmp_path, {"m": mauvais}))


def test_refuse_fiche_sans_choix_technique(tmp_path):
    vide = {**BASE, "choix_techniques": []}
    with pytest.raises(ErreurFiche, match="aucun choix technique"):
        charger_fiches(_ecrire(tmp_path, {"m": vide}))


def test_refuse_date_de_verification_vide(tmp_path):
    sans_date = {**BASE, "verifie_le": ""}
    with pytest.raises(ErreurFiche, match="verifie_le"):
        charger_fiches(_ecrire(tmp_path, {"m": sans_date}))


def test_signale_fiche_orpheline(tmp_path, monkeypatch):
    lock = tmp_path / "models.lock"
    lock.write_text(json.dumps({"modeles": {"connu": {}}}), encoding="utf-8")
    div = verifier_coherence_lock({"inconnu": BASE}, chemin_lock=lock)
    assert any("absent de models.lock" in d for d in div)
