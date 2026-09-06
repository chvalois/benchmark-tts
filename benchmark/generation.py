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
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

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


# -- boucle générique corpus × voix × répétitions ---------------------
def executer_corpus(
    *,
    nom_modele: str,
    synthetiser: Callable[[str, str, object], np.ndarray],
    sr_modele: int,
    phrases: list,
    voix_refs: dict,
    reps: int,
    base_seed: int,
    racine_sortie: Path,
    params_chunk,
    meta_base: dict,
    est_non_applicable: Callable[[object], str | None] | None = None,
) -> int:
    """Déroule le corpus pour chaque voix (contrat CONTRAT_MODELE.md).

    - `synthetiser(texte_chunk, categorie, ref) -> np.ndarray` au SR du
      modèle : SEULE partie propre au modèle.
    - `voix_refs` : `{voix: ref}` — `ref` est opaque (chemin WAV de clonage,
      ou id de voix interne), passé tel quel à `synthetiser`.
    - `est_non_applicable(phrase) -> motif|None` : ex. `multi_voix` non
      géré → lignes `n/a` (jamais `echec`).

    Écrit `<racine_sortie>/<voix>/{<id>_<rep>.wav, timings.csv, meta.json}`.
    Retourne le nombre total de runs `ok`.
    """
    from benchmark.chunking import categorie_globale, decouper
    from benchmark.pretraitement import pretraiter
    from benchmark.vram import PicVRAM

    total_ok = 0
    for voix, ref in voix_refs.items():
        sortie = racine_sortie / voix
        lignes: list[dict] = []
        for ph in phrases:
            motif = est_non_applicable(ph) if est_non_applicable else None
            if motif:
                for rep in range(1, reps + 1):
                    lignes.append({"id_phrase": ph.id, "repetition": rep, "statut": f"n/a:{motif}"})
                print(f"[{nom_modele}/{voix}] {ph.id} -> n/a ({motif})", flush=True)
                continue

            texte = pretraiter(ph.texte, est_titre=ph.est_titre)
            chunks = decouper(texte, params_chunk)
            cat_globale = categorie_globale(chunks)

            for rep in range(1, reps + 1):
                seed = base_seed + rep
                fixer_seed(seed)
                pic = PicVRAM()
                try:
                    with pic:
                        t0 = time.perf_counter()
                        morceaux: list[np.ndarray] = []
                        ttfa = 0.0
                        for i, ch in enumerate(chunks):
                            brut = synthetiser(ch.texte, ch.categorie, ref)
                            if i == 0:
                                ttfa = time.perf_counter() - t0
                            morceaux.append(preparer_audio(brut, sr_modele))
                            if ch.silence_apres_ms:
                                morceaux.append(silence(ch.silence_apres_ms))
                        gen_s = time.perf_counter() - t0
                        audio = np.concatenate(morceaux) if morceaux else np.zeros(0, np.float32)
                    audio_s = ecrire_wav(sortie / f"{ph.id}_{rep}.wav", audio)
                    statut = "ok"
                except Exception as e:  # noqa: BLE001 — on journalise, on continue le corpus
                    ttfa = gen_s = audio_s = 0.0
                    statut = f"echec:{type(e).__name__}"
                    print(f"[{nom_modele}/{voix}] {ph.id} rep {rep} -> {statut}: {e}", flush=True)
                lignes.append({
                    "id_phrase": ph.id, "repetition": rep, "seed": seed,
                    "ttfa_s": round(ttfa, 4), "gen_s": round(gen_s, 4),
                    "audio_s": round(audio_s, 4), "vram_pic_mo": pic.pic_mo or "",
                    "categorie_chunk": cat_globale, "statut": statut,
                })

        ecrire_timings(sortie / "timings.csv", lignes)
        ecrire_meta(sortie / "meta.json", {
            **meta_base, "modele": nom_modele, "voix": voix,
            "reps": reps, "base_seed": base_seed,
            "date_run": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        n_ok = sum(1 for x in lignes if x["statut"] == "ok")
        total_ok += n_ok
        print(f"[{nom_modele}/{voix}] terminé : {n_ok}/{len(lignes)} runs ok -> {sortie}", flush=True)
    return total_ok
