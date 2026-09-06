#!/usr/bin/env python3
"""Rapport d'un modèle : agrège scoring + vitesse + stabilité par voix.

Lit `<modele-dir>/<voix>/{transcriptions.csv, timings.csv, meta.json}`
(produits par l'adaptateur + `transcrire.py`), croise avec le corpus, et
écrit un JSON + un Markdown.

    source env.sh
    python3 benchmark/rapport.py --modele-dir "$TTSB_AUDIO_OUT/chatterbox_v3" \
        --out resultats/chatterbox_v3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.corpus import charger_corpus  # noqa: E402
from benchmark.evaluer import evaluer_runs, synthese  # noqa: E402
from benchmark.mesurer_vitesse import agreger_vitesse, charger_timings  # noqa: E402
from benchmark.mesurer_perceptuel import lire_perceptuel  # noqa: E402
from benchmark.stabilite import stabilite_duree  # noqa: E402
from benchmark.transcrire import lire_transcriptions  # noqa: E402


def rapport_voix(dossier_voix: Path, phrases, *, plancher_wer: float = 0.0) -> dict:
    f_perc = dossier_voix / "perceptuel.csv"
    perc = lire_perceptuel(f_perc) if f_perc.is_file() else None
    lignes = evaluer_runs(
        lire_transcriptions(dossier_voix / "transcriptions.csv"), phrases, perceptuel=perc
    )
    timings = charger_timings(dossier_voix / "timings.csv")
    meta = json.loads((dossier_voix / "meta.json").read_text(encoding="utf-8"))
    return {
        "meta": meta,
        "synthese": synthese(lignes, plancher_wer=plancher_wer),
        "vitesse": agreger_vitesse(timings),
        "stabilite": stabilite_duree(timings),
        "lignes": lignes,
    }


def rapport_modele(dossier_modele: Path, *, plancher_wer: float = 0.0) -> dict:
    phrases = charger_corpus()
    voix = [d for d in sorted(dossier_modele.iterdir()) if d.is_dir()
            and (d / "transcriptions.csv").is_file()]
    if not voix:
        raise SystemExit(f"[FAIL] aucune voix scorable dans {dossier_modele}")
    return {d.name: rapport_voix(d, phrases, plancher_wer=plancher_wer) for d in voix}


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def markdown(nom_modele: str, rap: dict) -> str:
    L: list[str] = [f"# Benchmark — {nom_modele}", ""]

    L.append("## Vue globale (par voix)")
    L.append("")
    L.append("| voix | runs ok | WER moyen | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for voix, r in rap.items():
        s, v, st = r["synthese"], r["vitesse"], r["stabilite"]
        vram = max((x.get("vram_pic_mo") or 0 for x in r.get("_timings", [])), default=0)
        utmos = f"{s['utmos_moyen']:.2f}" if s.get("utmos_moyen") is not None else "—"
        sim = f"{s['sim_moyen']:.3f}" if s.get("sim_moyen") is not None else "—"
        L.append(
            f"| {voix} | {s['n_verifiees']}/{s['n_runs']} | {_pct(s['wer_moyen'])} | "
            f"{_pct(s['wer_ecart_type'])} | {utmos} | {sim} | {_pct(s['taux_hallucination'])} | "
            f"{_pct(s['taux_repetition'])} | {_pct(s['taux_troncature'])} | "
            f"{v['global']['rtf']['moyenne']:.2f} | {vram or '?'} Mo | "
            f"{_pct(st['cv_median'])} |"
        )
    L.append("")

    for voix, r in rap.items():
        s = r["synthese"]
        L.append(f"## {voix} — WER par catégorie")
        L.append("")
        for axe, titre in (("wer_par_longueur", "longueur"),
                           ("wer_par_registre", "registre"),
                           ("wer_par_piege", "piège")):
            L.append(f"**Par {titre}**")
            L.append("")
            L.append(f"| {titre} | n | WER moyen |")
            L.append("|---|---|---|")
            for k, b in s[axe].items():
                L.append(f"| {k} | {b['n']} | {_pct(b['wer_moyen'])} |")
            L.append("")
        for cle, titre in (("phrases_hallucination", "Hallucination"),
                           ("phrases_repetition", "Répétition"),
                           ("phrases_troncature", "Troncature")):
            if s[cle]:
                L.append(f"**{titre} détectée sur** : {', '.join(s[cle])}")
                L.append("")
        if r["stabilite"]["n_suspects"]:
            sus = [p for p, x in r["stabilite"]["par_phrase"].items() if x["suspect"]]
            L.append(f"**Durée instable (CV > seuil)** : {', '.join(sus)}")
            L.append("")

    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modele-dir", required=True)
    p.add_argument("--out", default="", help="préfixe de sortie (défaut : resultats/<nom>)")
    p.add_argument("--plancher-wer", type=float, default=0.0)
    args = p.parse_args()

    dossier = Path(args.modele_dir)
    nom = dossier.name
    out = Path(args.out) if args.out else Path("resultats") / nom
    out.parent.mkdir(parents=True, exist_ok=True)

    rap = rapport_modele(dossier, plancher_wer=args.plancher_wer)
    for voix, r in rap.items():
        r["_timings"] = charger_timings(dossier / voix / "timings.csv")

    (out.with_suffix(".json")).write_text(
        json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "_timings"}
                    for k, v in rap.items()},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = markdown(nom, rap)
    out.with_suffix(".md").write_text(md, encoding="utf-8")
    print(md)
    print(f"\n-> {out.with_suffix('.json')}\n-> {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
