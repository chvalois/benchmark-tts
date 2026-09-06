"""Tests de la boucle générique executer_corpus (benchmark/generation.py)."""
from __future__ import annotations

import csv
import json

import numpy as np

from benchmark.chunking import FAMILLE_DEFAUT
from benchmark.corpus import Phrase
from benchmark.generation import executer_corpus

PHRASES = [
    Phrase("p01", "Une phrase de narration simple et posée pour le test.", "moyen", "narration", ()),
    Phrase("p02", "Chapitre premier", "court", "narration", (), "titre"),
    Phrase("p27", "<voice:a>Salut. <voice:b>Bonjour.", "moyen", "dialogue_joie", (), "multi_voix"),
]


def _synth_ok(texte, categorie, ref, seed=0):
    # 0,1 s d'audio par chunk, amplitude qui dépend du texte (déterministe)
    n = 2400
    return (0.1 * np.ones(n, dtype=np.float32)) * (len(texte) % 7 + 1) / 7


def test_executer_corpus_produit_wav_timings_meta(tmp_path):
    n_ok = executer_corpus(
        nom_modele="faux",
        synthetiser=_synth_ok,
        sr_modele=24_000,
        phrases=PHRASES,
        voix_refs={"voixA": "refA"},
        reps=2,
        base_seed=100,
        racine_sortie=tmp_path,
        params_chunk=FAMILLE_DEFAUT,
        meta_base={"repo_id": "x/y", "revision": "abc"},
        est_non_applicable=lambda ph: "multi_voix" if ph.est_multi_voix else None,
    )
    d = tmp_path / "voixA"
    # p01 + p02 => 2 phrases x 2 reps = 4 wav ; p27 => n/a (0 wav)
    assert n_ok == 4
    assert sorted(p.name for p in d.glob("*.wav")) == [
        "p01_1.wav", "p01_2.wav", "p02_1.wav", "p02_2.wav",
    ]
    rows = list(csv.DictReader(open(d / "timings.csv")))
    assert len(rows) == 6  # 4 ok + 2 lignes n/a (p27)
    na = [r for r in rows if r["statut"].startswith("n/a")]
    assert len(na) == 2 and na[0]["id_phrase"] == "p27"
    ok = [r for r in rows if r["statut"] == "ok"]
    assert all(float(r["audio_s"]) > 0 for r in ok)
    assert all(int(r["seed"]) in (101, 102) for r in ok)

    meta = json.loads((d / "meta.json").read_text())
    assert meta["modele"] == "faux" and meta["voix"] == "voixA" and meta["reps"] == 2
    assert meta["repo_id"] == "x/y" and "date_run" in meta


def test_executer_corpus_echec_isole_ne_stoppe_pas(tmp_path):
    appels = {"n": 0}

    def _synth_capricieux(texte, categorie, ref, seed=0):
        appels["n"] += 1
        if appels["n"] == 1:          # échoue sur le tout premier chunk
            raise RuntimeError("boom")
        return np.full(2400, 0.05, dtype=np.float32)

    n_ok = executer_corpus(
        nom_modele="faux",
        synthetiser=_synth_capricieux,
        sr_modele=24_000,
        phrases=[PHRASES[0]],
        voix_refs={"v": "r"},
        reps=3,
        base_seed=0,
        racine_sortie=tmp_path,
        params_chunk=FAMILLE_DEFAUT,
        meta_base={},
    )
    rows = list(csv.DictReader(open(tmp_path / "v" / "timings.csv")))
    assert n_ok == 2
    assert [r["statut"] for r in rows].count("ok") == 2
    assert any(r["statut"].startswith("echec:") for r in rows)


def test_executer_corpus_multi_voix(tmp_path):
    executer_corpus(
        nom_modele="faux", synthetiser=_synth_ok, sr_modele=24_000,
        phrases=[PHRASES[0]], voix_refs={"v1": "r1", "v2": "r2"},
        reps=1, base_seed=0, racine_sortie=tmp_path,
        params_chunk=FAMILLE_DEFAUT, meta_base={},
    )
    assert (tmp_path / "v1" / "p01_1.wav").is_file()
    assert (tmp_path / "v2" / "p01_1.wav").is_file()
