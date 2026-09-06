#!/usr/bin/env python3
"""Adaptateur de génération — MOSS-TTS-Local-Transformer-v1.5 (5B).

Moteur de prod avisol. Interface HF standard `AutoModel`/`AutoProcessor`
avec `trust_remote_code=True`. Codec audio à 12,5 frames/s, sortie
**stéréo** `[canaux, samples]`.

Passe-1 = **défauts du model card** (audio_temperature=1.7, etc.) + balise
`<lang:fr>` + clonage zero-shot. PAS le handler avisol calibré (budget de
tokens `chars_per_second`, catégorisation, jeux de params par catégorie).
Réf. de fond : BENCHMARK_TTS_OPENSOURCE_FR_APIAVISOL.md §2.2, §3.6.

    source env.sh
    uv run --python "$TTSB_VENVS/moss_tts_local_v15/bin/python" \
        models/moss_tts_local_v15/generer.py --reps 3 --voix papa_narration,johnny
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
from benchmark.generation import executer_corpus  # noqa: E402

NOM_MODELE = "moss_tts_local_v15"
REPO_ID = "OpenMOSS-Team/MOSS-TTS-Local-Transformer-v1.5"
REVISION = "be7766a6735b98bd793f7c79fb720b4d0f5d13b8"
CODE_REF = "OpenMOSS/MOSS-TTS@fb6e6a5eae694e856c2ae78457682ea8ad79b44a"

# Défauts du model card (§3.6 : audio_repetition_penalty >= 1.0 impératif).
GEN_KWARGS = dict(
    max_new_tokens=4096,
    do_sample=True,
    audio_temperature=1.7,
    audio_top_p=0.8,
    audio_top_k=25,
    audio_repetition_penalty=1.0,
)


def _chemin_poids() -> str:
    snap = Path(os.environ["HF_HUB_CACHE"]) / "models--OpenMOSS-Team--MOSS-TTS-Local-Transformer-v1.5" / "snapshots" / REVISION
    if not snap.is_dir():
        sys.exit(f"[FAIL] poids absents : {snap}\n  python3 benchmark/fetch_models.py --model moss_tts_local_v15")
    return str(snap)


def _charger_modele(device: str):
    import torch
    from transformers import AutoModel, AutoProcessor

    torch.backends.cuda.enable_cudnn_sdp(False)  # backend cuDNN SDPA cassé sur certaines combos (model card)

    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    chemin = _chemin_poids()
    processor = AutoProcessor.from_pretrained(chemin, trust_remote_code=True)
    if hasattr(processor, "audio_tokenizer"):
        processor.audio_tokenizer = processor.audio_tokenizer.to(device)
    model = AutoModel.from_pretrained(
        chemin, trust_remote_code=True,
        attn_implementation="sdpa", dtype=dtype,
        device_map={"": device},
    )
    model.eval()
    sr = int(getattr(processor.model_config, "sampling_rate", 24_000))
    return processor, model, sr


def _faire_synthetiser(processor, model, device: str):
    import torch

    def _synth(texte: str, _categorie: str, ref_wav: str, _seed: int = 0) -> np.ndarray:
        conv = [processor.build_user_message(text=texte, reference=[ref_wav], language="French")]
        batch = processor([conv], mode="generation")
        with torch.no_grad():
            outputs = model.generate(
                input_ids=batch["input_ids"].to(device),
                attention_mask=batch["attention_mask"].to(device),
                **GEN_KWARGS,
            )
        for message in processor.decode(outputs):
            if message is None:
                continue
            audio = message.audio_codes_list[0]          # tensor [canaux, samples]
            return audio.float().cpu().numpy()           # preparer_audio -> 1D (garde canal 0)
        return np.zeros(0, dtype=np.float32)

    return _synth


def _non_applicable(ph) -> str | None:
    if ph.est_multi_voix:
        return "multi_voix non géré (un appel = une voix de référence ; <voice:> avisol hors passe-1)"
    return None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reps", type=int, default=3)
    p.add_argument("--voix", default="papa_narration,johnny")
    p.add_argument("--base-seed", type=int, default=1000)
    p.add_argument("--phrases", default="")
    p.add_argument("--limite", type=int, default=0)
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    voix_list = [v.strip() for v in args.voix.split(",") if v.strip()]
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

    print(f"[{NOM_MODELE}] chargement (poids {REVISION[:8]}, code {CODE_REF.split('@')[1][:8]})…", flush=True)
    t0 = time.perf_counter()
    processor, model, sr_modele = _charger_modele(args.device)
    synth = _faire_synthetiser(processor, model, args.device)
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
        meta_base={
            "repo_id": REPO_ID, "revision": REVISION, "code_ref": CODE_REF,
            "params": {**GEN_KWARGS, "language": "French", "chunker": "FAMILLE_DEFAUT",
                       "handler": "model_card_defaults (pas le handler avisol calibré)",
                       "clonage": True},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
