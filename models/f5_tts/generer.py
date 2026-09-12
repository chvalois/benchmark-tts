#!/usr/bin/env python3
"""Adaptateur de génération — F5-TTS (flow-matching).

⚠️ Licence **CC-BY-NC — non commerciale**. Inclus comme *référence
prosodie/qualité*, pas comme candidat produit.

Paquet `f5-tts`. Clonage zero-shot : WAV de référence **+ sa
transcription** (`corpus/voix_reference/<voix>.prompt.txt`).

    source env.sh
    uv run --python "$TTSB_VENVS/f5_tts/bin/python" \
        models/f5_tts/generer.py --reps 3 --voix papa_narration,johnny
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

NOM_MODELE = "f5_tts"
REPO_ID = "SWivid/F5-TTS"
REVISION = "84e5a410d9cead4de2f847e7c9369a6440bdfaca"
F5_MODEL = "F5TTS_v1_Base"
NFE_STEP = 32
CFG_STRENGTH = 2.0


def _charger_modele(device: str):
    from f5_tts.api import F5TTS

    return F5TTS(model=F5_MODEL, device=device, hf_cache_dir=os.environ.get("HF_HUB_CACHE"))


def _charger_ref(voix: str):
    # F5 clippe la référence à ~12 s en interne : passer un WAV de 27 s +
    # sa transcription complète crée un décalage texte/audio -> sortie
    # catastrophique (WER > 100 %). On fournit un clip 12 s dédié F5
    # (`<voix>.f5.wav`) + sa transcription (`<voix>.f5.prompt.txt`).
    d = RACINE / "corpus" / "voix_reference"
    wav, prompt = d / f"{voix}.f5.wav", d / f"{voix}.f5.prompt.txt"
    if not wav.is_file() or not prompt.is_file():
        sys.exit(f"[FAIL] clip F5 manquant pour {voix} ({wav.name} / {prompt.name})")
    return (str(wav), prompt.read_text(encoding="utf-8").strip())


def _faire_synthetiser(f5):
    def _synth(texte: str, _categorie: str, ref, seed: int) -> np.ndarray:
        ref_wav, ref_text = ref
        wav, _sr, _spec = f5.infer(
            ref_file=ref_wav, ref_text=ref_text, gen_text=texte,
            nfe_step=NFE_STEP, cfg_strength=CFG_STRENGTH, speed=1.0, seed=seed,
            show_info=lambda *a, **k: None,
        )
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
    p.add_argument("--corpus", choices=("v1", "longform"), default="v1",
                   help="v1 = corpus/phrases.yaml (défaut) ; longform = corpus/longform.yaml (v2)")
    p.add_argument("--limite", type=int, default=0)
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    pxv = parser_voix_phrases(args.voix_phrases)
    voix_list = list(pxv) if pxv else [v.strip() for v in args.voix.split(",") if v.strip()]
    refs = {v: _charger_ref(v) for v in voix_list}

    phrases = charger_longform() if args.corpus == "longform" else charger_corpus()
    if args.phrases:
        garde = set(args.phrases.split(","))
        phrases = [ph for ph in phrases if ph.id in garde]
    if args.limite:
        phrases = phrases[: args.limite]

    racine_sortie = Path(os.environ.get("TTSB_AUDIO_OUT", RACINE / "audio_genere")) / NOM_MODELE
    if args.corpus == "longform":
        racine_sortie = racine_sortie / "longform"

    print(f"[{NOM_MODELE}] chargement ({REPO_ID} @ {REVISION[:8]}, {F5_MODEL})…", flush=True)
    t0 = time.perf_counter()
    f5 = _charger_modele(args.device)
    synth = _faire_synthetiser(f5)
    sr_modele = int(getattr(f5, "target_sample_rate", 24_000))
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t0:.1f} s, sr={sr_modele}", flush=True)

    try:
        synth("Bonjour, ceci est un test de préchauffage.", "narration", next(iter(refs.values())), 0)
        print(f"[{NOM_MODELE}] warm-up ok", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[{NOM_MODELE}] warm-up ignoré : {e}", flush=True)

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
            "licence": "CC-BY-NC (non commercial)",
            "params": {"model": F5_MODEL, "nfe_step": NFE_STEP, "cfg_strength": CFG_STRENGTH,
                       "clonage": True, "usage_commercial": False},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
