"""Tests des helpers purs de mesurer_nisqa (I/O CSV `nisqa.csv`).

Le runner (`nisqa_dossier`) charge le modèle NISQA → non testé ici.
"""
from __future__ import annotations

from benchmark.mesurer_nisqa import _num, ecrire_nisqa, lire_nisqa


def test_nisqa_roundtrip(tmp_path):
    f = tmp_path / "nisqa.csv"
    ecrire_nisqa(f, [
        {"id_phrase": "p01", "repetition": 1, "nisqa": 3.421},
        {"id_phrase": "p02", "repetition": 2, "nisqa": ""},  # fichier sans score
    ])
    relu = lire_nisqa(f)
    assert relu[0] == {"id_phrase": "p01", "repetition": 1, "nisqa": 3.421}
    assert relu[1] == {"id_phrase": "p02", "repetition": 2, "nisqa": None}


def test_lire_nisqa_neutralise_vide_et_nan(tmp_path):
    f = tmp_path / "nisqa.csv"
    f.write_text(
        "id_phrase,repetition,nisqa\n"
        "p01,1,\n"
        "p02,2,nan\n"
        "p03,3,inf\n"
        "p04,1,2.75\n",
        encoding="utf-8",
    )
    relu = lire_nisqa(f)
    assert [r["nisqa"] for r in relu] == [None, None, None, 2.75]


def test_num_tolere_tout():
    assert _num("2.5") == 2.5
    assert _num("") is None and _num(None) is None and _num("abc") is None
    assert _num("nan") is None and _num("inf") is None
