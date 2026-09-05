#!/usr/bin/env python3
"""Échafaudage commun aux `models/<nom>/generer.py`.

Centralise ce que le CONTRAT_MODELE impose de faire à l'identique partout :
seed reproductible, mise en forme de l'audio de sortie (24 kHz mono 1D),
écriture de `timings.csv` / `meta.json`. Chaque adaptateur ne garde que
l'appel au modèle.
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path

import numpy as np

SR_SORTIE = 24_000

# Colonnes de timings.csv (ordre = contrat).
COLONNES_TIMINGS = (
    "id_phrase", "repetition", "seed", "ttfa_s", "gen_s", "audio_s",
    "vram_pic_mo", "categorie_chunk", "statut",
)


def fixer_seed(seed: int) -> None:
    """Rend un run reproductible : `random`, `numpy`, et `torch` (+ CUDA)
    si présent. Ne lève pas si torch est absent (venv commun)."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def _en_1d(wav) -> np.ndarray:
    """Garantit un signal 1D. `squeeze()` puis, s'il reste > 1 dimension,
    on garde la LIGNE 0. JAMAIS `reshape(-1)` : sur `(2, N)` il concatène
    les canaux -> chaque chunk joué deux fois (bug silencieux, APIAVISOL §3.10)."""
    arr = np.asarray(wav, dtype=np.float32)
    arr = np.squeeze(arr)
    if arr.ndim > 1:
        arr = arr[0]
    return np.ascontiguousarray(arr, dtype=np.float32)


def preparer_audio(wav, sr_entree: int, sr_sortie: int = SR_SORTIE) -> np.ndarray:
    """-> float32 1D mono à `sr_sortie`, borné à [-1, 1]. Les tensors
    `bfloat16` doivent être passés déjà convertis (l'appelant fait
    `.float().cpu().numpy()`)."""
    arr = _en_1d(wav)
    if sr_entree != sr_sortie:
        import librosa

        arr = librosa.resample(arr, orig_sr=sr_entree, target_sr=sr_sortie)
    return np.clip(arr, -1.0, 1.0).astype(np.float32)


def ecrire_wav(chemin: Path | str, wav_1d_float32: np.ndarray, sr: int = SR_SORTIE) -> float:
    """Écrit un WAV PCM 16 bits mono. Retourne la durée audio en secondes."""
    import soundfile as sf

    arr = _en_1d(wav_1d_float32)
    pcm16 = np.clip(arr, -1.0, 1.0)
    pcm16 = (pcm16 * 32767.0).round().astype(np.int16)
    Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(chemin), pcm16, sr, subtype="PCM_16")
    return len(arr) / sr


def silence(duree_ms: int, sr: int = SR_SORTIE) -> np.ndarray:
    return np.zeros(int(round(sr * duree_ms / 1000.0)), dtype=np.float32)


def ecrire_timings(chemin: Path | str, lignes: list[dict]) -> None:
    Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES_TIMINGS)
        w.writeheader()
        for ligne in lignes:
            w.writerow({c: ligne.get(c, "") for c in COLONNES_TIMINGS})


def ecrire_meta(chemin: Path | str, meta: dict) -> None:
    Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, sort_keys=True)
