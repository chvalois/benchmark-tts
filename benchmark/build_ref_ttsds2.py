#!/usr/bin/env python3
"""Construit le corpus de **vraie parole française de référence** pour
TTSDS2 (`mesurer_ttsds2.py`).

Source : **MLS-French** — `facebook/multilingual_librispeech`, config
`french`, split `test` (lectures d'audiobooks du domaine public LibriVox,
CC-BY-4.0). Échantillonne ~`--n` clips de 3–30 s sur ~`--locuteurs`
`speaker_id` distincts (round-robin, ordre de flux → déterministe),
réécrit **mono 24 kHz** dans `$TTSB_ROOT/ttsds2_ref/fr/` + un
`MANIFEST.json` (source, licence, locuteurs, durées).

Caveat assumé : MLS est un corpus connu, potentiellement vu à
l'entraînement par certains TTS. Acceptable ici — TTSDS2 est la métrique
de naturalité *automatique*, l'arbitre final reste l'écoute humaine. Pour
un corpus non contaminé, pointer `--source-dir` vers un dossier de wav FR
propre : le reste du pipeline lit un dossier, quelle qu'en soit l'origine.

    source env.sh
    uv run --python "$TTSB_VENVS/_ttsds2/bin/python" benchmark/build_ref_ttsds2.py
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SR_CIBLE = 24_000
DUREE_MIN_S, DUREE_MAX_S = 3.0, 30.0
HF_DATASET = "facebook/multilingual_librispeech"
HF_CONFIG, HF_SPLIT = "french", "test"
LICENCE = "CC-BY-4.0 (MLS / LibriVox domaine public)"


def _sortie_defaut() -> Path:
    racine = os.environ.get("TTSB_ROOT", str(RACINE))
    return Path(racine) / "ttsds2_ref" / "fr"


def _ecrire_wav(chemin: Path, y, sr_src: int) -> float:
    import librosa
    import soundfile as sf

    if getattr(y, "ndim", 1) > 1:
        y = y.mean(axis=1)
    y = y.astype("float32")
    if sr_src != SR_CIBLE:
        y = librosa.resample(y, orig_sr=sr_src, target_sr=SR_CIBLE)
    sf.write(str(chemin), y, SR_CIBLE, subtype="PCM_16")
    return len(y) / SR_CIBLE


def depuis_source_dir(source: Path, sortie: Path, n: int) -> list[dict]:
    """Variante hors-MLS : recopie/normalise les .wav d'un dossier fourni."""
    import soundfile as sf

    src_wavs = sorted(source.glob("*.wav"))[:n]
    if not src_wavs:
        raise SystemExit(f"[FAIL] aucun .wav dans {source}")
    items = []
    for i, w in enumerate(src_wavs):
        y, sr = sf.read(str(w))
        dur = len(y) / sr
        if not (DUREE_MIN_S <= dur <= DUREE_MAX_S):
            continue
        dest = sortie / f"ref_{i:04d}.wav"
        d = _ecrire_wav(dest, y, sr)
        items.append({"fichier": dest.name, "source": w.name, "duree_s": round(d, 2)})
    return items


def depuis_mls(sortie: Path, n: int, n_loc: int, par_loc: int) -> list[dict]:
    from datasets import load_dataset

    ds = load_dataset(HF_DATASET, HF_CONFIG, split=HF_SPLIT, streaming=True)
    pris: dict[str, int] = {}
    items: list[dict] = []
    for ex in ds:
        if len(items) >= n:
            break
        spk = str(ex.get("speaker_id", ex.get("speaker", "?")))
        if spk not in pris and len(pris) >= n_loc:
            continue
        if pris.get(spk, 0) >= par_loc:
            continue
        au = ex["audio"]
        y, sr = au["array"], au["sampling_rate"]
        dur = len(y) / sr
        if not (DUREE_MIN_S <= dur <= DUREE_MAX_S):
            continue
        idx = len(items)
        dest = sortie / f"ref_{idx:04d}.wav"
        d = _ecrire_wav(dest, y, sr)
        pris[spk] = pris.get(spk, 0) + 1
        items.append({
            "fichier": dest.name, "speaker_id": spk,
            "id": str(ex.get("id", ex.get("audio_id", idx))),
            "duree_s": round(d, 2),
        })
    return items


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--out", default="", help=f"défaut : {_sortie_defaut()}")
    p.add_argument("--n", type=int, default=150, help="nombre de clips cible")
    p.add_argument("--locuteurs", type=int, default=30, help="locuteurs distincts max")
    p.add_argument("--par-locuteur", type=int, default=6, help="clips max par locuteur")
    p.add_argument("--source-dir", default="",
                   help="dossier de .wav FR à utiliser à la place de MLS-French")
    p.add_argument("--force", action="store_true", help="réécrit même si déjà peuplé")
    args = p.parse_args()

    sortie = Path(args.out) if args.out else _sortie_defaut()
    manifest = sortie / "MANIFEST.json"
    if manifest.is_file() and not args.force:
        print(f"[ref-ttsds2] déjà construit : {manifest} (--force pour refaire)")
        return 0
    sortie.mkdir(parents=True, exist_ok=True)
    for vieux in sortie.glob("ref_*.wav"):
        vieux.unlink()

    if args.source_dir:
        items = depuis_source_dir(Path(args.source_dir), sortie, args.n)
        source = f"source-dir:{args.source_dir}"
    else:
        items = depuis_mls(sortie, args.n, args.locuteurs, args.par_locuteur)
        source = f"{HF_DATASET}:{HF_CONFIG}/{HF_SPLIT}"

    if not items:
        raise SystemExit("[FAIL] aucun clip retenu")

    locs = sorted({it["speaker_id"] for it in items if "speaker_id" in it})
    durees = [it["duree_s"] for it in items]
    manifest.write_text(json.dumps({
        "source": source,
        "licence": LICENCE,
        "sr_hz": SR_CIBLE,
        "duree_min_s": DUREE_MIN_S, "duree_max_s": DUREE_MAX_S,
        "n_clips": len(items),
        "n_locuteurs": len(locs),
        "duree_totale_s": round(sum(durees), 1),
        "locuteurs": locs,
        "clips": items,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ref-ttsds2] {len(items)} clips / {len(locs)} locuteurs / "
          f"{sum(durees):.0f}s -> {sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
