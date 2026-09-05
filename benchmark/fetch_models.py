#!/usr/bin/env python3
"""fetch_models.py — télécharge les poids listés dans models.lock vers D:.

Garantit un stockage sur `$HF_HUB_CACHE` (donc D:) et un re-téléchargement
reproductible via une révision épinglée (SHA de commit HF).

    source env.sh
    python3 benchmark/fetch_models.py --check              # plan + tailles, rien téléchargé
    python3 benchmark/fetch_models.py --phase 1            # tous les modèles de la phase 1
    python3 benchmark/fetch_models.py --model chatterbox_v3
    python3 benchmark/fetch_models.py --set lean           # tout sauf phase 'ref'
    python3 benchmark/fetch_models.py --set outil          # ASR de scoring

Dépendance : huggingface_hub (>= 0.24). Refuse de tourner si HF_HOME n'est
pas sous TTSB_ROOT (garde-fou anti-écriture C:).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

LOCK = Path(__file__).resolve().parent.parent / "models.lock"


def _charger_lock() -> dict:
    with open(LOCK, encoding="utf-8") as f:
        return json.load(f)


def _verifier_stockage() -> None:
    racine = os.environ.get("TTSB_ROOT")
    hf = os.environ.get("HF_HUB_CACHE")
    if not racine or not hf:
        sys.exit("[FAIL] TTSB_ROOT / HF_HUB_CACHE non définis — `source env.sh` d'abord.")
    try:
        Path(hf).resolve().relative_to(Path(racine).resolve())
    except ValueError:
        sys.exit(f"[FAIL] HF_HUB_CACHE={hf} hors de TTSB_ROOT — risque d'écriture sur C:.")


def _selection(modeles: dict, args: argparse.Namespace) -> dict:
    if args.model:
        if args.model not in modeles:
            sys.exit(f"[FAIL] modèle inconnu : {args.model}. Connus : {', '.join(modeles)}")
        return {args.model: modeles[args.model]}
    if args.phase is not None:
        return {k: v for k, v in modeles.items() if str(v.get("phase")) == args.phase}
    if args.set == "lean":
        return {k: v for k, v in modeles.items() if v.get("phase") != "ref"}
    if args.set == "complet":
        return dict(modeles)
    if args.set == "outil":
        return {k: v for k, v in modeles.items() if v.get("phase") == "outil"}
    return dict(modeles)


def _afficher_plan(selection: dict) -> None:
    disque = 0.0
    print(f"{'modèle':<26} {'phase':<6} {'licence':<26} {'VRAM':>5} {'disque':>7}  révision")
    print("-" * 100)
    for nom, m in selection.items():
        disque += float(m.get("disque_go_estimee") or 0)
        rev = m.get("revision") or "NON ÉPINGLÉE"
        verif = "" if m.get("repo_id_verifie") else "  (repo_id NON vérifié)"
        print(
            f"{nom:<26} {str(m.get('phase')):<6} {m.get('licence',''):<26} "
            f"{str(m.get('vram_go_estimee','?'))+'Go':>5} "
            f"{str(m.get('disque_go_estimee','?'))+'Go':>7}  "
            f"{m.get('repo_id','?')} @ {rev}{verif}"
        )
    print("-" * 100)
    print(f"disque estimé (venv + poids + marge) : ~{disque:.0f} Go")


def _telecharger(nom: str, m: dict, allow_unpinned: bool) -> None:
    revision = m.get("revision")
    if not revision:
        if not allow_unpinned:
            print(f"[SKIP] {nom} : révision non épinglée (relancer avec --allow-unpinned).")
            return
        revision = None
        print(f"[WARN] {nom} : téléchargement SANS révision épinglée (non reproductible).")

    from huggingface_hub import snapshot_download  # import tardif : dépendance optionnelle

    chemin = snapshot_download(
        repo_id=m["repo_id"],
        revision=revision,
        allow_patterns=m.get("hf_allow_patterns"),
        cache_dir=os.environ["HF_HUB_CACHE"],
    )
    print(f"[OK]   {nom} -> {chemin}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    cible = p.add_mutually_exclusive_group()
    cible.add_argument("--model", help="un modèle précis (clé de models.lock)")
    cible.add_argument("--phase", help="tous les modèles d'une phase (1, 2, ref, outil)")
    cible.add_argument("--set", choices=("lean", "complet", "outil"), help="ensemble prédéfini")
    p.add_argument("--check", action="store_true", help="affiche le plan sans rien télécharger")
    p.add_argument("--allow-unpinned", action="store_true", help="autorise une révision non épinglée")
    args = p.parse_args()

    _verifier_stockage()
    lock = _charger_lock()
    selection = _selection(lock["modeles"], args)
    if not selection:
        sys.exit("[FAIL] sélection vide.")

    _afficher_plan(selection)
    if args.check:
        return 0

    try:
        import huggingface_hub  # noqa: F401
    except ImportError:
        sys.exit("[FAIL] huggingface_hub absent : pip/uv install -r benchmark/requirements.txt")

    print()
    for nom, m in selection.items():
        _telecharger(nom, m, args.allow_unpinned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
