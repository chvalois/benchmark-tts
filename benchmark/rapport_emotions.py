#!/usr/bin/env python3
"""Régénère `resultats/EMOTIONS.md` à partir des `resultats/<modele>.json`.

Le run émotions : chaque voix de référence émotionnelle
(`papa_{joie,colere,peur,tristesse}`) ne génère que les phrases de dialogue
de son registre (joie : p01,p06 · colère : p02,p07,p19,p22,p33 · peur :
p03,p08,p34 · tristesse : p04,p09), 3 reps. Kokoro est exclu (voix interne,
pas de clonage). On vérifie que l'émotion ne casse ni l'intelligibilité
(WER) ni l'identité (SIM), et on regarde la NISQA (TTSDS2 inexploitable
sur 6–15 clips).

    source env.sh
    python3 benchmark/rapport_emotions.py           # tous les resultats/*.json
    python3 benchmark/rapport_emotions.py resultats/firered_tts3.json ...
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
RESULTATS = RACINE / "resultats"
SORTIE = RESULTATS / "EMOTIONS.md"
VOIX_EMO = ("papa_joie", "papa_colere", "papa_peur", "papa_tristesse")

ENTETE = """# Run émotions — voix de référence émotionnelle → phrases du registre

Chaque voix de référence (`papa_joie/colere/peur/tristesse`) ne génère que
les phrases de dialogue de son registre (joie : p01,p06 · colère :
p02,p07,p19,p22,p33 · peur : p03,p08,p34 · tristesse : p04,p09), 3 reps.
Kokoro exclu (pas de clonage). Question testée (APIAVISOL §3.5) : **cloner
une voix de référence émotionnelle transporte-t-il l'émotion ?** — réponse
surtout à l'écoute (voir le mode ÉMOTION du test `site/ecoute/`) ; ici on
vérifie que l'émotion ne casse pas l'intelligibilité (WER) ni l'identité
(SIM), et on regarde la NISQA (TTSDS2, distributionnel, est inexploitable
sur 6–15 clips).

Audio : `D:\\tts-benchmark-data\\audio_genere\\<modèle>\\papa_<émotion>\\`.

Métriques **automatiques** : WER (whisper-large-v3-french), fidélité
language-agnostic, **NISQA** (naturalité prédite NISQA-TTS, ↑ mieux ~1–5),
**SIM** (similarité au locuteur de réf émotionnel, ECAPA, ↑ mieux). **Pas
encore d'écoute MOS humaine.** WER brut (aucun plancher humain soustrait).
"""

PIED = """
- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).
- **NISQA** ~1–5 (NISQA-TTS) — biais anglophone connu, en contre-vérification.
- **SIM** = cosinus embeddings **ECAPA-TDNN** gén. vs voix de réf émotionnelle (0–1).
- **CV durée** = écart-type / moyenne de la durée sur les 3 reps (stabilité).
- Détail par catégorie + WER par piège : `resultats/<modele>.md`.
"""


def _lignes(chemins: list[Path]) -> list[dict]:
    out: list[dict] = []
    for chemin in sorted(chemins):
        data = json.loads(chemin.read_text(encoding="utf-8"))
        for voix, r in data.items():
            if voix not in VOIX_EMO:
                continue
            s = r["synthese"]
            out.append({
                "modele": chemin.stem,
                "voix": voix,
                "wer": s["wer_moyen"],
                "sigma": s["wer_ecart_type"],
                # TTSDS2 (distributionnel) inexploitable sur 6–15 clips émotion
                # -> on garde NISQA (par énoncé) pour la naturalité ici.
                "nisqa": s.get("nisqa_moyen"),
                "sim": s.get("sim_moyen"),
                "hallu": s["taux_hallucination"],
                "rep": s["taux_repetition"],
                "tronc": s["taux_troncature"],
                "rtf": r["vitesse"]["global"]["rtf"]["moyenne"],
                "cv": r["stabilite"]["cv_median"],
            })
    return out


def _f(x, suffixe="", digits=2) -> str:
    if x is None:
        return "—"
    if suffixe == "%":
        return f"{x * 100:.1f}%"
    return f"{x:.{digits}f}"


def construire(chemins: list[Path]) -> str:
    lignes = sorted(_lignes(chemins), key=lambda d: (d["wer"], d["modele"], d["voix"]))
    L = [ENTETE, ""]
    L.append("| modèle | voix | clon. | WER | ±σ | NISQA | SIM | hallu. | rép. | tronc. | RTF | CV dur. |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for d in lignes:
        L.append(
            f"| {d['modele']} | {d['voix']} | oui | {_f(d['wer'], '%')} | {_f(d['sigma'], '%')} | "
            f"{_f(d['nisqa'])} | {_f(d['sim'], digits=3)} | {_f(d['hallu'], '%')} | {_f(d['rep'], '%')} | "
            f"{_f(d['tronc'], '%')} | {_f(d['rtf'])} | {_f(d['cv'], '%')} |"
        )
    n_modeles = len({d["modele"] for d in lignes})
    L.append("")
    L.append(f"*{len(lignes)} lignes — {n_modeles} modèles × 4 registres émotionnels.*")
    L.append(PIED)
    return "\n".join(L)


def main(argv: list[str]) -> int:
    chemins = [Path(a) for a in argv] or sorted(RESULTATS.glob("*.json"))
    chemins = [c for c in chemins if c.is_file()]
    if not chemins:
        sys.exit("[FAIL] aucun resultats/*.json — lance d'abord rapport.py")
    md = construire(chemins)
    SORTIE.write_text(md, encoding="utf-8")
    print(md)
    print(f"\n-> {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
