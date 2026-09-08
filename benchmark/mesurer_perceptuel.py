#!/usr/bin/env python3
"""Métrique perceptuelle objective : SIM (similarité au locuteur de la voix
de référence).

- **SIM** : cosinus des embeddings **ECAPA-TDNN**
  (`speechbrain/spkrec-ecapa-voxceleb`, entraîné VoxCeleb) entre l'audio
  généré et la voix de référence, **silences rognés** (`librosa.trim`,
  30 dB) des deux côtés. ECAPA sépare beaucoup mieux les locuteurs que
  `wavlm-base-plus-sv` (dont les cosinus, tous ~0,96, ne discriminaient
  pas — cf. corrélation nulle avec la note humaine de similarité).

**Aucune métrique de naturalité automatique** dans le benchmark : UTMOS,
TTSDS2 et NISQA ont tous été testés et écartés (non pertinents /
anti-corrélés avec la note humaine en français) — cf.
`docs/METHODOLOGIE.md` §10. La naturalité se juge à l'écoute
(`benchmark/agreger_ecoute.py`, `resultats/ecoute.md`).

Modèle-dépendant : tourne dans le venv `_commun`. Les helpers d'I/O
(`lire_perceptuel`, `_lister_wavs`) restent purs et testés.

    source env.sh
    uv run --python "$TTSB_VENVS/_commun/bin/python" benchmark/mesurer_perceptuel.py \
        --audio-dir "$TTSB_AUDIO_OUT/firered_tts3/papa_narration"
"""
from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SR_CIBLE = 16_000
MAX_SECONDES = 30  # fenêtre analysée (UTMOS/SIM n'ont pas besoin de plus ;
#                    protège des fichiers pathologiques, ex. runaway MOSS 5 min)
MIN_SECONDES = 0.4  # en-dessous, x-vector / UTMOS dégénèrent (embedding NaN) :
#                     génération quasi vide -> pas de score plutôt qu'un NaN


def _fini(x):
    """Valeur si finie, sinon '' (traitée comme 'pas de mesure' en aval)."""
    try:
        return x if math.isfinite(float(x)) else ""
    except (TypeError, ValueError):
        return ""


_NOM_WAV = re.compile(r"^(?P<id>[^_]+)_(?P<rep>\d+)\.wav$")
COLONNES = ("id_phrase", "repetition", "sim")


def _lister_wavs(dossier: Path) -> list[tuple[str, int, Path]]:
    out = []
    for p in sorted(dossier.glob("*.wav")):
        m = _NOM_WAV.match(p.name)
        if m:
            out.append((m.group("id"), int(m.group("rep")), p))
    return out


SV_MODELE = "speechbrain/spkrec-ecapa-voxceleb"
TRIM_DB = 30          # silences rognés à 30 dB sous la crête avant embedding SV


def _charger_sv():
    import os

    from speechbrain.inference.speaker import EncoderClassifier

    cache = os.environ.get("HF_HUB_CACHE") or os.environ.get("TTSB_ROOT", ".")
    return EncoderClassifier.from_hparams(
        source=SV_MODELE, savedir=str(Path(cache) / "speechbrain-ecapa"),
        run_opts={"device": "cpu"},
    )


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


def _rogner(y):
    """Rogne les silences tête/queue (les générations ajoutent du silence
    de fin de chunk qui dilue l'embedding locuteur)."""
    import librosa

    coupe, _ = librosa.effects.trim(y, top_db=TRIM_DB)
    return coupe if len(coupe) >= MIN_SECONDES * SR_CIBLE else y


def _embedding(model, y):
    import torch

    with torch.no_grad():
        emb = model.encode_batch(torch.from_numpy(_rogner(y)).unsqueeze(0))
    return emb.reshape(1, -1)


def perceptuel_dossier(audio_dir: Path | str, ref_wav: Path | str | None) -> list[dict]:
    """SIM vs `ref_wav` (cosinus ECAPA) pour chaque `<id>_<rep>.wav`."""
    import torch

    audio_dir = Path(audio_dir)
    wavs = _lister_wavs(audio_dir)
    if not wavs:
        raise SystemExit(f"[FAIL] aucun <id>_<rep>.wav dans {audio_dir}")

    emb_ref = sv = None
    if ref_wav and Path(ref_wav).is_file():
        sv = _charger_sv()
        emb_ref = _embedding(sv, _lire_16k(Path(ref_wav)))
    else:
        print(f"[perceptuel] pas de voix de référence pour {audio_dir.name} -> SIM omise", flush=True)

    lignes: list[dict] = []
    for i, (pid, rep, chemin) in enumerate(wavs, 1):
        try:
            y = _lire_16k(chemin)
            if len(y) < MIN_SECONDES * SR_CIBLE:
                print(f"[perceptuel] {chemin.name} -> {len(y) / SR_CIBLE:.2f}s "
                      f"(< {MIN_SECONDES}s) : génération quasi vide, score omis", flush=True)
                sim = ""
            else:
                sim = ""
                if emb_ref is not None:
                    sim = _fini(round(torch.nn.functional.cosine_similarity(
                        emb_ref, _embedding(sv, y)).item(), 4))
        except Exception as e:  # noqa: BLE001 — un fichier pathologique ne casse pas le dossier
            print(f"[perceptuel] {chemin.name} -> échec ({type(e).__name__}: {e})", flush=True)
            sim = ""
        lignes.append({"id_phrase": pid, "repetition": rep, "sim": sim})
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
        def _num(v):
            try:
                x = float(v)
            except (TypeError, ValueError):
                return None
            return x if math.isfinite(x) else None

        for row in csv.DictReader(f):
            # `utmos` : colonne d'anciennes passes, ignorée si présente.
            out.append({
                "id_phrase": row["id_phrase"],
                "repetition": int(row["repetition"]) if row.get("repetition") else None,
                "sim": _num(row.get("sim")),
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
