"""Tests des helpers purs de mesurer_perceptuel (I/O CSV, parsing de nom).

UTMOS a été retiré (non calibré FR) : `perceptuel.csv` ne porte plus que
`sim`. Les anciens CSV avec une colonne `utmos` doivent rester relisables.
"""
from __future__ import annotations

from benchmark.mesurer_perceptuel import (
    _fini,
    _lister_wavs,
    ecrire_perceptuel,
    lire_perceptuel,
)


def test_lister_wavs(tmp_path):
    for n in ("p01_1.wav", "p26_3.wav", "bruit.wav", "p07_1.txt"):
        (tmp_path / n).write_bytes(b"")
    assert [(i, r) for i, r, _ in _lister_wavs(tmp_path)] == [("p01", 1), ("p26", 3)]


def test_perceptuel_roundtrip(tmp_path):
    f = tmp_path / "perceptuel.csv"
    ecrire_perceptuel(f, [
        {"id_phrase": "p01", "repetition": 1, "sim": 0.912},
        {"id_phrase": "p02", "repetition": 2, "sim": ""},  # SIM absente (Kokoro)
    ])
    relu = lire_perceptuel(f)
    assert relu[0] == {"id_phrase": "p01", "repetition": 1, "sim": 0.912}
    assert relu[1]["sim"] is None


def test_fini_rejette_non_finis():
    assert _fini(0.94) == 0.94
    assert _fini(float("nan")) == ""
    assert _fini(float("inf")) == ""
    assert _fini("") == "" and _fini(None) == ""


def test_lire_perceptuel_neutralise_nan(tmp_path):
    """Un 'nan' écrit par une ancienne passe (x-vector sur audio quasi vide)
    ne doit pas polluer les moyennes : relu comme absence de mesure."""
    f = tmp_path / "perceptuel.csv"
    f.write_text(
        "id_phrase,repetition,sim\n"
        "p02,2,\n"
        "p02,3,nan\n",
        encoding="utf-8",
    )
    relu = lire_perceptuel(f)
    assert relu[0]["sim"] is None
    assert relu[1]["sim"] is None


def test_lire_perceptuel_ignore_ancienne_colonne_utmos(tmp_path):
    """CSV d'une passe antérieure (colonne `utmos`) : relu sans erreur,
    `utmos` simplement ignorée, `sim` conservée."""
    f = tmp_path / "perceptuel.csv"
    f.write_text(
        "id_phrase,repetition,utmos,sim\n"
        "p01,1,3.42,0.912\n"
        "p02,2,2.10,\n",
        encoding="utf-8",
    )
    relu = lire_perceptuel(f)
    assert "utmos" not in relu[0]
    assert relu[0] == {"id_phrase": "p01", "repetition": 1, "sim": 0.912}
    assert relu[1]["sim"] is None
