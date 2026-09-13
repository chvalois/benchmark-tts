#!/usr/bin/env python3
"""Normalisation de texte FR pour la comparaison ASR.

Deux sorties, une seule convention :
- `normaliser_texte()` -> str  : pour le WER (jiwer) ;
- `normaliser_mots()`  -> list : pour l'alignement mot-à-mot (fidélité).

Règle absolue : appliquer EXACTEMENT la même normalisation à la référence
et à l'hypothèse — sinon le WER / recall mesure la normalisation, pas le
modèle. *Language-agnostic* = aucune liste de mots-clés propre à un
corpus ; la langue ne sert qu'à `num2words` (chiffres -> lettres).

Angle mort corrigé le 2026-09-13 (v2) : les heures abrégées (« 10 h 45 »,
« 10h45 », « 10h ») sont désormais canonisées en « 10 heures 45 » avant le
développement générique des chiffres — des deux côtés (référence ET
transcription), donc peu importe que le texte source écrive « 10 h 45 »
ou que l'ASR transcrive « 10h45 » ou « 10 heures 45 », les trois formes
convergent vers la même normalisation. Avant ce correctif, le « h » isolé
survivait comme un mot à part (« dix h quarante-cinq ») et gonflait le WER
d'un modèle qui lisait pourtant l'heure correctement (cf. exemples réels
sur firered_tts3 / papa_narration, session du 2026-09-13).
"""
from __future__ import annotations

import re
import unicodedata

from num2words import num2words

# Balises de famille de modèle : retirées avant toute comparaison (jamais
# des « mots »). Cf. benchmark/CONTRAT_MODELE.md.
_TAG_PAUSE = re.compile(r"\[pause\s+[\d.]+s\]", re.IGNORECASE)
_TAG_VOICE_LANG_FX = re.compile(r"<\s*(?:voice|lang|fx)\s*:\s*[^>]*>", re.IGNORECASE)

_NOMBRE = re.compile(r"\d+(?:[.,]\d+)?")
_MOT = re.compile(r"[0-9a-zàâäáãéèêëïîíìôöòóõùûüúçñœæ]+", re.IGNORECASE)

# Heure abrégée FR : "10 h 45", "10h45", "10h 45", "10 h45", "10h" (sans
# minutes), et la forme déjà développée "10 heures 45" (le "h" isolé de
# "heures" est aussi capturé -> substitution idempotente, sans effet si le
# texte est déjà au clair).
_HEURE = re.compile(r"(\d{1,2})\s*[hH](?:eures?)?\s*(\d{1,2})?\b")


def retirer_balises(texte: str) -> str:
    t = _TAG_PAUSE.sub(" ", texte)
    return _TAG_VOICE_LANG_FX.sub(" ", t)


def developper_heures(texte: str) -> str:
    """« 10 h 45 » / « 10h45 » / « 10h » -> « 10 heures 45 » / « 10 heures ».

    Canonise la notation d'heure AVANT `developper_nombres` : ce dernier ne
    voit ensuite que des chiffres et le mot « heures » (déjà en toutes
    lettres, jamais touché par le développeur de chiffres), donc "10 h 45"
    et "10h45" produisent la MÊME sortie normalisée, quelle que soit la
    forme écrite côté référence ou transcrite côté ASR.
    """

    def _sub(m: re.Match) -> str:
        heure, minute = m.group(1), m.group(2)
        return f"{heure} heures {minute}" if minute else f"{heure} heures"

    return _HEURE.sub(_sub, texte)


def developper_nombres(texte: str, langue: str = "fr") -> str:
    """« 73 » -> « soixante-treize », « 10,5 » -> « dix virgule cinq ».

    Whisper transcrit les nombres en chiffres : on repasse TOUJOURS en
    lettres des deux côtés pour comparer à convention égale.
    """

    def _sub(m: re.Match) -> str:
        brut = m.group(0).replace(",", ".")
        if "." in brut:
            ent, dec = brut.split(".", 1)
            mots = [num2words(int(ent), lang=langue), "virgule"]
            mots += [num2words(int(c), lang=langue) for c in dec]
            return " ".join(mots)
        return num2words(int(brut), lang=langue)

    return _NOMBRE.sub(_sub, texte)


def normaliser_texte(texte: str, langue: str = "fr") -> str:
    t = retirer_balises(texte)
    t = developper_heures(t)
    t = developper_nombres(t, langue)
    t = unicodedata.normalize("NFC", t.lower())
    return " ".join(_MOT.findall(t))


def normaliser_mots(texte: str, langue: str = "fr") -> list[str]:
    texte_norm = normaliser_texte(texte, langue)
    return texte_norm.split() if texte_norm else []
