"""Tests des helpers purs de mesurer_perceptuel (I/O CSV, parsing de nom)."""
from __future__ import annotations

from benchmark.mesurer_perceptuel import _lister_wavs, ecrire_perceptuel, lire_perceptuel


def test_lister_wavs(tmp_path):
    for n in ("p01_1.wav", "p26_3.wav", "bruit.wav", "p07_1.txt"):
        (tmp_path / n).write_bytes(b"")
    assert [(i, r) for i, r, _ in _lister_wavs(tmp_path)] == [("p01", 1), ("p26", 3)]


def test_perceptuel_roundtrip(tmp_path):
    f = tmp_path / "perceptuel.csv"
    ecrire_perceptuel(f, [
        {"id_phrase": "p01", "repetition": 1, "utmos": 3.42, "sim": 0.912},
        {"id_phrase": "p02", "repetition": 2, "utmos": 2.10, "sim": ""},  # SIM absente (Kokoro)
    ])
    relu = lire_perceptuel(f)
    assert relu[0] == {"id_phrase": "p01", "repetition": 1, "utmos": 3.42, "sim": 0.912}
    assert relu[1]["sim"] is None and relu[1]["utmos"] == 2.10
