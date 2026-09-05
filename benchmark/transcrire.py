#!/usr/bin/env python3
"""Runner ASR — transcrit l'audio généré pour alimenter le scoring.

Modèle-dépendant, volontairement THIN : charge `whisper-large-v3-french`
(transformers), transcrit chaque `<id>_<rep>.wav` d'un dossier, écrit
`transcriptions.csv`. Le scoring (WER + fidélité) est fait ensuite par
`benchmark/evaluer.py` (pur).

    source env.sh
    uv run --python "$TTSB_VENVS/_commun/bin/python" benchmark/transcrire.py \
        --audio-dir "$TTSB_AUDIO_OUT/chatterbox_v3"

Jamais lancé pendant qu'un modèle TTS est chargé (un seul modèle GPU à la
fois — APIAVISOL §2.3).
"""
from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path

REPO_ASR = "bofenghuang/whisper-large-v3-french"
REVISION_ASR = "90a7cd1fea9cd69f80f5a0fc49738418dba96083"
SR_ASR = 16_000
_NOM_WAV = re.compile(r"^(?P<id>[^_]+)_(?P<rep>\d+)\.wav$")


def _lister_wavs(dossier: Path) -> list[tuple[str, int, Path]]:
    trouves = []
    for p in sorted(dossier.glob("*.wav")):
        m = _NOM_WAV.match(p.name)
        if m:
            trouves.append((m.group("id"), int(m.group("rep")), p))
    return trouves


def _charger_pipeline(device: str):
    import torch
    from transformers import pipeline

    return pipeline(
        "automatic-speech-recognition",
        model=REPO_ASR,
        revision=REVISION_ASR,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device=0 if device == "cuda" else -1,
        chunk_length_s=30,      # long-form (p26) découpé par le pipeline
        model_kwargs={"cache_dir": os.environ.get("HF_HUB_CACHE")},
    )


def transcrire_dossier(audio_dir: Path | str, *, device: str = "cuda") -> list[dict]:
    audio_dir = Path(audio_dir)
    wavs = _lister_wavs(audio_dir)
    if not wavs:
        raise SystemExit(f"[FAIL] aucun <id>_<rep>.wav dans {audio_dir}")

    asr = _charger_pipeline(device)
    lignes: list[dict] = []
    for i, (pid, rep, chemin) in enumerate(wavs, 1):
        out = asr(
            str(chemin),
            generate_kwargs={"language": "fr", "task": "transcribe"},
            return_timestamps=False,
        )
        texte = (out.get("text") or "").strip()
        lignes.append({"id_phrase": pid, "repetition": rep, "texte_transcrit": texte})
        print(f"[{i}/{len(wavs)}] {pid}_{rep}: {texte[:70]}", flush=True)
    return lignes


def ecrire_transcriptions(chemin: Path | str, lignes: list[dict]) -> None:
    Path(chemin).parent.mkdir(parents=True, exist_ok=True)
    with open(chemin, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id_phrase", "repetition", "texte_transcrit"])
        w.writeheader()
        w.writerows(lignes)


def lire_transcriptions(chemin: Path | str) -> list[dict]:
    with open(chemin, newline="", encoding="utf-8") as f:
        lignes = []
        for row in csv.DictReader(f):
            row["repetition"] = int(row["repetition"]) if row.get("repetition") else None
            lignes.append(row)
        return lignes


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--audio-dir", required=True)
    p.add_argument("--out", default="", help="défaut : <audio-dir>/transcriptions.csv")
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    out = Path(args.out) if args.out else Path(args.audio_dir) / "transcriptions.csv"
    lignes = transcrire_dossier(args.audio_dir, device=args.device)
    ecrire_transcriptions(out, lignes)
    print(f"[transcrire] {len(lignes)} transcriptions -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
