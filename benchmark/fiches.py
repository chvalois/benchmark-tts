#!/usr/bin/env python3
"""Fiches de vulgarisation par modèle — chargement + garde-fous.

`benchmark/fiches_modeles.yaml` est une donnée DÉCLARÉE, vérifiée à la main
(comme `licences.yaml`). Ce module la charge, valide sa forme, et vérifie sa
cohérence avec `models.lock` : une fiche qui parle d'un modèle absent du
verrou, ou un modèle scoré sans fiche, est un bug — pas un détail à ignorer.

    python3 -m benchmark.fiches        # table de contrôle + divergences
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_FICHES = RACINE / "benchmark" / "fiches_modeles.yaml"
CHEMIN_LOCK = RACINE / "models.lock"
RESULTATS = RACINE / "resultats"

_CHAMPS = frozenset({"une_phrase", "particularite", "choix_techniques",
                     "langues", "parametres", "a_savoir", "sources", "verifie_le"})


class ErreurFiche(ValueError):
    """Le registre de fiches est incohérent."""


def charger_fiches(chemin: Path | str = CHEMIN_FICHES) -> dict[str, dict]:
    with open(chemin, encoding="utf-8") as f:
        brut = yaml.safe_load(f)
    if not isinstance(brut, dict) or not brut:
        raise ErreurFiche("registre vide ou mal formé")
    for nom, e in brut.items():
        if not isinstance(e, dict):
            raise ErreurFiche(f"{nom} : entrée mal formée")
        manquants = _CHAMPS - e.keys()
        if manquants:
            raise ErreurFiche(f"{nom} : champs manquants {sorted(manquants)}")
        for texte in ("une_phrase", "particularite"):
            if not str(e.get(texte) or "").strip():
                raise ErreurFiche(f"{nom} : '{texte}' vide")
        if not e["choix_techniques"]:
            raise ErreurFiche(f"{nom} : aucun choix technique documenté")
        for bloc in e["choix_techniques"]:
            if not isinstance(bloc, dict) or not bloc.get("titre") or not bloc.get("texte"):
                raise ErreurFiche(f"{nom} : bloc 'choix_techniques' incomplet ({bloc!r})")
        lg = e.get("langues")
        if not isinstance(lg, dict) or not str(lg.get("resume") or "").strip():
            raise ErreurFiche(f"{nom} : 'langues.resume' manquant")
        if not str(lg.get("source") or "").strip():
            raise ErreurFiche(f"{nom} : 'langues.source' manquant (d'où vient la liste ?)")
        if not e["parametres"]:
            raise ErreurFiche(f"{nom} : aucun paramètre de génération documenté")
        for p in e["parametres"]:
            if not isinstance(p, dict) or not p.get("nom") or not p.get("role"):
                raise ErreurFiche(f"{nom} : bloc 'parametres' incomplet ({p!r})")
        if not e["sources"]:
            raise ErreurFiche(f"{nom} : aucune source (obligatoire)")
        for s in e["sources"]:
            if not isinstance(s, dict) or not s.get("label") or not s.get("url"):
                raise ErreurFiche(f"{nom} : source incomplète ({s!r})")
            if not str(s["url"]).startswith("https://"):
                raise ErreurFiche(f"{nom} : source non https ({s['url']})")
        if not str(e.get("verifie_le") or "").strip():
            raise ErreurFiche(f"{nom} : 'verifie_le' obligatoire (date de vérification)")
        for k in ("a_savoir",):
            if e[k] is None:
                e[k] = []
            if not isinstance(e[k], list):
                raise ErreurFiche(f"{nom} : '{k}' doit être une liste")
    return brut


def modeles_scorables(chemin_lock: Path | str = CHEMIN_LOCK) -> set[str]:
    """Modèles qui ont un rapport de mesures (`resultats/<nom>.json`) — ce sont
    eux qui méritent une page publique."""
    with open(chemin_lock, encoding="utf-8") as f:
        connus = set(json.load(f)["modeles"])
    return {f.stem for f in RESULTATS.glob("*.json")
            if f.stem != "ecoute" and f.stem in connus}


def verifier_coherence_lock(
    registre: dict[str, dict] | None = None, chemin_lock: Path | str = CHEMIN_LOCK
) -> list[str]:
    """Divergences entre le registre de fiches et `models.lock` / `resultats/`.
    Liste vide = cohérent."""
    reg = registre if registre is not None else charger_fiches()
    with open(chemin_lock, encoding="utf-8") as f:
        modeles = json.load(f)["modeles"]

    divergences: list[str] = []
    for nom in reg:
        if nom not in modeles:
            divergences.append(f"{nom} : fiche présente mais modèle absent de models.lock")
    for nom in sorted(modeles_scorables(chemin_lock)):
        if nom not in reg:
            divergences.append(f"{nom} : scoré (resultats/{nom}.json) mais sans fiche")
    return divergences


if __name__ == "__main__":
    reg = charger_fiches()
    div = verifier_coherence_lock(reg)
    for nom, e in sorted(reg.items()):
        print(f"{nom:<22} {len(e['choix_techniques'])} choix · "
              f"{len(e['a_savoir'])} mise(s) en garde · "
              f"{len(e['sources'])} source(s) · vérifié {e['verifie_le']}")
    print()
    if div:
        print("DIVERGENCES fiches <-> models.lock :")
        for d in div:
            print(f"  - {d}")
        raise SystemExit(1)
    print("registre de fiches cohérent avec models.lock.")
