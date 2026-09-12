#!/usr/bin/env python3
"""Adaptateur de génération — Audio8-TTS-Preview-0.6b (Edge0, clonage zero-shot).

Interface HF standard `AutoModel`/`AutoProcessor` avec `trust_remote_code=True` :
le code custom (DualAR, codec 44,1 kHz) est EMBARQUÉ dans le snapshot HF
épinglé (pas de code_ref GitHub séparé — le dépôt GitHub Edge0-AI/Audio8_TTS,
ex-Audio8-AI, ne contient que démo/training).

    source env.sh
    uv run --no-project --python "$TTSB_VENVS/audio8_06b/bin/python" \
        models/audio8_06b/generer.py --reps 3 --voix papa_narration,johnny

`--no-project` est OBLIGATOIRE (voir models/omnivoice/generer.py pour le
détail : sans ce flag, `uv run` resynchronise le venv sur le pyproject.toml
racine — vide de dépendances — et casse l'environnement pip-installé).

API :
    processor = AutoProcessor.from_pretrained(<dir>, trust_remote_code=True)
    model = AutoModel.from_pretrained(<dir>, trust_remote_code=True, dtype=...).eval().to(device)
    inputs = processor(text=[...], reference_audio=[wav], reference_text=[transcript], return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=4096, temperature=0.8, top_p=0.95, top_k=50, do_sample=True,
                             return_dict_in_generate=True)
    waveforms, lengths = model.decode_audio(output.codes)   # 44,1 kHz
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

NOM_MODELE = "audio8_06b"
REPO_ID = "Audio8/Audio8-TTS-Preview-0.6b"
REVISION = "f07040f3d151f1ba0253bfb92cb2f5dd38b44594"
# Le quickstart du model card utilise max_new_tokens=1024 (exemple court) ;
# augmenté ici pour couvrir des chunks jusqu'à ~60 mots (MAX_WORDS_PER_CHUNK)
# sans troncature.
GEN_KWARGS = dict(max_new_tokens=4096, temperature=0.8, top_p=0.95, top_k=50, do_sample=True)


def _chemin_poids() -> str:
    cache = os.environ["HF_HUB_CACHE"]
    snap = Path(cache) / "models--Audio8--Audio8-TTS-Preview-0.6b" / "snapshots" / REVISION
    if not snap.is_dir():
        sys.exit(f"[FAIL] poids absents : {snap}\n  python3 benchmark/fetch_models.py --model audio8_06b")
    return str(snap)


def _charger_modele(device: str):
    import torch
    from transformers import AutoModel, AutoProcessor

    dtype = torch.bfloat16 if device.startswith("cuda") else torch.float32
    chemin = _chemin_poids()
    processor = AutoProcessor.from_pretrained(chemin, trust_remote_code=True)
    model = AutoModel.from_pretrained(chemin, trust_remote_code=True, dtype=dtype).eval().to(device)
    sr = int(model.config.codec_sample_rate)
    return processor, model, sr


def _charger_ref(voix: str):
    d = RACINE / "corpus" / "voix_reference"
    wav = d / f"{voix}.wav"
    prompt_txt = (d / f"{voix}.prompt.txt").read_text(encoding="utf-8").strip()
    if not wav.is_file() or not prompt_txt:
        sys.exit(f"[FAIL] référence incomplète pour {voix} (wav ou .prompt.txt)")
    return (prompt_txt, str(wav))


def _faire_synthetiser(processor, model, device: str):
    import torch

    def _synth(texte: str, _categorie: str, ref, _seed: int = 0) -> np.ndarray:
        prompt_text, wav_path = ref
        inputs = processor(
            text=[texte],
            reference_audio=[wav_path],
            reference_text=[prompt_text],
            return_tensors="pt",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.inference_mode():
            output = model.generate(**inputs, **GEN_KWARGS, return_dict_in_generate=True)
            waveforms, lengths = model.decode_audio(output.codes)
        wav = waveforms[0, : int(lengths[0])]
        return wav.float().cpu().numpy()

    return _synth


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

    print(f"[{NOM_MODELE}] chargement (poids {REVISION[:8]})…", flush=True)
    t0 = time.perf_counter()
    processor, model, sr_modele = _charger_modele(args.device)
    synth = _faire_synthetiser(processor, model, args.device)
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t0:.1f} s, sr={sr_modele}", flush=True)

    refs = {v: _charger_ref(v) for v in voix_list}
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
            "repo_id": REPO_ID, "revision": REVISION,
            "params": {**GEN_KWARGS, "clonage": True},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
