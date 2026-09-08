"""Agrégation du test d'écoute — section ÉMOTION (logique pure).

Deux protocoles cohabitent :
- **nouveau** : modèle A vs modèle B, même voix `papa_<émotion>` → win-rate ;
- **archivé** : réf. émotionnelle vs réf. neutre (même modèle) → taux de transfert.
"""
from __future__ import annotations

import json

import pytest

from benchmark import agreger_ecoute


def _sol(tmp_path, monkeypatch, emo):
    p = tmp_path / "_solution.json"
    p.write_text(json.dumps({"build": {"rep": 1}, "clips": {}, "ab": {}, "mos": {},
                             "emo": emo}), encoding="utf-8")
    monkeypatch.setattr(agreger_ecoute, "SOLUTION", p)
    monkeypatch.setattr(agreger_ecoute, "_lignes_objectives", lambda: {})
    return tmp_path


def _export(dir_, pseudo, votes):
    p = dir_ / f"ecoute_{pseudo}.json"
    p.write_text(json.dumps({"pseudo": pseudo, "mode": "emo", "votes": votes}),
                 encoding="utf-8")
    return p


# ---------- nouveau protocole : modèle vs modèle ----------
@pytest.fixture
def sol_mv(tmp_path, monkeypatch):
    return _sol(tmp_path, monkeypatch, {
        "e1": {"phrase": "p02", "emotion": "colere", "voix": "papa_colere",
               "A_modele": "firered_tts3", "B_modele": "voxcpm2"},
        "e2": {"phrase": "p07", "emotion": "colere", "voix": "papa_colere",
               "A_modele": "voxcpm2", "B_modele": "chatterbox_v3"},
        "e3": {"phrase": "p04", "emotion": "tristesse", "voix": "papa_tristesse",
               "A_modele": "firered_tts3", "B_modele": "chatterbox_v3"},
    })


def test_emo_modele_vs_modele(sol_mv):
    e = _export(sol_mv, "alice", [
        {"id": "e1", "choix": "A"},   # firered bat voxcpm
        {"id": "e2", "choix": "="},   # voxcpm = chatterbox
        {"id": "e3", "choix": "A"},   # firered bat chatterbox
    ])
    md = agreger_ecoute.agreger([e])
    assert "## Émotion — quel modèle rend le mieux l'émotion ?" in md
    assert "| firered_tts3 | 100% | 2.0 / 2 |" in md
    assert "| voxcpm2 | 25% | 0.5 / 2 |" in md
    assert "| chatterbox_v3 | 25% | 0.5 / 2 |" in md
    assert "win-rate par (modèle, émotion)" in md


def test_emo_ignore_votes_sans_choix(sol_mv):
    e = _export(sol_mv, "carol", [
        {"id": "e1", "choix": "B"},
        {"id": "e2"},                 # pas de choix -> ignoré
        {"id": "zzz", "choix": "A"},   # id inconnu -> ignoré
    ])
    md = agreger_ecoute.agreger([e])
    assert "| voxcpm2 | 100% | 1.0 / 1 |" in md


def test_pas_de_section_emo_si_aucun_vote(sol_mv):
    e = sol_mv / "ecoute_dave.json"
    e.write_text(json.dumps({"pseudo": "dave", "mode": "mos", "votes": []}),
                 encoding="utf-8")
    md = agreger_ecoute.agreger([e])
    assert "## Émotion" not in md
