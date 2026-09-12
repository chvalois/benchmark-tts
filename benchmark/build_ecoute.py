#!/usr/bin/env python3
"""Génère le test d'écoute local `site/ecoute/`.

Construit des **pools** larges ; la page en tire un sous-ensemble aléatoire
(≤ `LIMITE_SESSION`) DIFFÉRENT à chaque session (cf. `index.html`), donc les
phrases ne sont jamais toujours les mêmes et une session reste courte.

- **toutes** les phrases du corpus (hors `multi_voix`) entrent dans le pool
  (`N_PHRASES_* = 34`) → variété maximale entre sessions ;
- pools A/B et MOS construits **pour chaque voix de `VOIX_ECOUTE`**
  (papa / aurore2 / tonton_marc / papy / johnny / manou) — chaque item porte
  sa voix ; MOS joue la `ref_<voix>.wav` correspondante. Les combos
  (modèle, voix) au WER > `WER_MAX_ECOUTE` (clips cassés) sont exclus ;
- **MOS + registres émotionnels** : les phrases de registre joie / colère /
  peur / tristesse (cf. `EMOTIONS`) ne sont notées en MOS que sur des clips
  clonés depuis la **voix de réf émotionnelle** correspondante
  (`papa_<émotion>`) — jamais depuis une voix de narration neutre ;
- pool A/B : chaque tête `TETES` vs les challengers + duels
  challenger-vs-challenger + paires aléatoires ;
- pool MOS : `N_MODELES_MOS` modèles tournants par phrase ;
- pool ÉMOTION : modèle A vs modèle B, les DEUX clonant la même voix
  `papa_<émotion>` sur la même phrase — « lequel rend le mieux
  l'émotion <X> ? » (compare les modèles sur leur rendu émotionnel) ;
- copie les WAV dans `site/ecoute/audio/` sous des noms anonymes
  (`c0001.wav`) — mapping clip→modèle dans `_solution.json`, **jamais
  chargé par la page** ;
- écrit `manifest.js` (données de la page, sans nom de modèle).

Kokoro est exclu du test (voix interne fixe, non comparable voix-à-voix).

    source env.sh
    python3 benchmark/build_ecoute.py
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import shutil
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
CORPUS = RACINE / "corpus" / "phrases.yaml"
RESULTATS = RACINE / "resultats"
SORTIE = RACINE / "site" / "ecoute"
AUDIO_SRC = Path("/mnt/d/tts-benchmark-data/audio_genere")  # $TTSB_AUDIO_OUT

# Modèles jugés à l'écoute = uniquement les clonants. Kokoro est EXCLU du
# test (A/B, MOS, émotion) : voix interne fixe `ff_siwis`, non comparable
# voix-à-voix — sa qualité reste couverte par les métriques auto
# (UTMOS + comparatif). Cf. docs/METHODOLOGIE.md §10.6.
MODELES = ["firered_tts3", "voxcpm2", "chatterbox_v3", "cosyvoice3_05b",
           "xtts_v2", "moss_tts_local_v15", "omnivoice", "audio8_06b"]
# Les deux "têtes" : plus exposées (vs chaque challenger + l'une à l'autre).
# VoxCPM2 en tête aussi (moins lourd que FireRed, intérêt fort).
TETES = ["voxcpm2", "firered_tts3"]

# Voix de référence jugées à l'écoute (A/B + MOS). Le mode ÉMOTION reste
# sur les voix `papa_*`. Chaque item porte sa voix ; la page joue la bonne
# `ref_<voix>.wav` en MOS. Une voix absente pour un modèle est sautée.
VOIX_ECOUTE = ["papa_narration", "aurore2_narration", "tonton_marc_narration",
               "papy_narration", "johnny", "manou_narration"]
VOIX = "papa_narration"          # défaut historique (émotion, ref.wav)
REF_WAV = RACINE / "corpus" / "voix_reference" / f"{VOIX}.wav"
WER_MAX_ECOUTE = 0.30            # exclut du A/B et du MOS les combos (modèle, voix)
#                                 dont le WER moyen dépasse ce seuil (clips cassés :
#                                 ex. firered/voxcpm sur papy → 60-77 %)
REP = 1
SEED = 20260906

# On construit un POOL large (× voix) ; la page en tire un sous-ensemble
# ALÉATOIRE (≤ LIMITE_SESSION, cf. index.html) DIFFÉRENT à chaque session —
# phrases ET voix variées, session courte.
# `N_PHRASES_* >= 34` → **toutes** les phrases du corpus (hors multi_voix)
# entrent dans le pool : la variété maximale entre sessions.
N_PHRASES_AB = 34       # toutes les phrases par voix
N_PAIRES_ALEA = 3       # paires entièrement aléatoires / voix (calibration)
N_PHRASES_MOS = 34      # toutes les phrases par voix × 2 modèles tournants
N_MODELES_MOS = 2       # modèles notés par phrase MOS (rotation équilibrée)
N_PAIRES_EMO = 3        # paires modèle-vs-modèle par phrase d'émotion
LIMITE_SESSION = 20     # items max tirés par session (cf. index.html)

# --- mode ÉMOTION : modèle A vs modèle B, MÊME voix de réf émotionnelle ---
# « Lequel rend le mieux l'émotion <X> ? » — les deux clips clonent la voix
# `papa_<émotion>` sur la même phrase ; on compare les MODÈLES sur leur
# rendu de l'émotion (pas émotion vs neutre : le résultat serait joué
# d'avance). Un modèle sans clip pour ce (phrase, voix) est sauté.
EMO_MODELES = ["firered_tts3", "voxcpm2", "chatterbox_v3", "moss_tts_local_v15",
               "cosyvoice3_05b", "xtts_v2", "omnivoice", "audio8_06b"]
EMOTIONS = {                       # émotion -> (voix de réf, phrases, mot pour la question)
    "joie":      ("papa_joie",      ["p01", "p06"],                      "JOYEUX / ENTHOUSIASTE"),
    "colere":    ("papa_colere",    ["p02", "p07", "p19", "p22", "p33"], "EN COLÈRE"),
    "peur":      ("papa_peur",      ["p03", "p08", "p34"],               "APEURÉ / INQUIET"),
    "tristesse": ("papa_tristesse", ["p04", "p09"],                      "TRISTE"),
}
# phrase de registre émotionnel -> voix de réf émotionnelle correspondante.
# En MOS, ces phrases ne sont notées QUE sur des clips clonés depuis la voix
# émotionnelle (`papa_<émotion>`), jamais depuis une voix de narration neutre.
MOS_VOIX_EMO = {p: vw for (vw, phs, _m) in EMOTIONS.values() for p in phs}

DEFAUTS = [
    {"k": "tronque", "label": "coupé / tronqué"},
    {"k": "repetition", "label": "répétition / bégaiement"},
    {"k": "voix_diff", "label": "voix ne ressemble pas"},
    {"k": "accent", "label": "accent / prononciation FR"},
    {"k": "artefact", "label": "artefact / bruit / robotique"},
]
AXES_MOS = [
    {"k": "naturel", "label": "Naturel"},
    {"k": "intelligibilite", "label": "Intelligibilité"},
    {"k": "similarite", "label": "Similarité à la voix de réf"},
    {"k": "expressivite", "label": "Expressivité / registre"},
]


def _voix_de(_modele: str) -> str:
    return VOIX          # tous les modèles du test clonent la même voix


def _hid(prefixe: str, *parts) -> str:
    """id STABLE dérivé du contenu : un même item garde son id d'un build
    à l'autre → les exports d'auditeurs restent valides tant que l'item
    reste dans le pool. `_flip` : côté A/B déterministe (pas de biais de
    position mais reproductible)."""
    h = hashlib.md5("|".join(map(str, parts)).encode()).hexdigest()
    return prefixe + h[:10]


def _flip(hid: str) -> bool:
    return int(hid[-2:], 16) % 2 == 1


# --- équité d'exposition : sur-représente dans le NOUVEAU pool les modèles
# les moins ENTENDUS jusqu'ici (votes réels déjà collectés dans exports/,
# dé-anonymisés via les solutions archivées) — un modèle tout juste ajouté
# (compte=0) démarre avec le poids maximal. -------------------------------
def _charger_solution_archivee() -> dict:
    """Fusion de `_solution.json` (build courant, avant écrasement) + de
    l'archive `_solutions/` — mapping id -> modèle(s) des builds précédents,
    seul moyen de décoder les votes réels déjà exportés."""
    sol: dict[str, dict] = {"ab": {}, "mos": {}, "emo": {}}
    dossier = SORTIE / "_solutions"
    fichiers = sorted(dossier.glob("*.json")) if dossier.is_dir() else []
    courante = SORTIE / "_solution.json"
    if courante.is_file():
        fichiers = fichiers + [courante]
    for f in fichiers:
        d = json.loads(f.read_text(encoding="utf-8"))
        for k in ("ab", "mos", "emo"):
            sol[k].update(d.get(k, {}))
    return sol


def _comptes_ecoute(modeles: list[str]) -> dict[str, int]:
    """Nb de fois que chaque modèle a été réellement ENTENDU (voté) dans
    `exports/*.json` — pas juste « proposé » dans un pool. Un modèle absent
    des exports (jamais écouté, ex. tout juste ajouté) reste à 0."""
    comptes = {m: 0 for m in modeles}
    dossier_exports = RACINE / "exports"
    if not dossier_exports.is_dir():
        return comptes
    sol = _charger_solution_archivee()
    axes_mos = [a["k"] for a in AXES_MOS]
    for f in sorted(dossier_exports.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for v in d.get("votes", []):
            vid = v.get("id")
            if not vid:
                continue
            if vid in sol["ab"] and v.get("choix"):
                s = sol["ab"][vid]
                for m in (s.get("A_modele"), s.get("B_modele")):
                    if m in comptes:
                        comptes[m] += 1
            elif vid in sol["emo"] and v.get("choix"):
                s = sol["emo"][vid]
                for m in (s.get("A_modele"), s.get("B_modele")):
                    if m in comptes:
                        comptes[m] += 1
            elif vid in sol["mos"] and any(v.get(a) is not None for a in axes_mos):
                m = sol["mos"][vid].get("modele")
                if m in comptes:
                    comptes[m] += 1
    return comptes


def _poids_equite(comptes: dict[str, int]) -> dict[str, float]:
    """Poids décroissant avec le nb d'écoutes déjà collectées (racine plutôt
    qu'inverse linéaire : sur-représente sans pour autant écraser les
    modèles déjà bien couverts à quasi rien). Un modèle à 0 écoute a le
    poids maximal (1.0) ; à 58 écoutes déjà, ~0,13 (~7-8x moins de chances
    d'être tiré à chaque tour) -> rattrapage rapide sans exclusion de fait."""
    return {m: 1.0 / math.sqrt(1 + n) for m, n in comptes.items()}


def _tirage_pondere(rnd: random.Random, pool: list[str], poids: dict[str, float]) -> str:
    return rnd.choices(pool, weights=[poids.get(m, 1.0) for m in pool], k=1)[0]


def _tirage_pondere_sans_remise(
    rnd: random.Random, pool: list[str], poids: dict[str, float], k: int
) -> list[str]:
    """`k` modèles DISTINCTS de `pool`, tirés sans remise mais pondérés
    (poids fort = plus de chances d'être tiré tôt)."""
    restant = list(pool)
    out: list[str] = []
    for _ in range(min(k, len(restant))):
        m = _tirage_pondere(rnd, restant, poids)
        out.append(m)
        restant.remove(m)
    return out


def _wav(modele: str, phrase: str, voix: str | None = None) -> Path:
    return AUDIO_SRC / modele / (voix or _voix_de(modele)) / f"{phrase}_{REP}.wav"


def _charger_selection() -> tuple[list[str], list[str]]:
    """(phrases_ab, phrases_mos) — flaggées d'abord, complétées au hasard."""
    corpus = yaml.safe_load(CORPUS.read_text(encoding="utf-8"))
    exclues = {pid for pid, v in corpus.items() if v.get("type") == "multi_voix"}
    toutes = [pid for pid in corpus if pid not in exclues]

    flaggees: set[str] = set()
    wer_max: dict[str, float] = {pid: 0.0 for pid in toutes}
    for m in MODELES:
        f = RESULTATS / f"{m}.json"
        if not f.is_file():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        r = data.get(_voix_de(m)) or next(iter(data.values()))
        s = r["synthese"]
        for cle in ("phrases_hallucination", "phrases_repetition", "phrases_troncature"):
            flaggees.update(s.get(cle, []))
        for pid, x in r["stabilite"]["par_phrase"].items():
            if x["suspect"]:
                flaggees.add(pid)
        for ligne in r["lignes"]:
            wer_max[ligne["id_phrase"]] = max(wer_max[ligne["id_phrase"]], ligne["wer"])
    flaggees.update(pid for pid, w in wer_max.items() if w >= 0.30)
    flaggees &= set(toutes)

    rnd = random.Random(SEED)
    propres = [pid for pid in toutes if pid not in flaggees]
    rnd.shuffle(propres)
    flag_l = sorted(flaggees)
    rnd.shuffle(flag_l)

    ordre = lambda p: int(p[1:])  # noqa: E731 — tri par numéro de phrase

    def _prendre(n: int) -> list[str]:
        if n >= len(toutes):                       # toutes les phrases
            return sorted(toutes, key=ordre)
        # sinon : moitié flaggées (pièges connus) + moitié propres, au hasard
        moitie = max(1, n // 2)
        pool = flag_l[:moitie] + propres[: n - min(moitie, len(flag_l))]
        return sorted(set(pool), key=ordre)[:n]

    return _prendre(N_PHRASES_AB), _prendre(N_PHRASES_MOS)


def _combos_exclus() -> set[tuple[str, str]]:
    """(modèle, voix) au WER moyen > WER_MAX_ECOUTE → clips inexploitables
    pour une comparaison à l'écoute (on ne compare pas un clip cassé)."""
    out: set[tuple[str, str]] = set()
    for m in MODELES:
        f = RESULTATS / f"{m}.json"
        if not f.is_file():
            continue
        for voix, r in json.loads(f.read_text(encoding="utf-8")).items():
            if r["synthese"]["wer_moyen"] > WER_MAX_ECOUTE:
                out.add((m, voix))
    return out


def build() -> None:
    audio_dir = SORTIE / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    for old in audio_dir.glob("*.wav"):
        old.unlink()

    rnd = random.Random(SEED)
    phrases_ab, phrases_mos = _charger_selection()

    comptes_ecoute = _comptes_ecoute(sorted(set(MODELES) | set(EMO_MODELES)))
    poids = _poids_equite(comptes_ecoute)
    print("[build_ecoute] écoutes réelles déjà collectées (équité, poids appliqué) : "
          + ", ".join(f"{m}={comptes_ecoute[m]}" for m in sorted(comptes_ecoute, key=lambda m: comptes_ecoute[m])))

    clips: dict[tuple[str, str], str] = {}
    solution_clips: dict[str, dict] = {}

    def clip_id(modele: str, phrase: str, voix: str | None = None) -> str:
        voix = voix or _voix_de(modele)
        key = (modele, voix, phrase)
        if key not in clips:
            src = _wav(modele, phrase, voix)
            if not src.is_file():
                raise SystemExit(f"[FAIL] audio manquant : {src}")
            cid = f"c{len(clips) + 1:04d}"
            shutil.copy2(src, audio_dir / f"{cid}.wav")
            clips[key] = cid
            solution_clips[cid] = {"modele": modele, "phrase": phrase, "rep": REP,
                                   "voix": voix}
        return clips[key]

    corpus = yaml.safe_load(CORPUS.read_text(encoding="utf-8"))
    exclus = _combos_exclus()

    def _ok(m: str, voix: str, phrase: str) -> bool:
        return (m, voix) not in exclus and _wav(m, phrase, voix).is_file()

    # --- paires A/B, PAR VOIX : pas de champion unique -------------------
    #   1) une tête (alternée) vs un challenger (tiré au sort, PONDÉRÉ équité) ;
    #   2) 1 phrase / 2 : duel des têtes ; l'autre : challenger vs challenger
    #      (les deux tirés pondérés équité) ;
    #   + N_PAIRES_ALEA paires aléatoires / voix (pondérées équité aussi).
    # Un combo (modèle, voix) au WER > seuil (clip cassé) est sauté.
    # Pondération équité (`poids`) : un modèle moins écouté jusqu'ici a plus
    # de chances d'être tiré -> sur-représenté dans CE pool pour rattraper
    # les modèles déjà beaucoup entendus (cf. `_comptes_ecoute` plus haut).
    challengers = [m for m in MODELES if m not in TETES]
    paires: list[dict] = []
    vus: set[tuple] = set()

    def _ajouter(voix: str, phrase: str, a: str, b: str) -> None:
        if a == b or not _ok(a, voix, phrase) or not _ok(b, voix, phrase):
            return
        cle = (voix, phrase, *sorted((a, b)))
        if cle in vus:
            return
        vus.add(cle)
        paires.append({"voix": voix, "phrase": phrase, "m1": a, "m2": b})

    for voix in VOIX_ECOUTE:
        for i, phrase in enumerate(phrases_ab):
            chall = _tirage_pondere(rnd, challengers, poids)
            _ajouter(voix, phrase, TETES[(i + i // len(challengers)) % 2], chall)
            if i % 2 == 0:
                _ajouter(voix, phrase, TETES[0], TETES[1])
            else:
                a = _tirage_pondere(rnd, challengers, poids)
                reste = [m for m in challengers if m != a] or [a]
                b = _tirage_pondere(rnd, reste, poids)
                _ajouter(voix, phrase, a, b)
        for _ in range(N_PAIRES_ALEA * 6):
            phrase = rnd.choice(phrases_ab)
            a = _tirage_pondere(rnd, MODELES, poids)
            reste = [m for m in MODELES if m != a]
            b = _tirage_pondere(rnd, reste, poids)
            _ajouter(voix, phrase, a, b)

    rnd.shuffle(paires)

    ab: list[dict] = []
    solution_ab: dict[str, dict] = {}
    for pr in paires:
        mlo, mhi = sorted((pr["m1"], pr["m2"]))
        aid = _hid("ab", pr["voix"], pr["phrase"], mlo, mhi)
        if aid in solution_ab:
            continue
        m_a, m_b = (mhi, mlo) if _flip(aid) else (mlo, mhi)
        ab.append({
            "id": aid, "phrase": pr["phrase"], "voix": pr["voix"],
            "texte": corpus[pr["phrase"]]["texte"].strip().replace("\n", " "),
            "registre": corpus[pr["phrase"]]["registre"],
            "A": f"audio/{clip_id(m_a, pr['phrase'], pr['voix'])}.wav",
            "B": f"audio/{clip_id(m_b, pr['phrase'], pr['voix'])}.wav",
        })
        solution_ab[aid] = {"phrase": pr["phrase"], "voix": pr["voix"],
                            "A_modele": m_a, "B_modele": m_b}

    # --- clips MOS : 2 modèles tournants par (phrase, voix) -------------
    # Phrase de registre émotionnel  -> UNIQUEMENT la voix `papa_<émotion>`
    # correspondante (pas de rendu neutre d'une réplique en colère, etc.).
    # Phrase neutre                  -> les voix de `VOIX_ECOUTE`.
    # Rotation PONDÉRÉE équité (sans remise) plutôt qu'un simple modulo :
    # un modèle moins écouté jusqu'ici a plus de chances d'entrer dans les
    # `N_MODELES_MOS` tirés pour chaque (phrase, voix).
    mos: list[dict] = []
    solution_mos: dict[str, dict] = {}
    for phrase in phrases_mos:
        voix_list = [MOS_VOIX_EMO[phrase]] if phrase in MOS_VOIX_EMO else VOIX_ECOUTE
        for voix in voix_list:
            dispo = [m for m in MODELES if _ok(m, voix, phrase)]
            if not dispo:
                continue
            for m in _tirage_pondere_sans_remise(rnd, dispo, poids, N_MODELES_MOS):
                mid = _hid("mos", voix, phrase, m)
                if mid in solution_mos:
                    continue
                mos.append({
                    "id": mid, "phrase": phrase, "voix": voix,
                    "texte": corpus[phrase]["texte"].strip().replace("\n", " "),
                    "registre": corpus[phrase]["registre"],
                    "clip": f"audio/{clip_id(m, phrase, voix)}.wav",
                    "ref": f"audio/ref_{voix}.wav",
                })
                solution_mos[mid] = {"phrase": phrase, "voix": voix, "modele": m}
    rnd.shuffle(mos)

    # --- mode ÉMOTION : modèle A vs modèle B, même voix `papa_<émotion>` ----
    # Paires tirées PONDÉRÉES équité (plus de chances pour un modèle moins
    # écouté jusqu'ici), avec re-tirage tant qu'on n'a pas `N_PAIRES_EMO`
    # paires distinctes pour cette phrase (ou jusqu'à épuiser les essais).
    emo: list[dict] = []
    solution_emo: dict[str, dict] = {}
    emo_sautes: list[str] = []
    for nom_emo, (voix_emo, phrases_emo, mot) in EMOTIONS.items():
        for phrase in phrases_emo:
            dispo_emo = [m for m in EMO_MODELES if _wav(m, phrase, voix_emo).is_file()]
            obtenues = 0
            essais = 0
            max_essais = N_PAIRES_EMO * 8
            while obtenues < N_PAIRES_EMO and essais < max_essais and len(dispo_emo) >= 2:
                essais += 1
                a = _tirage_pondere(rnd, dispo_emo, poids)
                reste = [m for m in dispo_emo if m != a]
                b = _tirage_pondere(rnd, reste, poids)
                mlo, mhi = sorted((a, b))
                eid = _hid("emo", nom_emo, phrase, mlo, mhi)
                if eid in solution_emo:
                    continue
                m_a, m_b = (mhi, mlo) if _flip(eid) else (mlo, mhi)
                emo.append({
                    "id": eid, "phrase": phrase, "emotion": nom_emo, "voix": voix_emo,
                    "question": f"Lequel rend le mieux l'émotion {mot} ?",
                    "texte": corpus[phrase]["texte"].strip().replace("\n", " "),
                    "registre": corpus[phrase]["registre"],
                    "A": f"audio/{clip_id(m_a, phrase, voix_emo)}.wav",
                    "B": f"audio/{clip_id(m_b, phrase, voix_emo)}.wav",
                })
                solution_emo[eid] = {"phrase": phrase, "emotion": nom_emo,
                                     "voix": voix_emo, "A_modele": m_a, "B_modele": m_b}
                obtenues += 1
            for m in EMO_MODELES:
                if m not in dispo_emo:
                    emo_sautes.append(f"{m}/{nom_emo}/{phrase}")
    rnd.shuffle(emo)
    if emo_sautes:
        print(f"[build_ecoute] {len(emo_sautes)} paires émotion sautées "
              f"(audio manquant) : {', '.join(emo_sautes[:6])}"
              + (" …" if len(emo_sautes) > 6 else ""))

    shutil.copy2(REF_WAV, audio_dir / "ref.wav")
    # réf jouée en MOS (axe similarité) : voix de `VOIX_ECOUTE` + voix
    # émotionnelles utilisées pour les phrases de registre émotionnel.
    for voix in sorted(set(VOIX_ECOUTE) | set(MOS_VOIX_EMO.values())):
        src = RACINE / "corpus" / "voix_reference" / f"{voix}.wav"
        if src.is_file():
            shutil.copy2(src, audio_dir / f"ref_{voix}.wav")

    build_info = {"seed": SEED, "voix": VOIX, "tetes": TETES,
                  "voix_ecoute": VOIX_ECOUTE, "modeles": MODELES,
                  "emo_modeles": EMO_MODELES, "rep": REP,
                  "wer_max_ecoute": WER_MAX_ECOUTE,
                  "combos_exclus": sorted(f"{m}/{v}" for m, v in exclus),
                  "phrases_ab": phrases_ab, "phrases_mos": phrases_mos,
                  "emo_sautes": emo_sautes,
                  "equite_comptes_ecoute": comptes_ecoute, "equite_poids": poids}

    manifest = {
        # côté page : PAS de nom de modèle (test aveugle) — seulement une
        # signature de build pour tracer l'export. `pool_*` = taille des
        # réservoirs ; la page tire ≤ `limite_session` items au hasard,
        # DIFFÉRENTS à chaque session.
        "build": {"seed": SEED, "voix": VOIX, "rep": REP,
                  "limite_session": LIMITE_SESSION, "voix_ecoute": VOIX_ECOUTE,
                  "pool_ab": len(ab), "pool_mos": len(mos), "pool_emo": len(emo)},
        "ref": "audio/ref.wav",
        "defauts": DEFAUTS, "axes_mos": AXES_MOS,
        "ab": ab, "mos": mos, "emo": emo,
    }
    (SORTIE / "manifest.js").write_text(
        "window.MANIFEST = " + json.dumps(manifest, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    # Mapping id -> modèle(s), chargé UNIQUEMENT par le bouton « Afficher les
    # modèles » (déblinde le test — pour vérification locale). Git-ignoré.
    (SORTIE / "solution.js").write_text(
        "window.SOLUTION = " + json.dumps(
            {"ab": solution_ab, "mos": solution_mos, "emo": solution_emo},
            ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    sol_complet = {"build": build_info, "clips": solution_clips,
                   "ab": solution_ab, "mos": solution_mos, "emo": solution_emo}
    (SORTIE / "_solution.json").write_text(
        json.dumps(sol_complet, ensure_ascii=False, indent=1), encoding="utf-8")
    # Archive : garde CHAQUE solution produite (nommée par hash de son
    # contenu). `agreger_ecoute.py` les fusionne → un export d'auditeur
    # reste exploitable même après un changement de pool. Git-ignoré.
    arch = SORTIE / "_solutions"
    arch.mkdir(exist_ok=True)
    empreinte = hashlib.md5(
        json.dumps([sorted(solution_ab), sorted(solution_mos), sorted(solution_emo)],
                   ensure_ascii=False).encode()).hexdigest()[:12]
    (arch / f"{empreinte}.json").write_text(
        json.dumps({"ab": solution_ab, "mos": solution_mos, "emo": solution_emo},
                   ensure_ascii=False),
        encoding="utf-8",
    )
    from collections import Counter
    cv_ab = Counter(v["voix"] for v in solution_ab.values())
    cv_mos = Counter(v["voix"] for v in solution_mos.values())
    mo = sum(f.stat().st_size for f in audio_dir.glob("*.wav")) / 1e6
    print(f"[build_ecoute] pools : {len(ab)} paires A/B, {len(mos)} clips MOS, "
          f"{len(emo)} paires ÉMOTION → la page tire ≤{LIMITE_SESSION} / session")
    print(f"[build_ecoute] A/B par voix : "
          + "  ".join(f"{v.replace('_narration','')}={cv_ab[v]}/{cv_mos[v]}" for v in VOIX_ECOUTE)
          + "  (paires/clips MOS)")
    if exclus:
        print(f"[build_ecoute] combos exclus (WER>{WER_MAX_ECOUTE:.0%}) : "
              + ", ".join(sorted(f"{m}/{v}" for m, v in exclus)))
    print(f"[build_ecoute] {len(clips)+1} fichiers audio ({mo:.0f} Mo) -> {SORTIE}")
    print(f"[build_ecoute] ouvre  {SORTIE / 'index.html'}  (double-clic)")


if __name__ == "__main__":
    build()
