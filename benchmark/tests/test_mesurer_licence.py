"""Tests du registre de licences (benchmark/mesurer_licence.py)."""
from __future__ import annotations

import textwrap

import pytest

from benchmark.mesurer_licence import (
    ErreurLicence,
    charger_licences,
    tableau_licences,
    verdict_commercial,
    verifier_coherence_lock,
)


# --- registre réel du dépôt ----------------------------------------
def test_registre_reel_se_charge():
    reg = charger_licences()
    assert "chatterbox_v3" in reg and "xtts_v2" in reg


def test_verdicts_connus():
    reg = charger_licences()
    assert "commercial" in verdict_commercial("chatterbox_v3", reg)
    assert "non commercial" in verdict_commercial("xtts_v2", reg)
    assert "conditionnel" in verdict_commercial("higgs_audio_v3", reg)


def test_coherence_avec_models_lock():
    # Le dépôt doit rester cohérent : aucune divergence de verdict commercial.
    assert verifier_coherence_lock() == []


def test_tableau_licences_trie_et_complet():
    t = tableau_licences()
    modeles = [r["modele"] for r in t]
    assert modeles == sorted(modeles)
    assert all({"licence", "usage_commercial", "verdict", "note"} <= r.keys() for r in t)


# --- validations sur registre temporaire ------------------------
def _ecrire(tmp_path, contenu):
    f = tmp_path / "licences.yaml"
    f.write_text(textwrap.dedent(contenu), encoding="utf-8")
    return f


def test_usage_invalide_leve(tmp_path):
    f = _ecrire(tmp_path, """
        m1:
          licence: MIT
          usage_commercial: peut-etre
          source_url: ""
          verifie_le: null
          note: ""
    """)
    with pytest.raises(ErreurLicence, match="usage_commercial invalide"):
        charger_licences(f)


def test_conditionnel_sans_note_leve(tmp_path):
    f = _ecrire(tmp_path, """
        m1:
          licence: "code Apache / poids NC"
          usage_commercial: conditionnel
          source_url: ""
          verifie_le: null
          note: ""
    """)
    with pytest.raises(ErreurLicence, match="exige une note"):
        charger_licences(f)


def test_champ_manquant_leve(tmp_path):
    f = _ecrire(tmp_path, "m1:\n  licence: MIT\n  usage_commercial: oui\n")
    with pytest.raises(ErreurLicence, match="champs manquants"):
        charger_licences(f)


def test_verdict_modele_inconnu_leve():
    with pytest.raises(ErreurLicence, match="absent du registre"):
        verdict_commercial("modele_fantome", charger_licences())


def test_registre_vide_leve(tmp_path):
    f = tmp_path / "licences.yaml"
    f.write_text("", encoding="utf-8")
    with pytest.raises(ErreurLicence, match="vide ou mal formé"):
        charger_licences(f)


def test_coherence_signale_modele_absent_du_registre():
    # registre partiel : chatterbox_v3 (présent dans models.lock) manque
    partiel = {
        "kokoro_82m": {
            "licence": "Apache-2.0", "usage_commercial": "oui",
            "source_url": "", "verifie_le": None, "note": "",
        }
    }
    div = verifier_coherence_lock(partiel)
    assert any("chatterbox_v3" in d and "absent de licences.yaml" in d for d in div)
