"""Tests de l'échafaudage de génération (benchmark/generation.py)."""
from __future__ import annotations

import numpy as np

from benchmark.generation import (
    COLONNES_TIMINGS,
    ecrire_meta,
    ecrire_timings,
    ecrire_wav,
    fixer_seed,
    preparer_audio,
    silence,
    _en_1d,
)


def test_fixer_seed_reproductible():
    fixer_seed(123)
    a = np.random.rand(5)
    fixer_seed(123)
    b = np.random.rand(5)
    assert np.array_equal(a, b)


def test_en_1d_depuis_stereo_ne_concatene_pas():
    # (2, N) -> on garde la ligne 0, PAS la concaténation des deux canaux
    stereo = np.array([[0.1, 0.2, 0.3], [0.9, 0.9, 0.9]], dtype=np.float32)
    out = _en_1d(stereo)
    assert out.shape == (3,)
    assert np.allclose(out, [0.1, 0.2, 0.3])


def test_en_1d_depuis_colonne():
    assert _en_1d(np.zeros((4, 1))).shape == (4,)


def test_preparer_audio_borne_et_type():
    brut = np.array([2.0, -3.0, 0.5], dtype=np.float32)
    out = preparer_audio(brut, sr_entree=24_000)
    assert out.dtype == np.float32
    assert out.max() <= 1.0 and out.min() >= -1.0


def test_ecrire_wav_duree_et_relecture(tmp_path):
    import soundfile as sf

    sig = (0.2 * np.sin(np.linspace(0, 100, 24_000))).astype(np.float32)  # 1 s @ 24k
    chemin = tmp_path / "chatterbox_v3" / "p01_1.wav"
    duree = ecrire_wav(chemin, sig)
    assert abs(duree - 1.0) < 1e-6
    data, sr = sf.read(str(chemin))
    assert sr == 24_000 and data.ndim == 1 and len(data) == 24_000


def test_silence_longueur():
    assert len(silence(500)) == 12_000  # 0,5 s @ 24k


def test_ecrire_timings_colonnes_et_ordre(tmp_path):
    f = tmp_path / "timings.csv"
    ecrire_timings(f, [
        {"id_phrase": "p01", "repetition": 1, "seed": 42, "ttfa_s": 0.3,
         "gen_s": 1.2, "audio_s": 2.0, "vram_pic_mo": 4100,
         "categorie_chunk": "narration", "statut": "ok"},
        {"id_phrase": "p27", "repetition": 1, "statut": "n/a"},  # champs partiels tolérés
    ])
    lignes = f.read_text(encoding="utf-8").splitlines()
    assert lignes[0] == ",".join(COLONNES_TIMINGS)
    assert lignes[1].startswith("p01,1,42,")
    assert lignes[2].startswith("p27,1,,,,,,,n/a")


def test_ecrire_meta_json(tmp_path):
    import json

    f = tmp_path / "meta.json"
    ecrire_meta(f, {"repo_id": "ResembleAI/chatterbox", "revision": "5bb1f6ee"})
    assert json.loads(f.read_text(encoding="utf-8"))["revision"] == "5bb1f6ee"
