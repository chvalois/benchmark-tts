#!/usr/bin/env python3
"""Licences — registre déclaré (`benchmark/licences.yaml`) + cohérence
avec `models.lock`.

Pas une mesure : une donnée vérifiée à la main une fois. Ce module la
charge, la valide, produit le verdict « usage commercial » et signale
toute divergence avec `models.lock` (deux sources qui se contredisent =
bug à corriger, pas à ignorer).
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_LICENCES = RACINE / "benchmark" / "licences.yaml"
CHEMIN_LOCK = RACINE / "models.lock"

VALEURS_USAGE = frozenset({"oui", "non", "conditionnel"})
_CHAMPS = frozenset({"licence", "usage_commercial", "source_url", "verifie_le", "note"})


class ErreurLicence(ValueError):
    """Le registre de licences est incohérent."""


def charger_licences(chemin: Path | str = CHEMIN_LICENCES) -> dict[str, dict]:
    with open(chemin, encoding="utf-8") as f:
        brut = yaml.safe_load(f)
    if not isinstance(brut, dict) or not brut:
        raise ErreurLicence("registre vide ou mal formé")
    for nom, e in brut.items():
        manquants = _CHAMPS - e.keys()
        if manquants:
            raise ErreurLicence(f"{nom} : champs manquants {sorted(manquants)}")
        if e["usage_commercial"] not in VALEURS_USAGE:
            raise ErreurLicence(f"{nom} : usage_commercial invalide {e['usage_commercial']!r}")
        if e["usage_commercial"] == "conditionnel" and not str(e.get("note") or "").strip():
            raise ErreurLicence(f"{nom} : 'conditionnel' exige une note explicative")
    return brut


def verdict_commercial(nom: str, registre: dict[str, dict] | None = None) -> str:
    reg = registre or charger_licences()
    if nom not in reg:
        raise ErreurLicence(f"modèle absent du registre : {nom}")
    usage = reg[nom]["usage_commercial"]
    return {
        "oui": "✅ usage commercial",
        "non": "❌ non commercial",
        "conditionnel": "⚠️ conditionnel (voir note)",
    }[usage]


def verifier_coherence_lock(
    registre: dict[str, dict] | None = None, chemin_lock: Path | str = CHEMIN_LOCK
) -> list[str]:
    """Retourne la liste des divergences entre le registre et `models.lock`
    (licence texte différente, ou verdict commercial opposé). Liste vide =
    cohérent."""
    reg = registre or charger_licences()
    with open(chemin_lock, encoding="utf-8") as f:
        modeles = json.load(f)["modeles"]

    divergences: list[str] = []
    for nom, m in modeles.items():
        if nom not in reg:
            divergences.append(f"{nom} : dans models.lock mais absent de licences.yaml")
            continue
        lock_commercial = bool(m.get("usage_commercial"))
        reg_commercial = reg[nom]["usage_commercial"] == "oui"
        if lock_commercial != reg_commercial:
            divergences.append(
                f"{nom} : usage_commercial models.lock={lock_commercial} "
                f"vs licences.yaml={reg[nom]['usage_commercial']!r}"
            )
    return divergences


def tableau_licences(registre: dict[str, dict] | None = None) -> list[dict]:
    reg = registre or charger_licences()
    return [
        {
            "modele": nom,
            "licence": e["licence"],
            "usage_commercial": e["usage_commercial"],
            "verdict": verdict_commercial(nom, reg),
            "note": e["note"],
        }
        for nom, e in sorted(reg.items())
    ]


if __name__ == "__main__":
    div = verifier_coherence_lock()
    for ligne in tableau_licences():
        print(f"{ligne['modele']:<26} {ligne['licence']:<34} {ligne['verdict']}")
    print()
    if div:
        print("DIVERGENCES registre <-> models.lock :")
        for d in div:
            print(f"  - {d}")
        raise SystemExit(1)
    print("registre cohérent avec models.lock.")
