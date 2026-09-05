"""Tests de la mesure de stabilité (benchmark/stabilite.py)."""
from __future__ import annotations

from benchmark.stabilite import stabilite_duree


def _l(pid, audio_s):
    return {"id_phrase": pid, "audio_s": audio_s}


def test_item_stable_non_suspect():
    lignes = [_l("p01", 2.00), _l("p01", 2.02), _l("p01", 1.98)]
    res = stabilite_duree(lignes)
    assert res["par_phrase"]["p01"]["suspect"] is False
    assert res["n_suspects"] == 0


def test_item_instable_suspect():
    # 48 s vs 90 s pour le même texte -> CV largement au-dessus du seuil
    lignes = [_l("p26", 48.0), _l("p26", 90.0), _l("p26", 62.0)]
    res = stabilite_duree(lignes)
    assert res["par_phrase"]["p26"]["suspect"] is True
    assert res["n_suspects"] == 1


def test_moins_de_deux_runs_ignore():
    res = stabilite_duree([_l("p07", 3.0)])
    assert res["par_phrase"] == {}
    assert res["cv_median"] == 0.0


def test_cv_median_sur_plusieurs_items():
    lignes = [
        _l("a", 10.0), _l("a", 10.0),          # CV 0
        _l("b", 10.0), _l("b", 12.0),          # CV > 0
    ]
    res = stabilite_duree(lignes)
    assert 0.0 <= res["cv_median"] <= 0.2
    assert set(res["par_phrase"]) == {"a", "b"}
