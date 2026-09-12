#!/usr/bin/env python3
"""Adaptateur de génération — VoxCPM2 (2B, clonage zero-shot, 48 kHz).

Paquet PyPI `voxcpm==2.0.3`. Clonage « Ultimate » : audio de référence +
sa transcription (`corpus/voix_reference/<voix>.prompt.txt`).

    source env.sh
    uv run --python "$TTSB_VENVS/voxcpm2/bin/python" \
        models/voxcpm2/generer.py --reps 3 --voix papa_narration,johnny

API (voxcpm) :
    model = VoxCPM.from_pretrained(<dir>, load_denoiser=False)
    wav = model.generate(text=..., prompt_wav_path=ref, prompt_text=...,
                         reference_wav_path=ref, cfg_value=2.0,
                         inference_timesteps=10, seed=<int>)   # -> np.ndarray, 48 kHz
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
from benchmark.corpus import charger_corpus, charger_longform  # noqa: E402
from benchmark.generation import executer_corpus, parser_voix_phrases  # noqa: E402

NOM_MODELE = "voxcpm2"
REPO_ID = "openbmb/VoxCPM2"
REVISION = "32279effe8c19989596f05d353d1447f51d9e915"
CFG_VALUE = 2.0
INFERENCE_TIMESTEPS = 10


def _chemin_poids() -> str:
    snap = Path(os.environ["HF_HUB_CACHE"]) / "models--openbmb--VoxCPM2" / "snapshots" / REVISION
    if not snap.is_dir():
        sys.exit(f"[FAIL] poids absents : {snap}\n  python3 benchmark/fetch_models.py --model voxcpm2")
    return str(snap)


def _charger_modele(_device: str):
    from voxcpm import VoxCPM

    return VoxCPM.from_pretrained(_chemin_poids(), load_denoiser=False)


def _charger_ref(voix: str):
    d = RACINE / "corpus" / "voix_reference"
    wav = d / f"{voix}.wav"
    prompt_txt = (d / f"{voix}.prompt.txt").read_text(encoding="utf-8").strip()
    if not wav.is_file() or not prompt_txt:
        sys.exit(f"[FAIL] référence incomplète pour {voix} (wav ou .prompt.txt)")
    return (prompt_txt, str(wav))


def _synthetiser_brut(model, texte: str, ref, _seed: int = 0) -> np.ndarray:
    # voxcpm 2.0.3 : _generate n'a pas de param `seed` -> la variance des reps
    # vient de la graine GLOBALE torch posée par executer_corpus (fixer_seed).
    prompt_text, wav_path = ref
    wav = model.generate(
        text=texte,
        prompt_wav_path=wav_path,
        prompt_text=prompt_text,
        reference_wav_path=wav_path,
        cfg_value=CFG_VALUE,
        inference_timesteps=INFERENCE_TIMESTEPS,
        normalize=False,
        retry_badcase=True,
    )
    return np.asarray(wav, dtype=np.float32)


def _non_applicable(ph) -> str | None:
    if ph.est_multi_voix:
        return "multi_voix non géré (une voix de référence par appel)"
    return None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--voix", default="papa_narration,johnny")
    p.add_argument("--voix-phrases", default="", help="'papa_joie:p01,p06;papa_colere:p02,...' — restreint les phrases par voix")
    p.add_argument("--base-seed", type=int, default=1000)
    p.add_argument("--phrases", default="")
    p.add_argument("--corpus", choices=("v1", "longform"), default="v1",
                   help="v1 = corpus/phrases.yaml (défaut) ; longform = corpus/longform.yaml (v2)")
    p.add_argument("--limite", type=int, default=0)
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    pxv = parser_voix_phrases(args.voix_phrases)
    voix_list = list(pxv) if pxv else [v.strip() for v in args.voix.split(",") if v.strip()]
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
    t0 = time.perf_counter()
    model = _charger_modele(args.device)
    sr_modele = int(getattr(getattr(model, "tts_model", model), "sample_rate", 48_000))
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t0:.1f} s, sr={sr_modele}", flush=True)

    refs = {v: _charger_ref(v) for v in voix_list}
    try:
        _synthetiser_brut(model, "Bonjour, ceci est un test de préchauffage.", next(iter(refs.values())), 0)
        print(f"[{NOM_MODELE}] warm-up ok", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[{NOM_MODELE}] warm-up ignoré : {e}", flush=True)

    def synth(texte, _categorie, ref, seed):
        return _synthetiser_brut(model, texte, ref, seed)

    total_ok = executer_corpus(
        nom_modele=NOM_MODELE,
        synthetiser=synth,
        sr_modele=sr_modele,
        phrases=phrases,
        voix_refs=refs,
        reps=args.reps,
        base_seed=args.base_seed,
        racine_sortie=racine_sortie,
        params_chunk=FAMILLE_DEFAUT,
        phrases_par_voix=pxv or None,
        meta_base={
            "repo_id": REPO_ID, "revision": REVISION,
            "params": {"cfg_value": CFG_VALUE, "inference_timesteps": INFERENCE_TIMESTEPS,
                       "cloning": "ultimate", "clonage": True},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
