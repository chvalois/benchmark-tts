#!/usr/bin/env python3
"""Adaptateur de génération — Chatterbox V3 Multilingual (baseline).

Respecte benchmark/CONTRAT_MODELE.md : lit le corpus + la voix partagés,
applique le pré-traitement commun, découpe (famille Chatterbox), génère
N répétitions, écrit `<id>_<rep>.wav` (24 kHz mono) + `timings.csv` +
`meta.json` dans `$TTSB_AUDIO_OUT/chatterbox_v3/`.

Seule partie propre au modèle : `_charger_modele()` / `_synthetiser()`.
Tout le reste vient de `benchmark/`.

    source env.sh
    uv run --python "$TTSB_VENVS/chatterbox_v3/bin/python" \
        models/chatterbox_v3/generer.py --reps 5 --voix vf_moyen

API modèle (retour d'expérience avisol, à revalider au 1er run réel) :
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    m = ChatterboxMultilingualTTS.from_pretrained(device="cuda", t3_model="v3")
    wav = m.generate(texte, language_id="fr", audio_prompt_path=ref,
                     exaggeration=0.3|0.9, cfg_weight=1.0)   # -> tensor (1, N)
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE))

from benchmark.chunking import FAMILLE_CHATTERBOX, categorie_globale, decouper  # noqa: E402
from benchmark.corpus import Phrase, charger_corpus  # noqa: E402
from benchmark.generation import (  # noqa: E402
    ecrire_meta,
    ecrire_timings,
    ecrire_wav,
    fixer_seed,
    parser_voix_phrases,
    preparer_audio,
    silence,
)
from benchmark.pretraitement import pretraiter  # noqa: E402
from benchmark.vram import PicVRAM  # noqa: E402

NOM_MODELE = "chatterbox_v3"
REPO_ID = "ResembleAI/chatterbox"
REVISION = "5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18"          # poids HF
CODE_REF = "resemble-ai/chatterbox@5de7a54aa4e5e2baadb0182dde554908b48b85c2"  # source (support t3_model=v3)
T3_MODEL = "v3"                                                 # checkpoint T3 sélectionné

# exaggeration dynamique (avisol) : posé en narration, vif en dialogue.
EXAG_NARRATION = 0.3
EXAG_DIALOGUE = 0.9
EXAG_REPLIQUE_COURTE = 0.5
CFG_WEIGHT = 0.5   # défaut modèle (chatterbox-tts 0.1.7)


# ---------------------------------------------------------------- modèle
def _charger_modele(device: str = "cuda"):
    # Source GitHub épinglée (CODE_REF) : from_pretrained accepte t3_model="v3"
    # -> charge t3_mtl23ls_v3.safetensors (parité avec la prod avisol).
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    modele = ChatterboxMultilingualTTS.from_pretrained(device=device, t3_model=T3_MODEL)
    return modele, int(modele.sr)


def _exag(categorie: str) -> float:
    return {
        "narration": EXAG_NARRATION,
        "dialogue": EXAG_DIALOGUE,
        "replique_courte": EXAG_REPLIQUE_COURTE,
    }.get(categorie, EXAG_NARRATION)


def _synthetiser(modele, texte: str, categorie: str, ref_wav: str) -> np.ndarray:
    wav = modele.generate(
        texte,
        language_id="fr",
        audio_prompt_path=ref_wav,
        exaggeration=_exag(categorie),
        cfg_weight=CFG_WEIGHT,
    )
    return wav.detach().float().cpu().numpy()


# ------------------------------------------------------------- pipeline
def _texte_pour_modele(phrase: Phrase) -> tuple[str | None, str]:
    """Retourne (texte, motif_na). texte=None si l'item est hors capacité
    de Chatterbox avec une voix de référence unique (multi_voix)."""
    if phrase.est_multi_voix:
        return None, "multi_voix non supporté avec une voix de référence unique"
    return pretraiter(phrase.texte, est_titre=phrase.est_titre), ""


def _generer_une(
    modele, sr_modele: int, phrase: Phrase, ref_wav: str
) -> tuple[np.ndarray, str, float, float]:
    texte, _ = _texte_pour_modele(phrase)
    chunks = decouper(texte, FAMILLE_CHATTERBOX)
    morceaux: list[np.ndarray] = []
    t0 = time.perf_counter()
    ttfa = 0.0
    for i, ch in enumerate(chunks):
        brut = _synthetiser(modele, ch.texte, ch.categorie, ref_wav)
        if i == 0:
            ttfa = time.perf_counter() - t0
        morceaux.append(preparer_audio(brut, sr_modele))
        if ch.silence_apres_ms:
            morceaux.append(silence(ch.silence_apres_ms))
    gen_s = time.perf_counter() - t0
    audio = np.concatenate(morceaux) if morceaux else np.zeros(0, dtype=np.float32)
    return audio, categorie_globale(chunks), ttfa, gen_s


def _generer_voix(modele, sr_modele: int, phrases, voix: str, ref_wav: str,
                  reps: int, base_seed: int, racine_sortie: Path,
                  garde_ids: set | None = None) -> int:
    """Génère le corpus (ou le sous-ensemble `garde_ids`) pour UNE voix
    -> `<racine_sortie>/<voix>/`."""
    sortie = racine_sortie / voix
    lignes: list[dict] = []
    for ph in phrases:
        if garde_ids is not None and ph.id not in garde_ids:
            continue
        texte, motif_na = _texte_pour_modele(ph)
        if texte is None:
            for rep in range(1, reps + 1):
                lignes.append({"id_phrase": ph.id, "repetition": rep, "statut": f"n/a:{motif_na}"})
            print(f"[{NOM_MODELE}/{voix}] {ph.id} -> n/a ({motif_na})", flush=True)
            continue
        for rep in range(1, reps + 1):
            seed = base_seed + rep
            fixer_seed(seed)
            try:
                with PicVRAM() as pic:
                    audio, cat, ttfa, gen_s = _generer_une(modele, sr_modele, ph, ref_wav)
                audio_s = ecrire_wav(sortie / f"{ph.id}_{rep}.wav", audio)
                statut = "ok"
            except Exception as e:  # noqa: BLE001 — on journalise, on continue le corpus
                cat, ttfa, gen_s, audio_s = "inconnu", 0.0, 0.0, 0.0
                pic = PicVRAM()
                statut = f"echec:{type(e).__name__}"
                print(f"[{NOM_MODELE}/{voix}] {ph.id} rep {rep} -> {statut}: {e}", flush=True)
            lignes.append({
                "id_phrase": ph.id, "repetition": rep, "seed": seed,
                "ttfa_s": round(ttfa, 4), "gen_s": round(gen_s, 4),
                "audio_s": round(audio_s, 4), "vram_pic_mo": pic.pic_mo or "",
                "categorie_chunk": cat, "statut": statut,
            })

    ecrire_timings(sortie / "timings.csv", lignes)
    ecrire_meta(sortie / "meta.json", {
        "modele": NOM_MODELE,
        "repo_id": REPO_ID,
        "revision": REVISION,
        "code_ref": CODE_REF,
        "t3_model": T3_MODEL,
        "voix": voix,
        "base_seed": base_seed,
        "reps": reps,
        "params": {
            "language_id": "fr", "cfg_weight": CFG_WEIGHT,
            "exaggeration": {"narration": EXAG_NARRATION, "dialogue": EXAG_DIALOGUE,
                             "replique_courte": EXAG_REPLIQUE_COURTE},
            "chunker": "FAMILLE_CHATTERBOX",
        },
        "commit_benchmark": os.environ.get("TTSB_COMMIT", ""),
        "date_run": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    n_ok = sum(1 for x in lignes if x["statut"] == "ok")
    print(f"[{NOM_MODELE}/{voix}] terminé : {n_ok}/{len(lignes)} runs ok -> {sortie}", flush=True)
    return n_ok


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reps", type=int, default=5)
    p.add_argument("--voix", default="vf_moyen", help="id(s) dans corpus/voix_reference/, séparés par des virgules")
    p.add_argument("--voix-phrases", default="", help="'papa_joie:p01,p06;papa_colere:p02,...' — restreint les phrases par voix")
    p.add_argument("--base-seed", type=int, default=1000)
    p.add_argument("--phrases", default="", help="filtre : p01,p07 (défaut : tout le corpus)")
    p.add_argument("--limite", type=int, default=0, help="n'traiter que les N premières phrases (smoke test)")
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    racine_sortie = Path(os.environ.get("TTSB_AUDIO_OUT", RACINE / "audio_genere")) / NOM_MODELE
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

    print(f"[{NOM_MODELE}] chargement (poids {REVISION[:8]}, code {CODE_REF.split('@')[1][:8]}, t3={T3_MODEL})…", flush=True)
    t_cold = time.perf_counter()
    modele, sr_modele = _charger_modele(args.device)
    print(f"[{NOM_MODELE}] cold start {time.perf_counter() - t_cold:.1f} s, sr={sr_modele}", flush=True)

    # Warm-up NON chronométré : le 1er appel compile les kernels CUDA (~15 s).
    t_warm = time.perf_counter()
    try:
        _synthetiser(modele, "Bonjour, ceci est un test de préchauffage.", "narration", refs[voix_list[0]])
        print(f"[{NOM_MODELE}] warm-up {time.perf_counter() - t_warm:.1f} s", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[{NOM_MODELE}] warm-up ignoré : {e}", flush=True)

    total_ok = 0
    for voix in voix_list:
        total_ok += _generer_voix(
            modele, sr_modele, phrases, voix, refs[voix],
            args.reps, args.base_seed, racine_sortie,
            garde_ids=set(pxv[voix]) if voix in pxv else None,
        )
    print(f"[{NOM_MODELE}] TOUT terminé : {total_ok} runs ok sur {len(voix_list)} voix", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
