#!/usr/bin/env python3
"""Découpage en chunks — paramétré PAR FAMILLE de modèle.

APIAVISOL §2.3, §3.1 : jamais de texte long en un seul appel. Fusion des
phrases en blocs (paragraphe / registre) jusqu'à une borne dure de mots
OU de caractères, coupure sur saut de paragraphe et sur bascule
narration <-> dialogue. Les silences de fin de chunk sont du silence PUR
ajouté APRÈS génération — jamais envoyés au modèle.

Règles communes à toutes les familles : `max_mots`, fusion, catégorie.
Seuls les seuils diffèrent (`ParamsChunk`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

MOTS_REPLIQUE_COURTE = 3  # <= 3 mots -> "replique_courte" (cf. corpus C3)

_DEBUT_DIALOGUE = re.compile(r'^\s*(?:[—–-]|«|"|“|«)')
_FIN_PHRASE = re.compile(r'(?<=[.!?…])\s+')


@dataclass(frozen=True)
class ParamsChunk:
    max_mots: int = 60
    max_cars: int = 400
    silence_phrase_ms: int = 300
    silence_forte_ms: int = 450        # après ? ou !
    silence_paragraphe_ms: int = 600


# Bornes issues du retour d'expérience avisol (200 cars -> crash CUDA flow model).
FAMILLE_CHATTERBOX = ParamsChunk(
    max_mots=60, max_cars=160,
    silence_phrase_ms=300, silence_forte_ms=450, silence_paragraphe_ms=600,
)
FAMILLE_DEFAUT = ParamsChunk()


@dataclass(frozen=True)
class Chunk:
    texte: str
    categorie: str            # narration | dialogue | replique_courte
    silence_apres_ms: int


def _est_dialogue(texte: str) -> bool:
    return bool(_DEBUT_DIALOGUE.match(texte))


def _categorie(texte: str) -> str:
    if len(texte.split()) <= MOTS_REPLIQUE_COURTE:
        return "replique_courte"
    return "dialogue" if _est_dialogue(texte) else "narration"


def segmenter_en_phrases(bloc: str) -> list[str]:
    """Découpe un bloc en phrases sur `.` `!` `?` `…` (et sur les sauts de
    ligne déjà posés par le pré-traitement §3.9 étape 5)."""
    phrases: list[str] = []
    for ligne in bloc.split("\n"):
        for p in _FIN_PHRASE.split(ligne.strip()):
            p = p.strip()
            if p:
                phrases.append(p)
    return phrases


def _appliquer_borne_dure(phrases: list[str], params: ParamsChunk) -> list[str]:
    """Borne DURE (APIAVISOL §3.1) : une phrase unique plus longue que
    `max_mots` / `max_cars` (sans ponctuation interne) est pré-coupée sur
    les frontières de mots — sinon crash du modèle de flow (avisol :
    200 cars -> crash CUDA)."""
    sortie: list[str] = []
    for phrase in phrases:
        mots = phrase.split()
        if len(mots) <= params.max_mots and len(phrase) <= params.max_cars:
            sortie.append(phrase)
            continue
        courant: list[str] = []
        for mot in mots:
            provisoire = " ".join(courant + [mot])
            trop = len(courant) + 1 > params.max_mots or len(provisoire) > params.max_cars
            if courant and trop:
                sortie.append(" ".join(courant))
                courant = [mot]
            else:
                courant.append(mot)
        if courant:
            sortie.append(" ".join(courant))
    return sortie


def _silence_fin(phrase: str, params: ParamsChunk, fin_paragraphe: bool) -> int:
    if fin_paragraphe:
        return params.silence_paragraphe_ms
    return params.silence_forte_ms if phrase.rstrip()[-1:] in "?!" else params.silence_phrase_ms


def decouper(texte: str, params: ParamsChunk = FAMILLE_DEFAUT) -> list[Chunk]:
    """Texte (déjà pré-traité) -> liste de `Chunk`. Le dernier chunk a un
    `silence_apres_ms = 0` (rien après la fin)."""
    paragraphes = [p for p in re.split(r"\n\s*\n", texte) if p.strip()]
    chunks: list[Chunk] = []

    for paragraphe in paragraphes:
        phrases = _appliquer_borne_dure(segmenter_en_phrases(paragraphe), params)
        bloc: list[str] = []
        bloc_dialogue: bool | None = None

        def _flush(fin_paragraphe: bool) -> None:
            nonlocal bloc, bloc_dialogue
            if not bloc:
                return
            texte_bloc = " ".join(bloc)
            chunks.append(Chunk(
                texte=texte_bloc,
                categorie=_categorie(texte_bloc),
                silence_apres_ms=_silence_fin(bloc[-1], params, fin_paragraphe),
            ))
            bloc = []
            bloc_dialogue = None

        for phrase in phrases:
            est_dlg = _est_dialogue(phrase)
            mots_actuels = sum(len(p.split()) for p in bloc)
            cars_actuels = len(" ".join(bloc))
            depasse = (
                mots_actuels + len(phrase.split()) > params.max_mots
                or cars_actuels + len(phrase) + 1 > params.max_cars
            )
            bascule = bloc_dialogue is not None and est_dlg != bloc_dialogue
            if bloc and (depasse or bascule):
                _flush(fin_paragraphe=False)
            bloc.append(phrase)
            bloc_dialogue = est_dlg

        _flush(fin_paragraphe=True)

    if chunks:
        dernier = chunks[-1]
        chunks[-1] = Chunk(dernier.texte, dernier.categorie, 0)
    return chunks


def categorie_globale(chunks: list[Chunk]) -> str:
    cats = {c.categorie for c in chunks}
    if not cats:
        return "inconnu"
    if len(cats) == 1:
        return next(iter(cats))
    return "mixte"
