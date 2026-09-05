"""Tests des helpers purs du runner ASR (benchmark/transcrire.py).

Les fonctions qui chargent Whisper ne sont pas testées ici (nécessitent
le modèle) — voir couverture omit dans pyproject.
"""
from __future__ import annotations

from benchmark.transcrire import _lister_wavs, ecrire_transcriptions, lire_transcriptions


def test_lister_wavs_parse_id_et_repetition(tmp_path):
    for nom in ("p01_1.wav", "p01_2.wav", "p26_1.wav", "bruit.wav", "p07_1.txt"):
        (tmp_path / nom).write_bytes(b"")
    trouves = _lister_wavs(tmp_path)
    assert [(i, r) for i, r, _ in trouves] == [("p01", 1), ("p01", 2), ("p26", 1)]


def test_transcriptions_roundtrip(tmp_path):
    f = tmp_path / "transcriptions.csv"
    lignes = [
        {"id_phrase": "p01", "repetition": 1, "texte_transcrit": "bonjour le monde"},
        {"id_phrase": "p02", "repetition": 3, "texte_transcrit": "il fait beau"},
    ]
    ecrire_transcriptions(f, lignes)
    relu = lire_transcriptions(f)
    assert relu[0] == {"id_phrase": "p01", "repetition": 1, "texte_transcrit": "bonjour le monde"}
    assert relu[1]["repetition"] == 3
