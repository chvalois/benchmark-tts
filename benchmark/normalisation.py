#!/usr/bin/env python3
"""Normalisation de texte FR pour la comparaison ASR.

Deux sorties, une seule convention :
- `normaliser_texte()` -> str  : pour le WER (jiwer) ;
- `normaliser_mots()`  -> list : pour l'alignement mot-à-mot (fidélité).

Règle absolue : appliquer EXACTEMENT la même normalisation à la référence
et à l'hypothèse — sinon le WER / recall mesure la normalisation, pas le
modèle. *Language-agnostic* = aucune liste de mots-clés propre à un
corpus ; la langue ne sert qu'à `num2words` (chiffres -> lettres).

Angle mort connu (v1) : les abréviations d'unité (« 10 h 45 » -> « dix h
quarante-cinq ») ne sont PAS développées en « heures ». La ligne WER des
items à piège `nombre` se lit donc avec la transcription en main, pas
comme une valeur absolue (cf. APIAVISOL §3.3).
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


def retirer_balises(texte: str) -> str:
    t = _TAG_PAUSE.sub(" ", texte)
    return _TAG_VOICE_LANG_FX.sub(" ", t)


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
    t = developper_nombres(t, langue)
    t = unicodedata.normalize("NFC", t.lower())
    return " ".join(_MOT.findall(t))


def normaliser_mots(texte: str, langue: str = "fr") -> list[str]:
    texte_norm = normaliser_texte(texte, langue)
    return texte_norm.split() if texte_norm else []
