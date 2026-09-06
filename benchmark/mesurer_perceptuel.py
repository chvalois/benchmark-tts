#!/usr/bin/env python3
"""Métriques perceptuelles objectives : UTMOS (naturel prédit) + SIM
(similarité au locuteur de la voix de référence).

- **UTMOS** : `tarepan/SpeechMOS` (utmos22_strong, torch.hub). Scalaire
  ~1–5 par fichier, sans référence. ⚠️ entraîné sur du MOS anglophone →
  valeur absolue non calibrée pour le FR ; à lire en **classement
  relatif** sur le même corpus.
- **SIM** : cosinus des embeddings `microsoft/wavlm-base-plus-sv`
  (`WavLMForXVector`) entre l'audio généré et la voix de référence. ⚠️
  proxy transformers ; le SIM « papers » utilise wavlm-large finetuné.

Modèle-dépendant : tourne dans le venv `_commun`. Les helpers d'I/O
(`lire_perceptuel`, `_lister_wavs`) restent purs et testés.

    source env.sh
    uv run --python "$TTSB_VENVS/_commun/bin/python" benchmark/mesurer_perceptuel.py \
        --audio-dir "$TTSB_AUDIO_OUT/firered_tts3/papa_narration"
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SR_CIBLE = 16_000
MAX_SECONDES = 30  # fenêtre analysée (UTMOS/SIM n'ont pas besoin de plus ;
#                    protège des fichiers pathologiques, ex. runaway MOSS 5 min)
_NOM_WAV = re.compile(r"^(?P<id>[^_]+)_(?P<rep>\d+)\.wav$")
COLONNES = ("id_phrase", "repetition", "utmos", "sim")


def _lister_wavs(dossier: Path) -> list[tuple[str, int, Path]]:
    out = []
    for p in sorted(dossier.glob("*.wav")):
        m = _NOM_WAV.match(p.name)
        if m:
            out.append((m.group("id"), int(m.group("rep")), p))
    return out


def _charger_utmos():
    import torch

    return torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)


def _charger_sv():
    import os

    from transformers import AutoFeatureExtractor, WavLMForXVector

    cache = os.environ.get("HF_HUB_CACHE")
    fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-base-plus-sv", cache_dir=cache)
    model = WavLMForXVector.from_pretrained("microsoft/wavlm-base-plus-sv", cache_dir=cache).eval()
    return fe, model


def _lire_16k(chemin: Path):
    import librosa
    import soundfile as sf

    y, sr = sf.read(str(chemin))
    if getattr(y, "ndim", 1) > 1:
        y = y.mean(axis=1)
    y = y.astype("float32")
    if sr != SR_CIBLE:
        y = librosa.resample(y, orig_sr=sr, target_sr=SR_CIBLE)
    return y[: MAX_SECONDES * SR_CIBLE]


def _embedding(fe, model, y):
    import torch

    with torch.no_grad():
        return model(**fe([y], sampling_rate=SR_CIBLE, return_tensors="pt")).embeddings


def perceptuel_dossier(audio_dir: Path | str, ref_wav: Path | str | None) -> list[dict]:
    """UTMOS pour chaque `<id>_<rep>.wav` ; SIM vs `ref_wav` si fourni."""
    import torch

    audio_dir = Path(audio_dir)
    wavs = _lister_wavs(audio_dir)
    if not wavs:
        raise SystemExit(f"[FAIL] aucun <id>_<rep>.wav dans {audio_dir}")

    utmos = _charger_utmos()
    emb_ref = None
    if ref_wav and Path(ref_wav).is_file():
        fe, sv = _charger_sv()
        emb_ref = _embedding(fe, sv, _lire_16k(Path(ref_wav)))
    else:
        fe = sv = None
        print(f"[perceptuel] pas de voix de référence pour {audio_dir.name} -> SIM omise", flush=True)

    lignes: list[dict] = []
    for i, (pid, rep, chemin) in enumerate(wavs, 1):
        try:
            y = _lire_16k(chemin)
            score_utmos = round(float(utmos(torch.from_numpy(y).unsqueeze(0), SR_CIBLE)), 3)
            sim = ""
            if emb_ref is not None:
                sim = round(torch.nn.functional.cosine_similarity(
                    emb_ref, _embedding(fe, sv, y)).item(), 4)
        except Exception as e:  # noqa: BLE001 — un fichier pathologique ne casse pas le dossier
            print(f"[perceptuel] {chemin.name} -> échec ({type(e).__name__}: {e})", flush=True)
            score_utmos, sim = "", ""
        lignes.append({"id_phrase": pid, "repetition": rep, "utmos": score_utmos, "sim": sim})
        if i % 25 == 0 or i == len(wavs):
            print(f"[perceptuel] {i}/{len(wavs)}", flush=True)
    return lignes


def ecrire_perceptuel(chemin: Path | str, lignes: list[dict]) -> None:
    Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES)
        w.writeheader()
        w.writerows(lignes)


def lire_perceptuel(chemin: Path | str) -> list[dict]:
    with open(chemin, newline="", encoding="utf-8") as f:
        out = []
        for row in csv.DictReader(f):
            out.append({
                "id_phrase": row["id_phrase"],
                "repetition": int(row["repetition"]) if row.get("repetition") else None,
                "utmos": float(row["utmos"]) if row.get("utmos") else None,
                "sim": float(row["sim"]) if row.get("sim") not in ("", None) else None,
            })
        return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--audio-dir", required=True)
    p.add_argument("--ref", default="", help="défaut : corpus/voix_reference/<nom du dossier>.wav")
    p.add_argument("--out", default="", help="défaut : <audio-dir>/perceptuel.csv")
    args = p.parse_args()

    audio_dir = Path(args.audio_dir)
    ref = Path(args.ref) if args.ref else RACINE / "corpus" / "voix_reference" / f"{audio_dir.name}.wav"
    out = Path(args.out) if args.out else audio_dir / "perceptuel.csv"

    lignes = perceptuel_dossier(audio_dir, ref if Path(ref).is_file() else None)
    ecrire_perceptuel(out, lignes)
    print(f"[perceptuel] {len(lignes)} lignes -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
