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
           "xtts_v2", "moss_tts_local_v15"]
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
               "cosyvoice3_05b", "xtts_v2"]
EMO_COMBOS = [(0, 1), (2, 3), (4, 5), (1, 4), (0, 3), (2, 5)]  # couvre les 6, paires variées
EMOTIONS = {                       # émotion -> (voix de réf, phrases, mot pour la question)
    "joie":      ("papa_joie",      ["p01", "p06"],                      "JOYEUX / ENTHOUSIASTE"),
    "colere":    ("papa_colere",    ["p02", "p07", "p19", "p22", "p33"], "EN COLÈRE"),
    "peur":      ("papa_peur",      ["p03", "p08", "p34"],               "APEURÉ / INQUIET"),
    "tristesse": ("papa_tristesse", ["p04", "p09"],                      "TRISTE"),
}

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
    #   1) une tête (alternée) vs un challenger (tournant) ;
    #   2) 1 phrase / 2 : duel des têtes ; l'autre : challenger vs challenger ;
    #   + N_PAIRES_ALEA paires aléatoires / voix.
    # Un combo (modèle, voix) au WER > seuil (clip cassé) est sauté.
    challengers = [m for m in MODELES if m not in TETES]
    nc = len(challengers)
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
        k2 = 0
        for i, phrase in enumerate(phrases_ab):
            _ajouter(voix, phrase, TETES[(i + i // nc) % 2], challengers[i % nc])
            if i % 2 == 0:
                _ajouter(voix, phrase, TETES[0], TETES[1])
            else:
                _ajouter(voix, phrase, challengers[k2 % nc], challengers[(k2 + 1) % nc])
                k2 += 1
        for _ in range(N_PAIRES_ALEA * 6):
            phrase = rnd.choice(phrases_ab)
            a, b = rnd.sample(MODELES, 2)
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

    # --- clips MOS, PAR VOIX : 2 modèles tournants par phrase ------------
    mos: list[dict] = []
    solution_mos: dict[str, dict] = {}
    for voix in VOIX_ECOUTE:
        for i, phrase in enumerate(phrases_mos):
            dispo = [m for m in MODELES if _ok(m, voix, phrase)]
            if not dispo:
                continue
            for j in range(N_MODELES_MOS):
                m = dispo[(N_MODELES_MOS * i + j) % len(dispo)]
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
    emo: list[dict] = []
    solution_emo: dict[str, dict] = {}
    emo_sautes: list[str] = []
    rot = 0
    for nom_emo, (voix_emo, phrases_emo, mot) in EMOTIONS.items():
        for phrase in phrases_emo:
            for j in range(N_PAIRES_EMO):
                ia, ib = EMO_COMBOS[(rot + j) % len(EMO_COMBOS)]
                a, b = EMO_MODELES[ia], EMO_MODELES[ib]
                if a == b:
                    continue
                if not (_wav(a, phrase, voix_emo).is_file()
                        and _wav(b, phrase, voix_emo).is_file()):
                    emo_sautes.append(f"{a}|{b}/{nom_emo}/{phrase}")
                    continue
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
            rot += N_PAIRES_EMO
    rnd.shuffle(emo)
    if emo_sautes:
        print(f"[build_ecoute] {len(emo_sautes)} paires émotion sautées "
              f"(audio manquant) : {', '.join(emo_sautes[:6])}"
              + (" …" if len(emo_sautes) > 6 else ""))

    shutil.copy2(REF_WAV, audio_dir / "ref.wav")
    for voix in VOIX_ECOUTE:                      # réf jouée en MOS, par voix
        src = RACINE / "corpus" / "voix_reference" / f"{voix}.wav"
        if src.is_file():
            shutil.copy2(src, audio_dir / f"ref_{voix}.wav")

    build_info = {"seed": SEED, "voix": VOIX, "tetes": TETES,
                  "voix_ecoute": VOIX_ECOUTE, "modeles": MODELES,
                  "emo_modeles": EMO_MODELES, "rep": REP,
                  "wer_max_ecoute": WER_MAX_ECOUTE,
                  "combos_exclus": sorted(f"{m}/{v}" for m, v in exclus),
                  "phrases_ab": phrases_ab, "phrases_mos": phrases_mos,
                  "emo_sautes": emo_sautes}

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
