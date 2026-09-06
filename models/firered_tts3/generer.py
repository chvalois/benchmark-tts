#!/usr/bin/env python3
"""Adaptateur de génération — FireRedTTS3 (base, clonage zero-shot).

Pas de paquet PyPI : code depuis le dépôt GitHub épinglé (comme avisol
pour Chatterbox), via PYTHONPATH. Le dépôt fournit `fireredtts3.core`.

    source env.sh
    uv run --python "$TTSB_VENVS/firered_tts3/bin/python" \
        models/firered_tts3/generer.py --reps 3 --voix papa_narration,johnny

API (fireredtts3/core.py) :
    tts = FireRedTTS3(<dir poids>, use_wetext=True, use_llm_tn=False)
    gen, sr = tts.generate(language="French", prompt_text=..., prompt_audio=<tensor>,
                           prompt_audio_sr=..., text=..., do_tn=True)
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

NOM_MODELE = "firered_tts3"
REPO_ID = "FireRedTeam/FireRedTTS3"
REVISION = "dcf1bdcd1b8b25b382fa84c3e34eb82e3054a610"        # poids HF
CODE_REF = "FireRedTeam/FireRedTTS3@1d32ba780da6af37a71bdfd9c68c12003e908a46"
LANGUE_FIRERED = "French"


def _chemin_poids() -> str:
    cache = os.environ["HF_HUB_CACHE"]
    snap = Path(cache) / "models--FireRedTeam--FireRedTTS3" / "snapshots" / REVISION
    if not snap.is_dir():
        sys.exit(f"[FAIL] poids absents : {snap}\n  python3 benchmark/fetch_models.py --model firered_tts3")
    return str(snap)


def _chemin_source() -> str:
    src = Path(os.environ["TTSB_ROOT"]) / "src" / "firered_tts3"
    if not (src / "fireredtts3" / "core.py").is_file():
        sys.exit(f"[FAIL] source FireRed absente : {src}\n"
                 f"  git clone https://github.com/FireRedTeam/FireRedTTS3 {src} "
                 f"&& (cd {src} && git checkout {CODE_REF.split('@')[1]})")
    return str(src)


def _charger_modele(device: str):
    sys.path.insert(0, _chemin_source())
    from fireredtts3.core import FireRedTTS3

    tts = FireRedTTS3(_chemin_poids(), use_wetext=True, use_llm_tn=False)
    if hasattr(tts, "to"):
        tts.to(device)
    return tts


def _charger_ref(voix: str):
    import torchaudio

    d = RACINE / "corpus" / "voix_reference"
    wav, sr = torchaudio.load(str(d / f"{voix}.wav"))
    prompt_txt = (d / f"{voix}.prompt.txt").read_text(encoding="utf-8").strip()
    if not prompt_txt:
        sys.exit(f"[FAIL] transcription de référence vide : {voix}.prompt.txt")
    return (prompt_txt, wav, int(sr))


def _synthetiser_brut(tts, texte: str, ref, seed: int = 1234) -> tuple[np.ndarray, int]:
    prompt_text, prompt_audio, prompt_sr = ref
    gen, gen_sr = tts.generate(
        text=texte,
        language=LANGUE_FIRERED,
        prompt_text=prompt_text,
        prompt_audio=prompt_audio,
        prompt_audio_sr=prompt_sr,
        seed=seed,          # FireRed a sa propre graine (défaut 1234) -> reps sinon identiques
        do_tn=True,
    )
    return gen.detach().float().cpu().numpy(), int(gen_sr)


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
    p.add_argument("--limite", type=int, default=0)
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    pxv = parser_voix_phrases(args.voix_phrases)
    voix_list = list(pxv) if pxv else [v.strip() for v in args.voix.split(",") if v.strip()]
    phrases = charger_corpus()
    if args.phrases:
        garde = set(args.phrases.split(","))
        phrases = [ph for ph in phrases if ph.id in garde]
    if args.limite:
        phrases = phrases[: args.limite]

    racine_sortie = Path(os.environ.get("TTSB_AUDIO_OUT", RACINE / "audio_genere")) / NOM_MODELE

    print(f"[{NOM_MODELE}] chargement (poids {REVISION[:8]}, code {CODE_REF.split('@')[1][:8]})…", flush=True)
    t0 = time.perf_counter()
    tts = _charger_modele(args.device)
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t0:.1f} s", flush=True)

    refs = {v: _charger_ref(v) for v in voix_list}

    # warm-up : cale aussi le SR réel de sortie du modèle
    sr_modele = 24_000
    try:
        _a, sr_modele = _synthetiser_brut(tts, "Bonjour, ceci est un test de préchauffage.", next(iter(refs.values())))
        print(f"[{NOM_MODELE}] warm-up ok, sr={sr_modele}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[{NOM_MODELE}] warm-up ignoré : {e}", flush=True)

    def synth(texte, _categorie, ref, seed):
        arr, _sr = _synthetiser_brut(tts, texte, ref, seed)
        return arr

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
            "params": {"language": LANGUE_FIRERED, "use_wetext": True,
                       "use_llm_tn": False, "do_tn": True, "clonage": True},
            "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        },
        est_non_applicable=_non_applicable,
    )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
