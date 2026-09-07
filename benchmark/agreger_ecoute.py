#!/usr/bin/env python3
"""Agrège les exports du test d'écoute (`site/ecoute/`).

Dé-anonymise via `_solution.json` puis produit :
- **A/B** : win-rate par modèle (victoires + ½ nuls), matrice des duels,
  défauts entendus attribués au bon modèle ;
- **MOS** : moyenne ± IC 95 % par modèle et par axe ;
- **corrélations** MOS ↔ métriques auto (par clip) : naturel↔UTMOS,
  intelligibilité↔(1−WER), similarité↔SIM.

    source env.sh
    python3 benchmark/agreger_ecoute.py exports/*.json --out resultats/ecoute.md
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOLUTION = RACINE / "site" / "ecoute" / "_solution.json"
RESULTATS = RACINE / "resultats"
AXES = ["naturel", "intelligibilite", "similarite", "expressivite"]


def _moy_ic(xs: list[float]) -> tuple[float, float, int]:
    n = len(xs)
    if n == 0:
        return 0.0, 0.0, 0
    m = sum(xs) / n
    if n < 2:
        return m, 0.0, n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))
    return m, 1.96 * sd / math.sqrt(n), n


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx == 0 or syy == 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def _lignes_objectives() -> dict[tuple[str, str, int], dict]:
    """(modele, phrase, rep) -> {wer, utmos, sim} depuis resultats/*.json."""
    out: dict[tuple[str, str, int], dict] = {}
    for f in RESULTATS.glob("*.json"):
        modele = f.stem
        for _voix, r in json.loads(f.read_text(encoding="utf-8")).items():
            for l in r.get("lignes", []):
                out[(modele, l["id_phrase"], l["repetition"])] = {
                    "wer": l["wer"], "utmos": l.get("utmos"), "sim": l.get("sim"),
                }
    return out


def agreger(exports: list[Path]) -> str:
    sol = json.loads(SOLUTION.read_text(encoding="utf-8"))
    obj = _lignes_objectives()
    L: list[str] = ["# Test d'écoute — agrégation", ""]

    ab_votes, mos_votes = [], []
    auditeurs = set()
    for f in exports:
        d = json.loads(f.read_text(encoding="utf-8"))
        auditeurs.add(d.get("pseudo", f.stem))
        (ab_votes if d.get("mode") == "ab" else mos_votes).extend(
            {**v, "_pseudo": d.get("pseudo")} for v in d.get("votes", []) if v.get("id")
        )

    # Panel anonymisé : seul le nombre d'auditeurs est publié, pas les pseudos.
    L.append(f"{len(auditeurs)} auditeur(s)  "
             f"— {len(ab_votes)} votes A/B, {len(mos_votes)} notes MOS.\n")

    # ---------- A/B ----------
    if ab_votes:
        stats = defaultdict(lambda: {"v": 0, "n": 0, "d": 0})
        duel = defaultdict(lambda: [0, 0])          # (m1,m2) trié -> [gagne m1, gagne m2]
        defauts = defaultdict(lambda: defaultdict(int))
        for v in ab_votes:
            s = sol["ab"].get(v["id"])
            if not s or not v.get("choix"):
                continue
            ma, mb = s["A_modele"], s["B_modele"]
            for m in (ma, mb):
                stats[m]["n"] += 1
            if v["choix"] == "A":
                stats[ma]["v"] += 1
            elif v["choix"] == "B":
                stats[mb]["v"] += 1
            else:
                stats[ma]["v"] += 0.5
                stats[mb]["v"] += 0.5
            k = tuple(sorted((ma, mb)))
            if v["choix"] in ("A", "B"):
                gagnant = ma if v["choix"] == "A" else mb
                duel[k][0 if gagnant == k[0] else 1] += 1
            for side, m in (("A", ma), ("B", mb)):
                for dk in v.get(f"def_{side}", []):
                    defauts[m][dk] += 1
                    stats[m]["d"] += 1

        L.append("## A/B — win-rate par modèle\n")
        L.append("| modèle | win-rate | (victoires / duels) | défauts entendus |")
        L.append("|---|---|---|---|")
        for m, s in sorted(stats.items(), key=lambda kv: -kv[1]["v"] / max(1, kv[1]["n"])):
            wr = s["v"] / s["n"] if s["n"] else 0
            det = " ".join(f"{k}:{n}" for k, n in sorted(defauts[m].items(), key=lambda x: -x[1])) or "—"
            L.append(f"| {m} | {wr:.0%} | {s['v']:.1f} / {s['n']} | {det} |")
        L.append("")
        L.append("## A/B — matrice des duels (gauche bat haut)\n")
        modeles = sorted({m for k in duel for m in k})
        L.append("| | " + " | ".join(modeles) + " |")
        L.append("|" + "---|" * (len(modeles) + 1))
        for a in modeles:
            cells = []
            for b in modeles:
                if a == b:
                    cells.append("·")
                    continue
                k = tuple(sorted((a, b)))
                ga, gb = duel.get(k, [0, 0])
                wins = ga if k[0] == a else gb
                tot = ga + gb
                cells.append(f"{wins}/{tot}" if tot else "—")
            L.append(f"| **{a}** | " + " | ".join(cells) + " |")
        L.append("")

    # ---------- MOS ----------
    if mos_votes:
        par = defaultdict(lambda: defaultdict(list))    # modele -> axe -> [notes]
        corr_pts = defaultdict(lambda: ([], []))        # (axe_h, metrique) -> (xs, ys)
        for v in mos_votes:
            s = sol["mos"].get(v["id"])
            if not s:
                continue
            m, phrase = s["modele"], s["phrase"]
            for a in AXES:
                if v.get(a) is not None:
                    par[m][a].append(float(v[a]))
            o = obj.get((m, phrase, sol["build"]["rep"]))
            if o:
                if v.get("naturel") is not None and o["utmos"] is not None:
                    xs, ys = corr_pts[("naturel", "UTMOS")]
                    xs.append(float(v["naturel"])); ys.append(o["utmos"])
                if v.get("intelligibilite") is not None:
                    xs, ys = corr_pts[("intelligibilite", "1-WER")]
                    xs.append(float(v["intelligibilite"])); ys.append(1 - o["wer"])
                if v.get("similarite") is not None and o["sim"] is not None:
                    xs, ys = corr_pts[("similarite", "SIM")]
                    xs.append(float(v["similarite"])); ys.append(o["sim"])

        L.append("## MOS — moyenne ± IC 95 % par axe\n")
        L.append("| modèle | " + " | ".join(a.capitalize() for a in AXES) + " |")
        L.append("|" + "---|" * (len(AXES) + 1))
        for m in sorted(par):
            cells = []
            for a in AXES:
                mo, ic, n = _moy_ic(par[m][a])
                cells.append(f"{mo:.2f} ±{ic:.2f}" if n else "—")
            L.append(f"| {m} | " + " | ".join(cells) + " |")
        L.append("")
        L.append("## Corrélation MOS (humain) ↔ métrique automatique (par clip)\n")
        L.append("| axe humain | métrique auto | Pearson r | n |")
        L.append("|---|---|---|---|")
        for (ah, met), (xs, ys) in corr_pts.items():
            r = _pearson(xs, ys)
            L.append(f"| {ah} | {met} | {r:.2f} | {len(xs)} |" if r is not None
                     else f"| {ah} | {met} | n/a | {len(xs)} |")
        L.append("")

    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("exports", nargs="+", help="fichiers ecoute_*.json des auditeurs")
    p.add_argument("--out", default="resultats/ecoute.md")
    args = p.parse_args()
    if not SOLUTION.is_file():
        raise SystemExit(f"[FAIL] {SOLUTION} absent — lance d'abord build_ecoute.py")
    md = agreger([Path(e) for e in args.exports])
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(md, encoding="utf-8")
    print(md)
    print(f"\n-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
