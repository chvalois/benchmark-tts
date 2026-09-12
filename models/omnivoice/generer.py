#!/usr/bin/env python3
"""Adaptateur de génération — OmniVoice (k2-fsa, clonage zero-shot, 600+ langues).

Paquet PyPI `omnivoice==0.2.1`. `OmniVoice.from_pretrained()` accepte un
chemin local (pas besoin de code_ref GitHub). L'audio_tokenizer
(HiggsAudioV2) est déjà bundlé dans le snapshot HF épinglé.

    source env.sh
    uv run --no-project --python "$TTSB_VENVS/omnivoice/bin/python" \
        models/omnivoice/generer.py --reps 3 --voix papa_narration,johnny

`--no-project` est OBLIGATOIRE : le `pyproject.toml` racine du repo ne
déclare aucune dépendance, donc `uv run --python <venv>` sans ce flag
tente de synchroniser l'environnement sur ce projet vide et désinstalle
tout ce qui a été pip-installé manuellement dans le venv (ModuleNotFoundError
sur numpy et consorts).

API (omnivoice.models.omnivoice.OmniVoice) :
    model = OmniVoice.from_pretrained(<dir poids>, device_map="cuda:0", dtype=torch.float16)
    audio = model.generate(text=..., language="French", ref_text=..., ref_audio=<chemin wav>)
    # -> list[np.ndarray], 1 item, 24 kHz
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

NOM_MODELE = "omnivoice"
REPO_ID = "k2-fsa/OmniVoice"
REVISION = "c5fdb5ccb189668d56333f77ba2629f4cd7535f4"
LANGUE_OMNIVOICE = "French"


def _chemin_poids() -> str:
    cache = os.environ["HF_HUB_CACHE"]
    snap = Path(cache) / "models--k2-fsa--OmniVoice" / "snapshots" / REVISION
    if not snap.is_dir():
        sys.exit(f"[FAIL] poids absents : {snap}\n  python3 benchmark/fetch_models.py --model omnivoice")
    return str(snap)


def _charger_modele(device: str):
    import torch
    from omnivoice import OmniVoice

    dtype = torch.float16 if device.startswith("cuda") else torch.float32
    model = OmniVoice.from_pretrained(_chemin_poids(), device_map=device, dtype=dtype)
    return model


def _charger_ref(voix: str):
    d = RACINE / "corpus" / "voix_reference"
    wav = d / f"{voix}.wav"
    prompt_txt = (d / f"{voix}.prompt.txt").read_text(encoding="utf-8").strip()
    if not wav.is_file() or not prompt_txt:
        sys.exit(f"[FAIL] référence incomplète pour {voix} (wav ou .prompt.txt)")
    return (prompt_txt, str(wav))


def _synthetiser_brut(model, texte: str, ref) -> np.ndarray:
    prompt_text, wav_path = ref
    audio = model.generate(
        text=texte,
        language=LANGUE_OMNIVOICE,
        ref_text=prompt_text,
        ref_audio=wav_path,
    )
    return np.asarray(audio[0], dtype=np.float32)


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
    model = _charger_modele(args.device)
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t0:.1f} s", flush=True)

    refs = {v: _charger_ref(v) for v in voix_list}

    sr_modele = 24_000
    try:
        _a = _synthetiser_brut(model, "Bonjour, ceci est un test de préchauffage.", next(iter(refs.values())))
        print(f"[{NOM_MODELE}] warm-up ok", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[{NOM_MODELE}] warm-up ignoré : {e}", flush=True)

    def synth(texte, _categorie, ref, _seed):
        return _synthetiser_brut(model, texte, ref)

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
            "params": {"language": LANGUE_OMNIVOICE, "normalize_text": False, "clonage": True},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
