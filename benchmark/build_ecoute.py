#!/usr/bin/env python3
"""Génère le test d'écoute local `site/ecoute/`.

- sélectionne des phrases (celles flaggées par les métriques objectives +
  un échantillon de phrases propres) ;
- construit les paires A/B (le meilleur WER `CHAMPION` vs chaque autre
  modèle + quelques paires aléatoires) et les clips MOS (phrases × tous
  les modèles) ;
- copie les WAV concernés dans `site/ecoute/audio/` sous des noms
  anonymes (`c0001.wav`) — le mapping clip→modèle va dans
  `_solution.json`, **jamais chargé par la page** ;
- écrit `manifest.js` (données de la page, sans nom de modèle).

    source env.sh
    python3 benchmark/build_ecoute.py
"""
from __future__ import annotations

import json
import random
import shutil
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
CORPUS = RACINE / "corpus" / "phrases.yaml"
RESULTATS = RACINE / "resultats"
SORTIE = RACINE / "site" / "ecoute"
AUDIO_SRC = Path("/mnt/d/tts-benchmark-data/audio_genere")  # $TTSB_AUDIO_OUT

MODELES = ["firered_tts3", "voxcpm2", "chatterbox_v3", "cosyvoice3_05b",
           "xtts_v2", "kokoro_82m", "moss_tts_local_v15"]
# Les deux "têtes" : comparées à tout le monde + l'une à l'autre sur chaque
# phrase. VoxCPM2 en tête aussi (moins lourd que FireRed, intérêt fort).
TETES = ["voxcpm2", "firered_tts3"]
VOIX = "papa_narration"
VOIX_KOKORO = "ff_siwis"           # Kokoro : pas de clonage
REF_WAV = RACINE / "corpus" / "voix_reference" / f"{VOIX}.wav"
REP = 1
SEED = 20260906

N_PHRASES_AB = 8          # ~6 paires / phrase  ≈ 48 + aléas
N_PAIRES_ALEA = 8         # paires entièrement aléatoires (calibration)
N_PHRASES_MOS = 6         # x 7 modèles = 42 clips

DEFAUTS = [
    {"k": "tronque", "label": "coupé / tronqué"},
    {"k": "repetition", "label": "répétition / bégaiement"},
    {"k": "voix_diff", "label": "voix ne ressemble pas"},
    {"k": "accent", "label": "accent / prononciation FR"},
    {"k": "artefact", "label": "artefact / bruit / robotique"},
]
AXES_MOS = [
    {"k": "naturel", "label": "Naturel"},
    {"k": "intelligibilite", "label": "Intelligibilité"},
    {"k": "similarite", "label": "Similarité à la voix de réf"},
    {"k": "expressivite", "label": "Expressivité / registre"},
]


def _voix_de(modele: str) -> str:
    return VOIX_KOKORO if modele == "kokoro_82m" else VOIX


def _wav(modele: str, phrase: str) -> Path:
    return AUDIO_SRC / modele / _voix_de(modele) / f"{phrase}_{REP}.wav"


def _charger_selection() -> tuple[list[str], list[str]]:
    """(phrases_ab, phrases_mos) — flaggées d'abord, complétées au hasard."""
    corpus = yaml.safe_load(CORPUS.read_text(encoding="utf-8"))
    exclues = {pid for pid, v in corpus.items() if v.get("type") == "multi_voix"}
    toutes = [pid for pid in corpus if pid not in exclues]

    flaggees: set[str] = set()
    wer_max: dict[str, float] = {pid: 0.0 for pid in toutes}
    for m in MODELES:
        f = RESULTATS / f"{m}.json"
        if not f.is_file():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        r = data.get(_voix_de(m)) or next(iter(data.values()))
        s = r["synthese"]
        for cle in ("phrases_hallucination", "phrases_repetition", "phrases_troncature"):
            flaggees.update(s.get(cle, []))
        for pid, x in r["stabilite"]["par_phrase"].items():
            if x["suspect"]:
                flaggees.add(pid)
        for ligne in r["lignes"]:
            wer_max[ligne["id_phrase"]] = max(wer_max[ligne["id_phrase"]], ligne["wer"])
    flaggees.update(pid for pid, w in wer_max.items() if w >= 0.30)
    flaggees &= set(toutes)

    rnd = random.Random(SEED)
    propres = [pid for pid in toutes if pid not in flaggees]
    rnd.shuffle(propres)
    flag_l = sorted(flaggees)
    rnd.shuffle(flag_l)

    def _prendre(n: int) -> list[str]:
        pool = flag_l[: max(1, n // 2)] + propres[: n - max(1, n // 2)]
        return sorted(set(pool), key=lambda p: int(p[1:]))[:n]

    return _prendre(N_PHRASES_AB), _prendre(N_PHRASES_MOS)


def build() -> None:
    audio_dir = SORTIE / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    for old in audio_dir.glob("*.wav"):
        old.unlink()

    rnd = random.Random(SEED)
    phrases_ab, phrases_mos = _charger_selection()

    clips: dict[tuple[str, str], str] = {}
    solution_clips: dict[str, dict] = {}

    def clip_id(modele: str, phrase: str) -> str:
        key = (modele, phrase)
        if key not in clips:
            src = _wav(modele, phrase)
            if not src.is_file():
                raise SystemExit(f"[FAIL] audio manquant : {src}")
            cid = f"c{len(clips) + 1:04d}"
            shutil.copy2(src, audio_dir / f"{cid}.wav")
            clips[key] = cid
            solution_clips[cid] = {"modele": modele, "phrase": phrase, "rep": REP,
                                   "voix": _voix_de(modele)}
        return clips[key]

    corpus = yaml.safe_load(CORPUS.read_text(encoding="utf-8"))

    # --- paires A/B : pas de champion unique -------------------------
    # Chaque phrase : le duel des 2 têtes + chaque tête vs 2 challengers
    # (décalés par phrase → couvre les 5) + 1 duel challenger-vs-challenger.
    challengers = [m for m in MODELES if m not in TETES]
    vus: set[tuple[str, str, str]] = set()
    paires: list[dict] = []

    def _ajouter(phrase: str, a: str, b: str) -> None:
        if a == b:
            return
        cle = (phrase, *sorted((a, b)))
        if cle in vus:
            return
        vus.add(cle)
        paires.append({"phrase": phrase, "m1": a, "m2": b})

    for i, phrase in enumerate(phrases_ab):
        _ajouter(phrase, TETES[0], TETES[1])
        for j, tete in enumerate(TETES):
            for off in (0, 1):
                _ajouter(phrase, tete, challengers[(2 * i + j + off) % len(challengers)])
        _ajouter(phrase, challengers[i % len(challengers)],
                 challengers[(i + 2) % len(challengers)])

    for _ in range(N_PAIRES_ALEA * 3):
        if sum(1 for p in paires if {p["m1"], p["m2"]} & set(TETES) == set()) >= N_PAIRES_ALEA:
            break
        phrase = rnd.choice(phrases_ab)
        a, b = rnd.sample(MODELES, 2)
        _ajouter(phrase, a, b)

    rnd.shuffle(paires)

    ab: list[dict] = []
    solution_ab: dict[str, dict] = {}
    for i, pr in enumerate(paires, 1):
        m_a, m_b = (pr["m1"], pr["m2"]) if rnd.random() < 0.5 else (pr["m2"], pr["m1"])
        aid = f"ab{i:03d}"
        ab.append({
            "id": aid, "phrase": pr["phrase"],
            "texte": corpus[pr["phrase"]]["texte"].strip().replace("\n", " "),
            "registre": corpus[pr["phrase"]]["registre"],
            "A": f"audio/{clip_id(m_a, pr['phrase'])}.wav",
            "B": f"audio/{clip_id(m_b, pr['phrase'])}.wav",
        })
        solution_ab[aid] = {"phrase": pr["phrase"], "A_modele": m_a, "B_modele": m_b}

    # --- clips MOS ---
    mos: list[dict] = []
    solution_mos: dict[str, dict] = {}
    k = 1
    for phrase in phrases_mos:
        for m in MODELES:
            mid = f"mos{k:03d}"
            k += 1
            mos.append({
                "id": mid, "phrase": phrase,
                "texte": corpus[phrase]["texte"].strip().replace("\n", " "),
                "registre": corpus[phrase]["registre"],
                "clip": f"audio/{clip_id(m, phrase)}.wav",
            })
            solution_mos[mid] = {"phrase": phrase, "modele": m}
    rnd.shuffle(mos)

    shutil.copy2(REF_WAV, audio_dir / "ref.wav")

    build_info = {"seed": SEED, "voix": VOIX, "tetes": TETES,
                  "modeles": MODELES, "rep": REP,
                  "phrases_ab": phrases_ab, "phrases_mos": phrases_mos}

    manifest = {
        # côté page : PAS de nom de modèle (test aveugle) — seulement une
        # signature de build pour tracer l'export.
        "build": {"seed": SEED, "voix": VOIX, "rep": REP,
                  "n_ab": len(ab), "n_mos": len(mos)},
        "ref": "audio/ref.wav",
        "defauts": DEFAUTS, "axes_mos": AXES_MOS,
        "ab": ab, "mos": mos,
    }
    (SORTIE / "manifest.js").write_text(
        "window.MANIFEST = " + json.dumps(manifest, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    (SORTIE / "_solution.json").write_text(
        json.dumps({"build": build_info, "clips": solution_clips,
                    "ab": solution_ab, "mos": solution_mos},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    mo = sum(f.stat().st_size for f in audio_dir.glob("*.wav")) / 1e6
    print(f"[build_ecoute] {len(ab)} paires A/B, {len(mos)} clips MOS, "
          f"{len(clips)+1} fichiers audio ({mo:.0f} Mo) -> {SORTIE}")
    print(f"[build_ecoute] ouvre  {SORTIE / 'index.html'}  (double-clic)")


if __name__ == "__main__":
    build()
