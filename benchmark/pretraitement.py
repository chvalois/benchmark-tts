#!/usr/bin/env python3
"""Pré-traitement du texte FR — commun à TOUS les modèles du benchmark.

Réf. : BENCHMARK_TTS_OPENSOURCE_FR_APIAVISOL.md §3.9 (6 étapes ordonnées)
       + §3.1 (ponctuation finale d'un titre — opt-in via `est_titre`).

Toutes les fonctions sont PURES (`str -> str`) : aucun effet de bord,
aucune mutation. `pretraiter()` applique les étapes dans l'ordre de la
spéc. Aucune heuristique de détection de « titre » : c'est une métadonnée
du corpus (`type: titre`), passée explicitement par l'appelant.

Le module ne connaît RIEN des balises propres à une famille de modèle
(`<voice:...>`, `<lang:...>`, `[pause N.Ns]`) : leur gestion appartient à
l'adaptateur du modèle (voir benchmark/CONTRAT_MODELE.md).
"""
from __future__ import annotations

import re

# --- Étape 0 : apostrophes typographiques -> ASCII -------------------------
# Fait en préambule : tout le reste (verbes élidés, « qu'il ») s'appuie
# dessus.
_APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "ʼ": "'"})


def normaliser_apostrophes(texte: str) -> str:
    return texte.translate(_APOSTROPHES)


# --- Étape 1 : structure markdown / mise en forme bloc --------------------
# On retire uniquement le NIVEAU BLOC (titres #, puces, citations >, règles
# ---). On NE touche PAS aux `*...*` : ce sont les délimiteurs d'onomatopée
# traités à l'étape 4.
_MD_TITRE = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]+", flags=re.MULTILINE)
_MD_PUCE = re.compile(r"^[ \t]{0,3}(?:[-+•]|\d+[.)])[ \t]+", flags=re.MULTILINE)
_MD_CITATION = re.compile(r"^[ \t]{0,3}>[ \t]?", flags=re.MULTILINE)
_MD_REGLE = re.compile(r"^[ \t]{0,3}(?:-{3,}|\*{3,}|_{3,})[ \t]*$", flags=re.MULTILINE)


def retirer_structure_markdown(texte: str) -> str:
    t = _MD_REGLE.sub("", texte)
    t = _MD_TITRE.sub("", t)
    t = _MD_CITATION.sub("", t)
    t = _MD_PUCE.sub("", t)
    return t


# --- Étape 2 : virgule d'incise avant un verbe de parole rapportée -------
# «  Bonjour  », répond Juliette.  ->  «  Bonjour  » répond Juliette.
# Liste volontairement bornée aux verbes fréquents en narration FR ;
# extensible.
_RADICAUX_PAROLE: tuple[str, ...] = (
    "dit", "dis", "disait",
    "repond", "repondit", "repondait",
    "répond", "répondit", "répondait",
    "demanda", "demande", "demandait",
    "s'écria", "s'exclama", "s'étonna", "s'indigna", "s'emporta",
    "murmura", "chuchota", "souffla", "soupira", "gémit",
    "cria", "hurla", "gronda", "tonna",
    "ajouta", "ajoute", "reprit", "reprend", "poursuivit", "continua",
    "lança", "lance", "fit", "conclut", "insista", "protesta", "rétorqua",
    "objecta", "renchérit", "acquiesça", "déclara", "affirma", "expliqua",
    "précisa", "songea", "pensa", "observa", "remarqua", "annonça",
    "balbutia", "bredouilla", "articula", "bafouilla",
)
_INCISE = re.compile(
    r",(\s+)(" + "|".join(re.escape(v) for v in _RADICAUX_PAROLE) + r")"
    r"(?!-(?:moi|toi|nous|vous|le|la|les|lui|leur))\b",
    flags=re.IGNORECASE,
)


def retirer_virgule_incise(texte: str) -> str:
    return _INCISE.sub(r" \2", texte)


# --- Étape 3 : points de suspension -> point simple ---------------------
_POINTS_SUSPENSION = re.compile(r"\.(?:[ \t]*\.)+")


def normaliser_points_suspension(texte: str) -> str:
    t = texte.replace("…", ".")
    return _POINTS_SUSPENSION.sub(".", t)


# --- Étape 4 : désamorcer les « ! » dans les onomatopées `*...*` --------
_ONOMATOPEE = re.compile(r"\*([^*\n]+?)\*")


def desamorcer_onomatopees(texte: str) -> str:
    return _ONOMATOPEE.sub(
        lambda m: "*" + m.group(1).replace("!", "").strip() + "*", texte
    )


# --- Étape 5 : saut de ligne en fin de phrase (si vraie phrase suit) ----
_ABREVIATIONS = (
    "M.", "MM.", "Mme", "Mmes", "Mlle", "Mlles", "Dr.", "Pr.", "St.", "Ste.",
    "cf.", "etc.", "ex.", "p.", "art.", "vol.", "chap.", "fig.",
)
_FIN_PHRASE = re.compile(
    r"([.!?…])([ \t]+)(?=[«\"“(]?[A-ZÀ-ÖØ-Þ0-9])"
)


def segmenter_phrases(texte: str) -> str:
    def _remplacer(m: re.Match) -> str:
        if m.group(1) == ".":
            avant = texte[: m.start() + 1]
            if any(avant.endswith(ab) for ab in _ABREVIATIONS):
                return m.group(0)
        return m.group(1) + "\n"

    return _FIN_PHRASE.sub(_remplacer, texte)


# --- Étape 6 : suppression des émojis (blocs Unicode dédiés) ------------
_EMOJI = re.compile(
    "["
    "\U0001f000-\U0001faff"  # jeux, pictogrammes, emoticons, transport, ext-A
    "\U00002600-\U000027bf"  # symboles divers + dingbats
    "\U00002300-\U000023ff"  # ⌚⏰⏳… (technique / horloges)
    "\U00002b00-\U00002bff"  # flèches / étoiles décoratives
    "\U0001f1e6-\U0001f1ff"  # indicateurs régionaux (drapeaux)
    "\U0000fe00-\U0000fe0f"  # sélecteurs de variation
    "\U0000200d"             # ZWJ (séquences emoji composées)
    "\U000020e3"             # keycap combinant
    "\U00002122\U00002139"   # ™ ℹ
    "]+"
)


def supprimer_emojis(texte: str) -> str:
    return _EMOJI.sub("", texte)


# --- Nettoyage d'espaces (ne touche PAS à l'espace fine FR avant ; : ! ? »)
_ESPACES_MULTIPLES = re.compile(r"[ \t]{2,}")
_ESPACE_AVANT_NL = re.compile(r"[ \t]+\n")
_LIGNES_VIDES = re.compile(r"\n{3,}")


def _reduire_espaces(texte: str) -> str:
    t = _ESPACES_MULTIPLES.sub(" ", texte)
    t = _ESPACE_AVANT_NL.sub("\n", t)
    t = _LIGNES_VIDES.sub("\n\n", t)
    return t


# --- §3.1 : titre sans ponctuation terminale -> ajout d'un point --------
_PONCT_TERMINALE = ".!?…»\"'"


def ajouter_ponctuation_finale(texte: str) -> str:
    t = texte.rstrip()
    if not t or t[-1] in _PONCT_TERMINALE:
        return t
    return t + "."


# --- Pipeline ----------------------------------------------------------
def pretraiter(texte: str, *, est_titre: bool = False) -> str:
    """Applique les 6 étapes §3.9 dans l'ordre, puis (si `est_titre`) §3.1.

    `est_titre` vient de la métadonnée `type: titre` du corpus — jamais
    d'une détection automatique.
    """
    t = normaliser_apostrophes(texte)
    t = retirer_structure_markdown(t)
    t = retirer_virgule_incise(t)
    t = normaliser_points_suspension(t)
    t = desamorcer_onomatopees(t)
    t = segmenter_phrases(t)
    t = supprimer_emojis(t)
    t = _reduire_espaces(t)
    if est_titre:
        t = ajouter_ponctuation_finale(t)
    return t.strip()
