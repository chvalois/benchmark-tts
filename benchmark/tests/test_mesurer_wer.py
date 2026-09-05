"""Tests du WER FR (benchmark/mesurer_wer.py)."""
from __future__ import annotations

from benchmark.mesurer_wer import agreger_wer, plancher_wer, wer


def test_wer_parfait():
    r = wer("le chat dort sur le mur", "le chat dort sur le mur")
    assert r["wer"] == 0.0
    assert r["hits"] == 6 and r["substitutions"] == 0
    assert r["n_ref"] == 6


def test_wer_une_substitution():
    r = wer("le chat dort", "le chien dort")
    assert r["substitutions"] == 1
    assert abs(r["wer"] - 1 / 3) < 1e-9


def test_wer_normalisation_nombres_ne_penalise_pas():
    r = wer("il a 21 ans", "il a vingt et un ans")
    assert r["wer"] == 0.0


def test_wer_reference_vide():
    assert wer("", "")["wer"] == 0.0
    r = wer("", "du bruit ajoute")
    assert r["wer"] == 1.0 and r["insertions"] == 3


def test_agreger_wer_global_et_categories():
    mesures = [
        {"wer": 0.0, "longueur": "court", "registre": "narration", "pieges": []},
        {"wer": 0.2, "longueur": "court", "registre": "narration", "pieges": ["nombre"]},
        {"wer": 0.4, "longueur": "long", "registre": "cours_magistral", "pieges": ["nombre", "liaison"]},
    ]
    agg = agreger_wer(mesures)
    assert agg["global"]["n"] == 3
    assert abs(agg["global"]["wer_moyen"] - 0.2) < 1e-9
    assert agg["par_longueur"]["court"]["n"] == 2
    assert agg["par_piege"]["nombre"]["n"] == 2      # phrase à 2 pièges comptée dans chaque groupe
    assert agg["par_piege"]["liaison"]["n"] == 1


def test_plancher_wer_sans_donnee_est_zero():
    assert plancher_wer([]) == 0.0
    assert abs(plancher_wer([{"wer": 0.05}, {"wer": 0.07}]) - 0.06) < 1e-9
