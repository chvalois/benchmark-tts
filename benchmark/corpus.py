#!/usr/bin/env python3
"""Chargement et validation du corpus (`corpus/phrases.yaml`).

Le corpus est FIXE pour la durée d'une release. Ce module en fait la
seule porte d'entrée : il valide le schéma (longueur / registre / pièges
/ type) et expose des `Phrase` immuables. Toute entrée non conforme fait
échouer le chargement — jamais de silence.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
CHEMIN_CORPUS = RACINE / "corpus" / "phrases.yaml"
CHEMIN_LONGFORM = RACINE / "corpus" / "longform.yaml"

LONGUEURS = frozenset({"court", "moyen", "long"})
REGISTRES = frozenset({
    "narration", "dialogue_joie", "dialogue_colere", "dialogue_peur",
    "dialogue_tristesse", "cours_magistral",
})
PIEGES = frozenset({
    "liaison", "nombre", "nom_propre", "silence_rythme",
    "homographe_heterophone", "emprunt_en", "ponctuation_repetee", "onomatopee",
})
TYPES = frozenset({"phrase", "titre", "long_form", "multi_voix"})

_CHAMPS_REQUIS = frozenset({"texte", "longueur", "registre", "pieges"})

# --- volet LONG-FORM (v2 : narration longue + podcast + journalisme) ----
GENRES_LONGFORM = frozenset({
    "narration_livre", "podcast_solo", "podcast_dialogue", "interview_reponse",
    "journalisme_flash", "journalisme_reportage", "edito", "documentaire",
    "vulgarisation",
})
TRAITS_LONGFORM = frozenset({
    "tenue_timbre", "respiration_paragraphe", "sigle", "date_heure",
    "nombre_complexe", "nom_propre_dense", "discours_rapporte", "enumeration",
    "question_rhetorique", "incise", "anglicisme", "disfluence",
    "ponctuation_dialogue", "ironie", "terminologie", "bascule_registre",
    "homographe_heterophone",
})
_CHAMPS_REQUIS_LF = frozenset({"titre", "genre", "duree_cible_s", "fictif", "traits", "texte"})


class ErreurCorpus(ValueError):
    """Le corpus ne respecte pas le schéma attendu."""


@dataclass(frozen=True)
class Phrase:
    id: str
    texte: str
    longueur: str
    registre: str
    pieges: tuple[str, ...]
    type: str = "phrase"

    @property
    def est_titre(self) -> bool:
        return self.type == "titre"

    @property
    def est_multi_voix(self) -> bool:
        return self.type == "multi_voix"


def _valider(entree_id: str, d: object) -> Phrase:
    if not isinstance(d, dict):
        raise ErreurCorpus(f"{entree_id} : entrée non-dict ({type(d).__name__})")
    manquants = _CHAMPS_REQUIS - d.keys()
    if manquants:
        raise ErreurCorpus(f"{entree_id} : champs manquants {sorted(manquants)}")
    if not str(d["texte"]).strip():
        raise ErreurCorpus(f"{entree_id} : texte vide")
    if d["longueur"] not in LONGUEURS:
        raise ErreurCorpus(f"{entree_id} : longueur invalide {d['longueur']!r}")
    if d["registre"] not in REGISTRES:
        raise ErreurCorpus(f"{entree_id} : registre invalide {d['registre']!r}")
    pieges = tuple(d["pieges"] or ())
    inconnus = set(pieges) - PIEGES
    if inconnus:
        raise ErreurCorpus(f"{entree_id} : pièges inconnus {sorted(inconnus)}")
    type_ = d.get("type", "phrase")
    if type_ not in TYPES:
        raise ErreurCorpus(f"{entree_id} : type invalide {type_!r}")
    return Phrase(entree_id, str(d["texte"]).strip(), d["longueur"], d["registre"], pieges, type_)


def charger_corpus(chemin: Path | str = CHEMIN_CORPUS) -> list[Phrase]:
    with open(chemin, encoding="utf-8") as f:
        brut = yaml.safe_load(f)
    if not isinstance(brut, dict) or not brut:
        raise ErreurCorpus("corpus vide ou mal formé (attendu : mapping id -> entrée)")
    return [_valider(str(k), v) for k, v in brut.items()]


@dataclass(frozen=True)
class TexteLong:
    """Entrée du volet long-form (v2). Structurellement compatible avec
    `Phrase` pour traverser `executer_corpus` et le scoring : `registre`
    expose le `genre`, `pieges` expose les `traits`, `longueur` vaut
    toujours `"long"`."""

    id: str
    titre: str
    genre: str
    duree_cible_s: int
    fictif: bool
    traits: tuple[str, ...]
    texte: str
    type: str = "long_form"

    @property
    def est_titre(self) -> bool:
        return False

    @property
    def est_multi_voix(self) -> bool:
        return False

    @property
    def registre(self) -> str:
        return self.genre

    @property
    def longueur(self) -> str:
        return "long"

    @property
    def pieges(self) -> tuple[str, ...]:
        return self.traits


def _valider_longform(entree_id: str, d: object) -> TexteLong:
    if not isinstance(d, dict):
        raise ErreurCorpus(f"{entree_id} : entrée non-dict ({type(d).__name__})")
    manquants = _CHAMPS_REQUIS_LF - d.keys()
    if manquants:
        raise ErreurCorpus(f"{entree_id} : champs manquants {sorted(manquants)}")
    if not str(d["texte"]).strip():
        raise ErreurCorpus(f"{entree_id} : texte vide")
    if d["genre"] not in GENRES_LONGFORM:
        raise ErreurCorpus(f"{entree_id} : genre invalide {d['genre']!r}")
    if not isinstance(d["duree_cible_s"], int) or d["duree_cible_s"] <= 0:
        raise ErreurCorpus(f"{entree_id} : duree_cible_s invalide {d['duree_cible_s']!r}")
    if d["fictif"] is not True:
        raise ErreurCorpus(f"{entree_id} : fictif doit valoir true (corpus 100 % inventé)")
    traits = tuple(d["traits"] or ())
    inconnus = set(traits) - TRAITS_LONGFORM
    if inconnus:
        raise ErreurCorpus(f"{entree_id} : traits inconnus {sorted(inconnus)}")
    return TexteLong(
        entree_id, str(d["titre"]).strip(), d["genre"], int(d["duree_cible_s"]),
        True, traits, str(d["texte"]).strip(),
    )


def charger_longform(chemin: Path | str = CHEMIN_LONGFORM) -> list[TexteLong]:
    """Volet long-form (v2). Fichier distinct de `phrases.yaml` : même
    règle de gel pour la durée d'une release."""
    with open(chemin, encoding="utf-8") as f:
        brut = yaml.safe_load(f)
    if not isinstance(brut, dict) or not brut:
        raise ErreurCorpus("corpus long-form vide ou mal formé (attendu : mapping id -> entrée)")
    return [_valider_longform(str(k), v) for k, v in brut.items()]
