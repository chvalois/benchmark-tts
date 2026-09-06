#!/usr/bin/env python3
"""Adaptateur de génération — XTTS-v2 (Coqui).

⚠️ Licence **CPML — non commerciale**. Inclus comme *référence qualité*,
pas comme candidat produit.

Paquet `coqui-tts` (fork communautaire, Coqui a fermé) + `transformers`
4.57.x (la 5.x retire des symboles utilisés par le fork). Clonage
zero-shot depuis un WAV de référence (pas de transcription nécessaire).

    source env.sh
    COQUI_TOS_AGREED=1 uv run --python "$TTSB_VENVS/xtts_v2/bin/python" \
        models/xtts_v2/generer.py --reps 3 --voix papa_narration,johnny
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE))

from benchmark.chunking import FAMILLE_DEFAUT  # noqa: E402
from benchmark.corpus import charger_corpus  # noqa: E402
from benchmark.generation import executer_corpus, parser_voix_phrases  # noqa: E402

NOM_MODELE = "xtts_v2"
REPO_ID = "coqui/XTTS-v2"
REVISION = "6c2b0d75eae4b7047358e3b6bd9325f857d43f77"
SR_MODELE = 24_000


def _chemin_poids() -> str:
    snap = Path(os.environ["HF_HUB_CACHE"]) / "models--coqui--XTTS-v2" / "snapshots" / REVISION
    if not snap.is_dir():
        sys.exit(f"[FAIL] poids absents : {snap}\n  python3 benchmark/fetch_models.py --model xtts_v2")
    return str(snap)


def _charger_modele(device: str):
    os.environ.setdefault("COQUI_TOS_AGREED", "1")
    from TTS.api import TTS

    d = _chemin_poids()
    tts = TTS(model_path=d, config_path=f"{d}/config.json", progress_bar=False)
    return tts.to(device)


def _faire_synthetiser(tts):
    def _synth(texte: str, _categorie: str, ref_wav: str, _seed: int = 0) -> np.ndarray:
        wav = tts.tts(text=texte, speaker_wav=ref_wav, language="fr")
        return np.asarray(wav, dtype=np.float32)
    return _synth


def _non_applicable(ph) -> str | None:
    if ph.est_multi_voix:
        return "multi_voix non géré (une voix de référence par appel)"
    return None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--voix", default="papa_narration,johnny")
    p.add_argument("--voix-phrases", default="")
    p.add_argument("--base-seed", type=int, default=1000)
    p.add_argument("--phrases", default="")
    p.add_argument("--limite", type=int, default=0)
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    pxv = parser_voix_phrases(args.voix_phrases)
    voix_list = list(pxv) if pxv else [v.strip() for v in args.voix.split(",") if v.strip()]
    refs = {v: str(RACINE / "corpus" / "voix_reference" / f"{v}.wav") for v in voix_list}
    for v, chemin in refs.items():
        if not Path(chemin).is_file():
            sys.exit(f"[FAIL] voix de référence absente : {chemin}")

    phrases = charger_corpus()
    if args.phrases:
        garde = set(args.phrases.split(","))
        phrases = [ph for ph in phrases if ph.id in garde]
    if args.limite:
        phrases = phrases[: args.limite]

    racine_sortie = Path(os.environ.get("TTSB_AUDIO_OUT", RACINE / "audio_genere")) / NOM_MODELE

    print(f"[{NOM_MODELE}] chargement ({REPO_ID} @ {REVISION[:8]})…", flush=True)
    t0 = time.perf_counter()
    tts = _charger_modele(args.device)
    synth = _faire_synthetiser(tts)
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t0:.1f} s", flush=True)

    try:
        synth("Bonjour, ceci est un test de préchauffage.", "narration", next(iter(refs.values())))
        print(f"[{NOM_MODELE}] warm-up ok", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[{NOM_MODELE}] warm-up ignoré : {e}", flush=True)

    total_ok = executer_corpus(
        nom_modele=NOM_MODELE,
        synthetiser=synth,
        sr_modele=SR_MODELE,
        phrases=phrases,
        voix_refs=refs,
        reps=args.reps,
        base_seed=args.base_seed,
        racine_sortie=racine_sortie,
        params_chunk=FAMILLE_DEFAUT,
        phrases_par_voix=pxv or None,
        meta_base={
            "repo_id": REPO_ID, "revision": REVISION,
            "licence": "CPML (non commercial)",
            "params": {"language": "fr", "clonage": True, "usage_commercial": False},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
