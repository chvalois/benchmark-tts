#!/usr/bin/env python3
"""doctor.py — vérifie que l'environnement est sain AVANT toute génération.

Contrôles : version Python, GPU + VRAM (nvidia-smi), CUDA (nvcc, non
bloquant), redirection du stockage vers D:, espace disque libre sur
TTSB_ROOT, caches par défaut qui alimenteraient encore C:.

Aucune dépendance tierce (stdlib seule). Code de sortie non nul si un
point bloquant échoue.

    source env.sh && python3 scripts/doctor.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

GO = 1024 ** 3

# Espace libre sur le système de fichiers de TTSB_ROOT
DISK_LIBRE_ERREUR_GO = 20   # en dessous : bloquant
DISK_LIBRE_WARN_GO = 80     # en dessous : set "lean" (~70 Go) seulement

# Variables qui DOIVENT pointer sous TTSB_ROOT (sinon écriture sur C:)
VARS_SOUS_RACINE = (
    "HF_HOME", "HF_HUB_CACHE", "TORCH_HOME", "UV_CACHE_DIR",
    "PIP_CACHE_DIR", "XDG_CACHE_HOME", "TTSB_VENVS", "TTSB_AUDIO_OUT",
)


class Rapport:
    """Accumule des lignes de diagnostic et retient s'il y a du bloquant."""

    def __init__(self) -> None:
        self._lignes = []
        self.bloquant = False

    def ok(self, sujet: str, detail: str) -> None:
        self._lignes.append(("OK  ", sujet, detail))

    def warn(self, sujet: str, detail: str) -> None:
        self._lignes.append(("WARN", sujet, detail))

    def erreur(self, sujet: str, detail: str) -> None:
        self._lignes.append(("FAIL", sujet, detail))
        self.bloquant = True

    def afficher(self) -> None:
        for niveau, sujet, detail in self._lignes:
            print(f"[{niveau}] {sujet:<20} {detail}")


def _run(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def _taille_go(chemin: Path) -> float:
    total = 0
    for p in chemin.rglob("*"):
        try:
            if p.is_file() and not p.is_symlink():
                total += p.stat().st_size
        except OSError:
            continue
    return total / GO


def _sous_racine(valeur: str, racine: Path) -> bool:
    try:
        Path(valeur).expanduser().resolve().relative_to(racine.resolve())
        return True
    except (ValueError, OSError):
        return False


def verifier_python(r: Rapport) -> None:
    v = sys.version_info
    if (v.major, v.minor) < (3, 10):
        r.erreur("python", f"3.10+ requis, trouvé {v.major}.{v.minor}")
    else:
        r.ok("python", f"{v.major}.{v.minor}.{v.micro}")


def verifier_gpu(r: Rapport) -> None:
    q = _run([
        "nvidia-smi",
        "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader,nounits",
    ])
    if not q:
        r.erreur("gpu", "nvidia-smi indisponible ou en échec")
        return
    nom, mem_mib, driver = (c.strip() for c in q.splitlines()[0].split(","))
    mem_go = int(float(mem_mib)) / 1024
    r.ok("gpu", f"{nom}, {mem_go:.1f} Go VRAM, driver {driver}")
    if mem_go < 23:
        r.warn("gpu", "< 24 Go : MOSS 8B / Voxtral risquent de ne pas tenir")


def verifier_cuda(r: Rapport) -> None:
    q = _run(["nvcc", "--version"])
    if q:
        r.ok("cuda (nvcc)", q.splitlines()[-1].strip())
    else:
        r.warn("cuda (nvcc)", "nvcc absent — non bloquant (torch embarque son runtime)")


def verifier_stockage(r: Rapport) -> Path | None:
    brut = os.environ.get("TTSB_ROOT")
    if not brut:
        r.erreur("stockage", "TTSB_ROOT non défini — `source env.sh` d'abord")
        return None
    racine = Path(brut)
    if not str(racine).startswith("/mnt/d"):
        r.warn("stockage", f"TTSB_ROOT={racine} n'est pas sur /mnt/d")
    if not racine.exists():
        r.erreur("stockage", f"{racine} n'existe pas (le `source env.sh` le crée)")
        return None
    if not os.access(racine, os.W_OK):
        r.erreur("stockage", f"{racine} non accessible en écriture")
        return None
    r.ok("stockage", f"TTSB_ROOT={racine}")

    for var in VARS_SOUS_RACINE:
        val = os.environ.get(var)
        if not val:
            r.warn("env", f"{var} non défini")
        elif not _sous_racine(val, racine):
            r.erreur("env", f"{var}={val} hors de TTSB_ROOT (risque écriture C:)")
        else:
            r.ok("env", f"{var} -> sous TTSB_ROOT")
    return racine


def verifier_caches_defaut(r: Rapport) -> None:
    home = Path.home()
    for label in ("huggingface", "uv", "torch"):
        chemin = home / ".cache" / label
        try:
            non_vide = chemin.is_dir() and any(chemin.iterdir())
        except OSError:
            non_vide = False
        if non_vide:
            r.warn(
                "cache HOME",
                f"~/.cache/{label} non vide ({_taille_go(chemin):.1f} Go) — "
                f"vérifier qu'il n'est plus alimenté",
            )


def verifier_espace(r: Rapport, racine: Path) -> None:
    libre_go = shutil.disk_usage(racine).free / GO
    if libre_go < DISK_LIBRE_ERREUR_GO:
        r.erreur("espace disque", f"{libre_go:.0f} Go libres (< {DISK_LIBRE_ERREUR_GO})")
    elif libre_go < DISK_LIBRE_WARN_GO:
        r.warn("espace disque", f"{libre_go:.0f} Go libres — set 'lean' (~70 Go) seulement")
    else:
        r.ok("espace disque", f"{libre_go:.0f} Go libres sur {racine}")


def main() -> int:
    r = Rapport()
    verifier_python(r)
    verifier_gpu(r)
    verifier_cuda(r)
    racine = verifier_stockage(r)
    verifier_caches_defaut(r)
    if racine is not None:
        verifier_espace(r, racine)

    print()
    r.afficher()
    print()
    if r.bloquant:
        print("=> BLOQUANT : corriger les lignes [FAIL] avant de générer.")
        return 1
    print("=> Environnement sain.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
