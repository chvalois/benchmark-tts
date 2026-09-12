#!/usr/bin/env python3
"""Adaptateur de génération — Kokoro-82M.

Kokoro **ne fait pas de clonage zero-shot** : il a un jeu fixe de voix
pré-entraînées. En français, une seule : `ff_siwis`. Ce n'est donc PAS
comparable voix-à-voix aux modèles clonants — mais le WER, la robustesse
et la vitesse le sont. Le rapport doit signaler `voix_interne=True`.

    source env.sh
    uv run --python "$TTSB_VENVS/kokoro_82m/bin/python" \
        models/kokoro_82m/generer.py --reps 3 --voix ff_siwis
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE))

from benchmark.chunking import FAMILLE_DEFAUT  # noqa: E402
from benchmark.corpus import charger_corpus, charger_longform  # noqa: E402
from benchmark.generation import executer_corpus  # noqa: E402

NOM_MODELE = "kokoro_82m"
REPO_ID = "hexgrad/Kokoro-82M"
REVISION = "f3ff3571791e39611d31c381e3a41a3af07b4987"
VOIX_FR = {"ff_siwis"}
SR_MODELE = 24_000


def _charger_modele(device: str):
    from kokoro import KPipeline

    return KPipeline(lang_code="f", repo_id=REPO_ID, device=device)


def _faire_synthetiser(pipe):
    def _synth(texte: str, _categorie: str, voix: str, _seed: int = 0) -> np.ndarray:
        segs = list(pipe(texte, voice=voix, speed=1))
        if not segs:
            return np.zeros(0, dtype=np.float32)
        return np.concatenate(
            [np.asarray(s.audio, dtype=np.float32) for s in segs]
        )
    return _synth


def _non_applicable(ph) -> str | None:
    if ph.est_multi_voix:
        return "multi_voix non géré (Kokoro : voix unique, pas de balise <voice:>)"
    return None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--voix", default="ff_siwis", help="voix Kokoro FR (seule : ff_siwis)")
    p.add_argument("--base-seed", type=int, default=1000)
    p.add_argument("--phrases", default="")
    p.add_argument("--corpus", choices=("v1", "longform"), default="v1",
                   help="v1 = corpus/phrases.yaml (défaut) ; longform = corpus/longform.yaml (v2)")
    p.add_argument("--limite", type=int, default=0)
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    voix_list = [v.strip() for v in args.voix.split(",") if v.strip()]
    inconnues = set(voix_list) - VOIX_FR
    if inconnues:
        sys.exit(f"[FAIL] voix Kokoro FR inconnue(s) : {sorted(inconnues)} (dispo : {sorted(VOIX_FR)})")

    phrases = charger_longform() if args.corpus == "longform" else charger_corpus()
    if args.phrases:
        garde = set(args.phrases.split(","))
        phrases = [ph for ph in phrases if ph.id in garde]
    if args.limite:
        phrases = phrases[: args.limite]

    racine_sortie = Path(os.environ.get("TTSB_AUDIO_OUT", RACINE / "audio_genere")) / NOM_MODELE
    if args.corpus == "longform":
        racine_sortie = racine_sortie / "longform"

    print(f"[{NOM_MODELE}] chargement ({REPO_ID} @ {REVISION[:8]})…", flush=True)
    import time
    t0 = time.perf_counter()
    pipe = _charger_modele(args.device)
    synth = _faire_synthetiser(pipe)
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t0:.1f} s", flush=True)
    try:
        synth("Bonjour, ceci est un test de préchauffage.", "narration", voix_list[0])
        print(f"[{NOM_MODELE}] warm-up ok", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[{NOM_MODELE}] warm-up ignoré : {e}", flush=True)

    total_ok = executer_corpus(
        nom_modele=NOM_MODELE,
        synthetiser=synth,
        sr_modele=SR_MODELE,
        phrases=phrases,
        voix_refs={v: v for v in voix_list},   # ref == id de voix interne
        reps=args.reps,
        base_seed=args.base_seed,
        racine_sortie=racine_sortie,
        params_chunk=FAMILLE_DEFAUT,
        meta_base={
            "repo_id": REPO_ID, "revision": REVISION,
            "params": {"lang_code": "f", "speed": 1, "voix_interne": True, "clonage": False},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
