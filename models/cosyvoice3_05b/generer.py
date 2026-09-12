#!/usr/bin/env python3
"""Adaptateur de génération — CosyVoice3 (Fun-CosyVoice3-0.5B-2512).

Pas de paquet PyPI complet : code depuis le dépôt GitHub `FunAudioLLM/
CosyVoice` (épinglé) + sous-module `Matcha-TTS`, via PYTHONPATH.
Clonage zero-shot : WAV de référence + sa transcription.

    source env.sh
    PYTHONPATH="$TTSB_ROOT/src/cosyvoice:$TTSB_ROOT/src/cosyvoice/third_party/Matcha-TTS" \
      uv run --python "$TTSB_VENVS/cosyvoice3_05b/bin/python" \
      models/cosyvoice3_05b/generer.py --reps 3 --voix papa_narration,johnny

API (model card) :
    from cosyvoice.cli.cosyvoice import AutoModel
    m = AutoModel(model_dir=<dir>)
    for j in m.inference_zero_shot(gen_text, prompt_text, prompt_wav, stream=False):
        audio = j['tts_speech']            # tensor [1, N] @ m.sample_rate
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
_SRC = Path(os.environ["TTSB_ROOT"]) / "src" / "cosyvoice"
sys.path.insert(0, str(_SRC))
sys.path.insert(0, str(_SRC / "third_party" / "Matcha-TTS"))

from benchmark.chunking import FAMILLE_DEFAUT  # noqa: E402
from benchmark.corpus import charger_corpus, charger_longform  # noqa: E402
from benchmark.generation import executer_corpus, parser_voix_phrases  # noqa: E402

NOM_MODELE = "cosyvoice3_05b"
REPO_ID = "FunAudioLLM/Fun-CosyVoice3-0.5B-2512"
REVISION = "29e01c4e8d000f4bcd70751be16fa94bf3d85a18"
CODE_REF = "FunAudioLLM/CosyVoice@074ca6d"
# CosyVoice3 exige le token <|endofprompt|> dans prompt_text (assert dans llm.py).
PREFIXE_INSTRUCT = "You are a helpful assistant.<|endofprompt|>"


def _chemin_poids() -> str:
    snap = Path(os.environ["HF_HUB_CACHE"]) / "models--FunAudioLLM--Fun-CosyVoice3-0.5B-2512" / "snapshots" / REVISION
    if not snap.is_dir():
        sys.exit(f"[FAIL] poids absents : {snap}\n  python3 benchmark/fetch_models.py --model cosyvoice3_05b")
    return str(snap)


def _charger_modele(_device: str):
    from cosyvoice.cli.cosyvoice import AutoModel

    return AutoModel(model_dir=_chemin_poids())


def _charger_ref(voix: str):
    # CosyVoice attend un CHEMIN de WAV 16 kHz + une transcription courte
    # (prompt trop long -> "too short than prompt text" + perf dégradée) :
    # clip 12 s dédié (`<voix>.16k.wav` / `<voix>.f5.prompt.txt`).
    d = RACINE / "corpus" / "voix_reference"
    wav, prompt = d / f"{voix}.16k.wav", d / f"{voix}.f5.prompt.txt"
    if not wav.is_file() or not prompt.is_file():
        sys.exit(f"[FAIL] clip 16k manquant pour {voix} ({wav.name} / {prompt.name})")
    return (str(wav), PREFIXE_INSTRUCT + prompt.read_text(encoding="utf-8").strip())


def _faire_synthetiser(model):
    def _synth(texte: str, _categorie: str, ref, _seed: int = 0) -> np.ndarray:
        ref_wav, ref_text = ref
        morceaux = []
        for j in model.inference_zero_shot(texte, ref_text, ref_wav, stream=False):
            morceaux.append(np.asarray(j["tts_speech"], dtype=np.float32).reshape(-1))
        return np.concatenate(morceaux) if morceaux else np.zeros(0, dtype=np.float32)
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

    print(f"[{NOM_MODELE}] chargement ({REPO_ID} @ {REVISION[:8]})…", flush=True)
    t0 = time.perf_counter()
    model = _charger_modele(args.device)
    synth = _faire_synthetiser(model)
    sr_modele = int(getattr(model, "sample_rate", 24_000))
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t0:.1f} s, sr={sr_modele}", flush=True)

    try:
        synth("Bonjour, ceci est un test de préchauffage.", "narration", next(iter(refs.values())))
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
            "repo_id": REPO_ID, "revision": REVISION, "code_ref": CODE_REF,
            "params": {"mode": "inference_zero_shot", "clonage": True},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
