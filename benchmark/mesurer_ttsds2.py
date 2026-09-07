#!/usr/bin/env python3
"""Naturalité **principale** du benchmark : TTSDS2 (Text-to-Speech
Distribution Score v2, Minixhofer et al., SLT/ICLR).

Score **distributionnel** (pas par énoncé) : compare la distribution de la
parole générée d'un système `(modèle, voix)` à celle d'un corpus de
**vraie parole française de référence**, sur plusieurs espaces de
features — locuteur, intelligibilité, prosodie, features génériques. La
seule des 16 métriques comparées dans le papier à corréler > 0,5 avec le
MOS humain sur *tous* les domaines/langues testés.

- Corpus de réf FR : `$TTSB_ROOT/ttsds2_ref/fr/` (bâti par
  `benchmark/build_ref_ttsds2.py` depuis MLS-French — voir son `MANIFEST.json`).
- Composantes : **intelligibilité + prosodie + générique** (1/3 chacune).
  SPEAKER exclu (benchmark `wespeaker` de ttsds 2.1.3 cassé — cf.
  `requirements-ttsds2.txt` ; l'identité locuteur reste couverte par SIM
  ECAPA). ENVIRONMENT exclu (bruit de fond, hors sujet).
- Sortie : `<audio-dir>/ttsds2.json`
  `{"score_global", "par_composante": {...}, "ref", "n_gen", "n_ref"}`.
- L'agrégation (`rapport.py`) range ce JSON tel quel dans la synthèse.

Modèle-dépendant, deps lourdes et récentes (`transformers>=5`,
`openai-whisper`, `pyannote-audio`, `wespeaker`…) → venv **dédié**
`$TTSB_VENVS/_ttsds2`, jamais `_commun`. Seul `lire_ttsds2` est pur/testé.

    source env.sh
    uv run --python "$TTSB_VENVS/_ttsds2/bin/python" benchmark/mesurer_ttsds2.py \
        --audio-dir "$TTSB_AUDIO_OUT/firered_tts3/papa_narration"
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Composantes TTSDS2 retenues.
#  - Environment exclu : bruit de fond, hors sujet pour de la synthèse propre.
#  - Speaker exclu : le benchmark `wespeaker` de ttsds 2.1.3 est cassé
#    (pyannote-audio 3.4 passe `use_auth_token=` à un huggingface_hub>=1.0
#    qui l'a retiré ; forcer pyannote>=4 casse s3prl — cf. requirements-ttsds2.txt).
#    L'identité locuteur reste couverte par SIM (ECAPA, `mesurer_perceptuel.py`).
COMPOSANTES = ("intelligibility", "prosody", "generic")
_CLES_SPEAKER = ("wespeaker", "dvector")


def _ref_defaut() -> Path:
    racine = os.environ.get("TTSB_ROOT", str(RACINE))
    return Path(racine) / "ttsds2_ref" / "fr"


def lire_ttsds2(chemin: Path | str) -> dict | None:
    """Relit `<audio-dir>/ttsds2.json`. `None` si absent ou illisible
    (JSON corrompu, tronqué) — l'agrégation traite alors « pas de mesure »."""
    p = Path(chemin)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def ecrire_ttsds2(chemin: Path | str, data: dict) -> None:
    p = Path(chemin)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _lignes_agg(aggregated) -> list[dict]:
    """`suite.get_aggregated_results()` → liste de dicts-lignes.

    Forme observée (ttsds 2.1.3) : `pandas.DataFrame`, colonnes
    `benchmark_category` (PROSODY / INTELLIGIBILITY / GENERIC / **OVERALL**),
    `dataset`, `score_mean`, `score_std`, … — une ligne par catégorie
    + une ligne OVERALL par dataset."""
    if hasattr(aggregated, "to_dict"):
        return aggregated.to_dict("records")
    if isinstance(aggregated, list):
        return [r for r in aggregated if isinstance(r, dict)]
    if isinstance(aggregated, dict):
        return [{"benchmark_category": k, **v} if isinstance(v, dict) else {"benchmark_category": k, "score_mean": v}
                for k, v in aggregated.items()]
    return []


def _extraire_scores(aggregated, nom_dataset: str) -> tuple[float | None, dict]:
    """(score_global, {composante: score}) depuis `get_aggregated_results()`.

    `score_global` = ligne `OVERALL` ; sinon moyenne des composantes."""
    recs = _lignes_agg(aggregated)
    if nom_dataset and any("dataset" in r for r in recs):
        filtre = [r for r in recs if str(r.get("dataset", "")).strip() == nom_dataset]
        recs = filtre or recs

    par_composante: dict[str, float] = {}
    score_global: float | None = None
    for r in recs:
        cat = str(r.get("benchmark_category", r.get("category", ""))).strip().lower()
        val = r.get("score_mean", r.get("score", r.get("score_global")))
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            continue
        val = float(val)
        if cat == "overall":
            score_global = val
        elif cat in COMPOSANTES:
            par_composante[cat] = val

    if score_global is None and par_composante:
        score_global = sum(par_composante.values()) / len(par_composante)
    return score_global, {c: par_composante.get(c) for c in COMPOSANTES}


def _cache_dir_defaut() -> Path:
    racine = os.environ.get("TTSB_ROOT", str(RACINE))
    return Path(os.environ.get("TTSDS_CACHE_DIR") or Path(racine) / "ttsds-cache")


def _device_auto() -> str:
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:  # noqa: BLE001
        return "cpu"


def ttsds2_dossier(audio_dir: Path | str, ref_dir: Path | str,
                   *, multilingual: bool = True,
                   cache_dir: Path | str | None = None,
                   device: str | None = None, n_workers: int | None = None) -> dict:
    """Lance TTSDS2 : `audio_dir` (généré) vs `ref_dir` (vraie parole FR).

    Catégories SPEAKER et ENVIRONMENT exclues (poids 0) : le score porte sur
    intelligibilité + prosodie + générique (cf. `COMPOSANTES`).

    `device` : "cuda" par défaut si dispo (l'extraction whisper/wav2vec2/hubert
    sur CPU est prohibitivement lente). `n_workers` : parallélisme du calcul de
    distances (défaut 4 — `cpu_count()` sature la RAM sur ce poste)."""
    from ttsds import BenchmarkSuite
    from ttsds.benchmarks.benchmark import BenchmarkCategory
    from ttsds.ttsds import BENCHMARKS, BENCHMARKS_ML
    from ttsds.util.dataset import DirectoryDataset

    audio_dir, ref_dir = Path(audio_dir), Path(ref_dir)
    cache_dir = Path(cache_dir) if cache_dir else _cache_dir_defaut()
    cache_dir.mkdir(parents=True, exist_ok=True)
    device = device or _device_auto()
    gen_wavs = sorted(audio_dir.glob("*.wav"))
    ref_wavs = sorted(ref_dir.glob("*.wav"))
    if not gen_wavs:
        raise SystemExit(f"[FAIL] aucun .wav dans {audio_dir}")
    if not ref_wavs:
        raise SystemExit(f"[FAIL] corpus de réf vide : {ref_dir} "
                         f"(lancer benchmark/build_ref_ttsds2.py)")

    # On sélectionne nous-mêmes le dict (l'auto-swap ML de BenchmarkSuite ne
    # se fait que si `benchmarks` est laissé au défaut) et on retire SPEAKER.
    base = BENCHMARKS_ML if multilingual else BENCHMARKS
    benchmarks = {k: v for k, v in base.items() if k not in _CLES_SPEAKER}

    nom = f"{audio_dir.parent.name}__{audio_dir.name}"
    suite = BenchmarkSuite(
        datasets=[DirectoryDataset(str(audio_dir), name=nom)],
        reference_datasets=[DirectoryDataset(str(ref_dir), name="ref_fr")],
        benchmarks=benchmarks,
        multilingual=multilingual,
        skip_errors=True,
        include_environment=False,
        cache_dir=str(cache_dir),
        device=device,
        n_workers=n_workers if n_workers is not None else 4,
        category_weights={
            BenchmarkCategory.SPEAKER: 0.0,
            BenchmarkCategory.INTELLIGIBILITY: 1 / 3,
            BenchmarkCategory.PROSODY: 1 / 3,
            BenchmarkCategory.GENERIC: 1 / 3,
            BenchmarkCategory.ENVIRONMENT: 0.0,
        },
    )
    print(f"[ttsds2] device={device} n_workers={n_workers or 4} "
          f"gen={len(gen_wavs)} ref={len(ref_wavs)} — run…", flush=True)
    suite.run()
    score_global, par_composante = _extraire_scores(
        suite.get_aggregated_results(), nom
    )
    return {
        "score_global": score_global,
        "par_composante": par_composante,
        "ref": "fr",
        "ref_dir": str(ref_dir),
        "n_gen": len(gen_wavs),
        "n_ref": len(ref_wavs),
        "multilingual": multilingual,
        "speaker_exclu": True,   # cf. COMPOSANTES / requirements-ttsds2.txt
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--audio-dir", required=True)
    p.add_argument("--ref", default="", help=f"défaut : {_ref_defaut()}")
    p.add_argument("--out", default="", help="défaut : <audio-dir>/ttsds2.json")
    p.add_argument("--cache-dir", default="", help=f"cache TTSDS2 (défaut : {_cache_dir_defaut()})")
    p.add_argument("--device", default="", choices=["", "cuda", "cpu"],
                   help="défaut : cuda si dispo (CPU = prohibitif)")
    p.add_argument("--n-workers", type=int, default=4, help="parallélisme distances (défaut 4)")
    p.add_argument("--mono-lingue", action="store_true",
                   help="désactive le mode multilingue de TTSDS2 (modèles EN)")
    args = p.parse_args()

    audio_dir = Path(args.audio_dir)
    ref_dir = Path(args.ref) if args.ref else _ref_defaut()
    out = Path(args.out) if args.out else audio_dir / "ttsds2.json"

    data = ttsds2_dossier(audio_dir, ref_dir, multilingual=not args.mono_lingue,
                          cache_dir=args.cache_dir or None,
                          device=args.device or None, n_workers=args.n_workers)
    ecrire_ttsds2(out, data)
    print(f"[ttsds2] score_global={data['score_global']} "
          f"(n_gen={data['n_gen']}, n_ref={data['n_ref']}) -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
