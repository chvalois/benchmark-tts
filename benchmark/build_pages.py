#!/usr/bin/env python3
"""Génère le site de résultats statique (`site/resultats/`).

- `index.html`    : page projet — classement (auto + écoute) + méthode.
- `objectif.html` : table complète des métriques auto, **toutes voix
  confondues** (moyenne pondérée par le nb de runs), triable, détail par
  modèle (WER par longueur / registre / piège).
- `ecoute.html`   : les 3 protocoles du test d'écoute humain, à partir de
  `resultats/ecoute.json`.
- `modele-<nom>.html` : une fiche de vulgarisation par modèle scoré —
  particularité, choix techniques, mesures, sources (registre déclaré
  `benchmark/fiches_modeles.yaml`, validé par `benchmark/fiches.py`).

Pages autonomes (données injectées, Google Fonts) — ouvrables en `file://`.
**Aucun nom de voix de référence ni de participant** : que des agrégats.

    source env.sh
    python3 benchmark/build_pages.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # lancé en script

RACINE = Path(__file__).resolve().parent.parent
RESULTATS = RACINE / "resultats"
LICENCES = RACINE / "benchmark" / "licences.yaml"
MODELS_LOCK = RACINE / "models.lock"
SORTIE = RACINE / "site" / "resultats"
REPO = "https://github.com/chvalois/benchmark-tts"

# Noms d'affichage (les slugs `resultats/*.json` sont techniques).
NOM_MODELE = {
    "firered_tts3": "FireRed TTS3", "voxcpm2": "VoxCPM2",
    "chatterbox_v3": "Chatterbox v3", "cosyvoice3_05b": "CosyVoice3-0.5B",
    "xtts_v2": "XTTS-v2", "moss_tts_local_v15": "MOSS-1.5",
    "kokoro_82m": "Kokoro-82M", "f5_tts": "F5-TTS",
    "omnivoice": "OmniVoice", "audio8_06b": "Audio8-TTS-0.6B",
}


def _nm(slug: str) -> str:
    return NOM_MODELE.get(slug, slug)


# Défauts signalables par l'auditeur·rice sur un clip A/B (cf.
# `benchmark/build_ecoute.py::DEFAUTS` — labels dupliqués ici volontairement,
# c'est la seule page qui en a besoin).
DEFAUT_LABELS = {
    "tronque": "coupé / tronqué",
    "repetition": "répétition / bégaiement",
    "voix_diff": "voix ne ressemble pas à la référence",
    "accent": "accent / prononciation non française",
    "artefact": "artefact / bruit / robotique",
}
DEFAUT_LABELS_COURT = {
    "tronque": "tronqué", "repetition": "répétition", "voix_diff": "voix≠réf",
    "accent": "accent", "artefact": "artefact",
}
DEFAUT_COULEURS = {
    "tronque": "#c0533f", "repetition": "#c98a3c", "voix_diff": "#6f7fd1",
    "accent": "#3f8fc4", "artefact": "#9a63b0",
}
EMOTION_LABELS = {"joie": "Joie", "colere": "Colère", "peur": "Peur", "tristesse": "Tristesse"}


# Modèles présents dans resultats/*.json mais retirés de l'agrégation —
# le motif affiché vient du `statut` posé dans models.lock (source de
# vérité unique : pas de liste d'exclusion dupliquée ici).
STATUT_MOTIF = {
    "fr_non_supporte": "FR non supporté",
    "retire_benchmark": "retiré du benchmark",
}

# --------------------------------------------------------------------------
# Spéc. des métriques — sens (↓ = plus bas meilleur, ↑ = plus haut meilleur,
# 0 = neutre), format, et seuils bon / à-surveiller pour le code couleur.
# --------------------------------------------------------------------------
M = {
    "clonage":   dict(label="clon.",    dir=0,  fmt="oui",  g=None, b=None),
    "wer":       dict(label="WER",      dir=-1, fmt="pct",  g=.05,  b=.10),
    "wer_sigma": dict(label="±σ",       dir=-1, fmt="pct",  g=.08,  b=.15),
    "wer_net":   dict(label="WER net",  dir=-1, fmt="pct",  g=.04,  b=.09),
    "sim":       dict(label="SIM",      dir=1,  fmt="num3", g=.80,  b=.72),
    "hallu":     dict(label="hallu.",   dir=-1, fmt="pct",  g=.001, b=.05),
    "rep":       dict(label="rép.",     dir=-1, fmt="pct",  g=.001, b=.05),
    "tronc":     dict(label="tronc.",   dir=-1, fmt="pct",  g=.001, b=.05),
    "anom":      dict(label="anomalies", dir=-1, fmt="pct", g=.001, b=.05),
    "rtf":       dict(label="RTF",      dir=0,  fmt="x",    g=.60,  b=1.50),
    "ttfa":      dict(label="TTFA s",   dir=-1, fmt="num2", g=2.0,  b=8.0),
    "cv":        dict(label="CV durée", dir=-1, fmt="pct",  g=.10,  b=.15),
    "vram_go":   dict(label="VRAM~",    dir=0,  fmt="int",  g=6,    b=12),
}


def _fmt(k: str, x) -> str:
    if x is None:
        return "—"
    f = M.get(k, {}).get("fmt", "plain")
    if f == "pct":
        return f"{x*100:.1f}%"
    if f == "num2":
        return f"{x:.2f}"
    if f == "num3":
        return f"{x:.3f}"
    if f == "x":
        return f"{x:.2f}\u00d7"
    if f == "int":
        return str(x)
    if f == "oui":
        return "oui" if x else "non"
    return str(x)


def _cls(k: str, x) -> str:
    """classe couleur : m-good / m-mid / m-bad / '' (neutre)."""
    spec = M.get(k)
    if not spec or x is None or spec["dir"] == 0 or spec["g"] is None:
        return ""
    g, b = spec["g"], spec["b"]
    if spec["dir"] == -1:                     # plus bas = mieux
        return "m-good" if x <= g else ("m-bad" if x >= b else "m-mid")
    return "m-good" if x >= g else ("m-bad" if x <= b else "m-mid")   # plus haut = mieux


CSS = """
:root{
  --bg:#f7f6f2; --panel:#ffffff; --panel2:#f1efe8; --line:#e3ded2;
  --ink:#1b1f1e; --muted:#66706e; --faint:#9aa19d;
  --trace:#14806f; --trace-soft:#dcefe9;
  --ok:#2f8a44; --warn:#a9791b; --crit:#b8443b;
  --shadow:0 1px 2px rgba(20,30,28,.06),0 8px 24px -12px rgba(20,30,28,.14);
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0e1214; --panel:#151b1d; --panel2:#101617; --line:#242e30;
  --ink:#dfe6e3; --muted:#8f9c99; --faint:#5c6a68;
  --trace:#6fd0c0; --trace-soft:#16302c;
  --ok:#6bbf73; --warn:#d6a447; --crit:#d9695f;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 12px 32px -14px rgba(0,0,0,.55);
}}
:root[data-theme="dark"]{
  --bg:#0e1214; --panel:#151b1d; --panel2:#101617; --line:#242e30;
  --ink:#dfe6e3; --muted:#8f9c99; --faint:#5c6a68;
  --trace:#6fd0c0; --trace-soft:#16302c;
  --ok:#6bbf73; --warn:#d6a447; --crit:#d9695f;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 12px 32px -14px rgba(0,0,0,.55);
}

*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:15.5px;line-height:1.6;-webkit-font-smoothing:antialiased}
::selection{background:var(--trace);color:var(--bg)}
a{color:inherit;text-decoration:none}
a.link{color:var(--trace);text-decoration:underline;text-underline-offset:2px;
  text-decoration-thickness:1px;
  text-decoration-color:color-mix(in oklab,var(--trace) 45%,transparent)}
a.link:hover{text-decoration-color:var(--trace)}
.mono{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  font-variant-numeric:tabular-nums}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}

/* header */
header.bar{position:sticky;top:0;z-index:20;
  background:color-mix(in oklab,var(--bg) 86%,transparent);
  backdrop-filter:saturate(1.4) blur(8px);border-bottom:1px solid var(--line)}
header.bar .wrap{display:flex;align-items:center;gap:14px;height:56px}
.brand{font-family:"Newsreader",Georgia,serif;font-size:1.1rem;font-weight:500;
  display:flex;align-items:center;gap:8px;white-space:nowrap}
.brand .fr{font:500 .6rem/1 "IBM Plex Mono",monospace;letter-spacing:.14em;
  color:var(--trace);border:1px solid color-mix(in oklab,var(--trace) 40%,var(--line));
  border-radius:4px;padding:3px 5px 2px;text-transform:uppercase}
header.bar nav{margin-left:auto;display:flex;align-items:center;gap:2px}
header.bar nav .navliens{display:flex;align-items:center;gap:2px}
header.bar nav a{font-size:.84rem;color:var(--muted);padding:7px 9px;border-radius:7px}
header.bar nav a:hover{color:var(--ink)}
header.bar nav a.on{color:var(--ink);background:var(--panel2)}
.tgl,.burger{width:32px;height:32px;display:grid;place-items:center;border-radius:7px;
  border:1px solid var(--line);background:var(--panel);color:var(--muted);cursor:pointer;
  font:inherit;line-height:1;padding:0}
.tgl{margin-left:4px}
.tgl:hover,.burger:hover{color:var(--ink)}
.burger{display:none;margin-left:6px}
.burger .bg{display:block;width:15px;height:1.5px;background:currentColor;border-radius:2px;
  position:relative;transition:transform .18s ease,opacity .18s ease}
.burger .bg::before,.burger .bg::after{content:"";position:absolute;left:0;width:15px;
  height:1.5px;background:currentColor;border-radius:2px;
  transition:transform .18s ease,top .18s ease}
.burger .bg::before{top:-5px} .burger .bg::after{top:5px}
.burger[aria-expanded="true"] .bg{background:transparent}
.burger[aria-expanded="true"] .bg::before{top:0;transform:rotate(45deg)}
.burger[aria-expanded="true"] .bg::after{top:0;transform:rotate(-45deg)}

/* --- mobile : les liens passent dans un menu déroulant (hamburger) --- */
@media (max-width:620px){
  .burger{display:grid}
  header.bar nav .navliens{position:absolute;top:100%;left:0;right:0;
    flex-direction:column;align-items:stretch;gap:0;
    background:var(--bg);border-bottom:1px solid var(--line);
    box-shadow:var(--shadow);padding:6px 16px 12px;display:none}
  header.bar nav .navliens.ouvert{display:flex}
  header.bar nav .navliens a{font-size:.98rem;padding:13px 10px;border-radius:8px}
  header.bar nav .navliens a+a{border-top:1px solid var(--line)}
  header.bar nav .navliens a.on{background:var(--panel2)}
}

/* hero */
.hero{padding:48px 0 36px;border-bottom:1px solid var(--line)}
.eyebrow{font:500 .7rem/1 "IBM Plex Mono",monospace;letter-spacing:.2em;
  text-transform:uppercase;color:var(--trace);margin-bottom:16px}
.hero h1{font-family:"Newsreader",Georgia,serif;font-weight:400;
  font-size:clamp(1.9rem,6vw,3.1rem);line-height:1.08;letter-spacing:-.012em;
  text-wrap:balance;margin:0 0 14px;max-width:16ch}
.hero .thesis{font-size:1.02rem;color:var(--muted);margin:0 0 24px}
.hero .thesis em{font-family:"Newsreader",serif;font-style:italic;color:var(--ink)}
.scope{margin-top:30px;border:1px solid var(--line);border-radius:12px;
  background:var(--panel);padding:16px 16px 8px;box-shadow:var(--shadow);overflow-x:auto}
.scope .cap{font:.7rem/1 "IBM Plex Mono",monospace;letter-spacing:.1em;
  text-transform:uppercase;color:var(--faint);margin-bottom:10px}

main .wrap{padding-top:44px;padding-bottom:20px}
section+section{margin-top:48px}
section[id],[id="top"]{scroll-margin-top:72px}
.sec-h{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:16px}
.sec-h h2{font-family:"Newsreader",serif;font-weight:500;font-size:1.45rem;
  letter-spacing:-.01em;margin:0}
.sec-h .n{font:.7rem/1 "IBM Plex Mono",monospace;color:var(--faint);letter-spacing:.08em}
.lead{color:var(--muted);margin:-4px 0 18px;font-size:.95rem}
.lead p{margin:0 0 .7em}
.lead p:last-child{margin-bottom:0}

/* --- table --- */
.tools{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
select{font:inherit;font-size:.9rem;border:1px solid var(--line);background:var(--panel);
  color:var(--ink);border-radius:8px;padding:8px 11px}
.legend{display:flex;gap:14px;flex-wrap:wrap;font:.74rem/1 "IBM Plex Mono",monospace;
  color:var(--muted);margin-bottom:12px}
.legend b{font-weight:400;display:inline-flex;align-items:center;gap:6px}
.legend i{width:11px;height:11px;border-radius:3px;display:inline-block}
.sw-g{background:color-mix(in oklab,var(--ok) 55%,var(--panel))}
.sw-m{background:color-mix(in oklab,var(--warn) 55%,var(--panel))}
.sw-b{background:color-mix(in oklab,var(--crit) 60%,var(--panel))}

.board{border:1px solid var(--line);border-radius:12px;background:var(--panel);
  box-shadow:var(--shadow);overflow:hidden}
.tablewrap{overflow-x:auto}
table.rt{border-collapse:collapse;width:100%}
.rt thead th{background:var(--panel);
  font:500 .66rem/1.3 "IBM Plex Mono",monospace;letter-spacing:.05em;
  text-transform:uppercase;color:var(--muted);text-align:right;
  padding:12px 12px;border-bottom:1px solid var(--line);cursor:pointer;
  white-space:nowrap;user-select:none}
.rt thead th:first-child,.rt thead th.name{text-align:left}
.rt thead th.rk{text-align:center;width:40px;cursor:default}
.rt thead th:hover:not(.rk){color:var(--ink)}
.rt thead th .hlabel{border-bottom:1px dotted var(--faint);cursor:help}
.rt thead th .ar{color:var(--faint);font-weight:400;margin-left:3px}
.rt thead th[data-active] .ar{color:var(--trace)}
.rt tbody td{padding:12px;border-bottom:1px solid var(--line);text-align:right;
  font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums;
  font-size:.88rem;white-space:nowrap}
.rt tbody tr:last-child td{border-bottom:0}
.rt td.name{font-family:"IBM Plex Sans",sans-serif;font-weight:500;font-size:.96rem;text-align:left}
.rt td.name a{border-bottom:1px solid transparent}
.rt td.name a:hover{border-bottom-color:var(--trace)}
.rt td.name .sub{display:block;font:.7rem/1.3 "IBM Plex Mono",monospace;
  color:var(--faint);margin-top:3px;font-weight:400}
.rt td.rk{text-align:center;color:var(--faint)}
.rt tr.top td.rk{color:var(--trace);font-weight:600}
.rt tr.exp{cursor:pointer}
.rt tr.exp:hover td{background:var(--panel2)}
td.m-good{background:color-mix(in oklab,var(--ok) 11%,transparent)}
td.m-mid{background:color-mix(in oklab,var(--warn) 12%,transparent)}
td.m-bad{background:color-mix(in oklab,var(--crit) 13%,transparent);
  color:var(--crit);font-weight:500}
.werbar{display:inline-flex;align-items:center;gap:8px;justify-content:flex-end}
.werbar i{display:block;height:6px;border-radius:3px;background:var(--trace);opacity:.6;min-width:2px}
.dot{display:none}
.chip{display:inline-block;font:.68rem/1 "IBM Plex Mono",monospace;padding:4px 7px;
  border-radius:5px;border:1px solid var(--line);color:var(--muted)}
.chip.ok{color:var(--ok);border-color:color-mix(in oklab,var(--ok) 35%,var(--line))}
.chip.warn{color:var(--warn);border-color:color-mix(in oklab,var(--warn) 35%,var(--line))}
.chip.crit{color:var(--crit);border-color:color-mix(in oklab,var(--crit) 40%,var(--line))}
.rt tr.detail td{background:var(--panel2);text-align:left;white-space:normal;
  font-family:"IBM Plex Sans",sans-serif;padding:16px 18px 20px}
.rt tr.detail .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px}
.rt tr.detail .grid table{width:100%;border-collapse:collapse}
.rt tr.detail .grid th{position:static;font-size:.6rem;padding:5px 7px;text-align:left;
  border-bottom:1px solid var(--line);color:var(--muted)}
.rt tr.detail .grid td{padding:5px 7px;font-size:.78rem;border-bottom:1px solid var(--line)}
.flags{margin-top:12px;display:flex;flex-wrap:wrap;gap:6px}
.board-foot{padding:11px 15px;border-top:1px solid var(--line);
  font:.76rem/1.5 "IBM Plex Mono",monospace;color:var(--faint)}

/* matrice des duels — 2 axes, donc non empilable : on la fait défiler
   horizontalement AVEC la colonne des noms figée à gauche, pour ne jamais
   perdre de vue à quelle ligne correspond une cellule. */
table.matrice{table-layout:auto;border-collapse:separate;border-spacing:0}
table.matrice th,table.matrice td{text-align:center;font-size:.78rem;
  padding:9px 10px;white-space:nowrap}
table.matrice thead th{font-size:.62rem;cursor:default;vertical-align:bottom;
  min-width:74px;background:var(--panel);border-bottom:1px solid var(--line)}
table.matrice thead th:first-child{position:sticky;left:0;z-index:3;min-width:118px}
table.matrice td.name{font-family:"IBM Plex Sans",sans-serif;font-weight:500;
  text-align:left;font-size:.82rem;position:sticky;left:0;z-index:2;
  background:var(--panel);border-right:1px solid var(--line);
  box-shadow:6px 0 8px -8px rgba(0,0,0,.35)}
table.matrice tbody td{border-bottom:1px solid var(--line)}
table.matrice tbody tr:last-child td{border-bottom:0}
table.matrice td.diag,table.matrice td.nodata{color:var(--faint)}
@media (max-width:620px){
  table.matrice th,table.matrice td{font-size:.72rem;padding:8px 7px}
  table.matrice thead th{min-width:62px}
  table.matrice thead th:first-child,table.matrice td.name{min-width:96px;
    max-width:96px;white-space:normal;line-height:1.25}
}

/* tests d'écoute : gros titres numérotés par test */
.testblock{padding-top:8px}
.testblock+.testblock{margin-top:56px;border-top:1px solid var(--line);padding-top:40px}
.testhead .eyebrow{margin-bottom:10px}
.testhead h1{font-family:"Newsreader",Georgia,serif;font-weight:400;
  font-size:clamp(1.5rem,4vw,2.15rem);line-height:1.15;letter-spacing:-.01em;margin:0 0 12px}
.subhead{font-family:"Newsreader",serif;font-weight:500;font-size:1.1rem;
  margin:28px 0 10px;color:var(--ink)}
.subhead:first-of-type{margin-top:20px}
.subhead .n{font:.68rem/1 "IBM Plex Mono",monospace;color:var(--faint);
  letter-spacing:.06em;margin-left:8px;font-weight:400}

/* --- responsif : on masque les colonnes secondaires, la table reste
   une table et tient sans scroll horizontal --- */
@media (max-width:900px){ .rt .p3{display:none} }
@media (max-width:620px){
  .rt .p2{display:none}
  .rt thead th{padding:10px 8px;font-size:.62rem}
  .rt tbody td{padding:11px 8px;font-size:.82rem}
  .rt td.name{font-size:.9rem}
  .rt td.name .sub{font-size:.64rem;white-space:normal}
  .legend{gap:10px;font-size:.7rem}
  .md table{font-size:.72rem}
  .md th,.md td{padding:6px 7px}
}

/* --- mobile : les tableaux « une ligne = un modèle » s'empilent en fiches.
   Plus aucun défilement horizontal, et TOUTES les colonnes redeviennent
   visibles (y compris celles masquées en p2/p3 sur écran moyen), chacune
   précédée de son intitulé. Les matrices (2 axes) sont exclues : elles ne
   s'empilent pas — elles gardent leur colonne de gauche figée. --- */
/* NB : sélecteurs en enfant direct (`>`) — sinon les règles descendent aussi
   dans les petites tables imbriquées du détail dépliable et leur suppriment
   leurs en-têtes. */
@media (max-width:620px){
  table.rt.empile{display:block}
  table.rt.empile > thead{display:none}
  table.rt.empile > tbody{display:block}
  table.rt.empile > tbody > tr{display:block;padding:12px 14px 14px;
    border-bottom:1px solid var(--line);position:relative}
  table.rt.empile > tbody > tr:last-child{border-bottom:0}
  table.rt.empile > tbody > tr > td{display:flex;align-items:baseline;gap:12px;
    justify-content:space-between;width:auto;border:0;padding:5px 0;
    text-align:right;white-space:normal}
  table.rt.empile > tbody > tr > td.p2,
  table.rt.empile > tbody > tr > td.p3{display:flex}
  table.rt.empile > tbody > tr > td::before{content:attr(data-label);text-align:left;
    color:var(--muted);font:500 .66rem/1.5 "IBM Plex Mono",monospace;
    letter-spacing:.04em;text-transform:uppercase;flex:0 0 auto}
  table.rt.empile > tbody > tr > td.name{padding:0 58px 8px 0;font-size:1.02rem;
    justify-content:flex-start}
  table.rt.empile > tbody > tr > td.name::before{content:none}
  table.rt.empile > tbody > tr > td.rk{position:absolute;top:12px;right:14px;padding:0;
    font:500 .72rem/1 "IBM Plex Mono",monospace;color:var(--faint)}
  table.rt.empile > tbody > tr > td.rk::before{content:"#";margin-right:1px}
  /* cellules colorées : le fond pleine largeur devient illisible empilé,
     on ne garde la couleur que sur la valeur */
  table.rt.empile > tbody > tr > td.m-good,
  table.rt.empile > tbody > tr > td.m-mid,
  table.rt.empile > tbody > tr > td.m-bad{background:none}
  table.rt.empile > tbody > tr > td.m-good{color:var(--ok)}
  table.rt.empile > tbody > tr > td.m-mid{color:var(--warn)}
  table.rt.empile > tbody > tr > td.m-bad{color:var(--crit)}
  /* ligne de détail dépliée : on rend la main aux tables imbriquées */
  table.rt.empile > tbody > tr.detail{padding:0}
  table.rt.empile > tbody > tr.detail > td{display:block;text-align:left;
    padding:14px 14px 16px}
  table.rt.empile > tbody > tr.detail > td::before{content:none}
}

/* callout / cards */
.callout{border:1px solid var(--line);border-left:3px solid var(--trace);
  border-radius:0 12px 12px 0;background:var(--panel);padding:18px 20px;box-shadow:var(--shadow)}
.callout .k{font-family:"Newsreader",serif;font-style:italic;font-size:1.08rem;
  color:var(--ink);display:block;margin-bottom:6px}
.callout .d{color:var(--muted);font-size:.92rem}
.mgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:14px}
.mcard{border:1px solid var(--line);border-radius:12px;background:var(--panel);
  padding:15px 17px;display:flex;flex-direction:column;gap:8px}
.mhead{display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.mhead .mrk{font:600 .78rem/1 "IBM Plex Mono",monospace;color:var(--faint);
  border:1px solid var(--line);border-radius:5px;padding:3px 6px}
.mcard:first-child .mhead .mrk{color:var(--trace);border-color:var(--trace)}
.mhead a{font-family:"IBM Plex Sans",sans-serif;font-weight:600;font-size:1rem;
  border-bottom:1px solid transparent}
.mhead a:hover{border-bottom-color:var(--trace)}
.mhead .chip{margin-left:auto}
.msub{color:var(--faint);font-size:.72rem;line-height:1.5}
.mstat{font-size:.8rem;color:var(--muted);display:flex;flex-wrap:wrap;align-items:baseline;
  gap:3px 4px}
.mstat b{color:var(--ink);font-weight:500}
.mstat b.m-bad{color:var(--crit)} .mstat b.m-mid{color:var(--warn)} .mstat b.m-good{color:var(--ok)}
.mstat .sep{color:var(--faint);margin:0 4px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:16px;align-items:start}
.card{border:1px solid var(--line);border-radius:12px;background:var(--panel);padding:18px 20px}
.card h3{margin:0 0 8px;font-size:.98rem;font-weight:600}
.card p{margin:0 0 .6em;color:var(--muted);font-size:.88rem;line-height:1.55}
.card p:last-child{margin-bottom:0}
.card ul{margin:.4em 0 .8em;padding-left:1.1em;color:var(--muted);font-size:.86rem;line-height:1.6}
.card ul:last-child{margin-bottom:0}
.card li{margin-bottom:.35em}
.card li:last-child{margin-bottom:0}
.card li b{color:var(--ink);font-weight:600}
.card .tag{font:.66rem/1 "IBM Plex Mono",monospace;letter-spacing:.1em;text-transform:uppercase;
  color:var(--trace);display:block;margin-bottom:9px}
/* fiche modèle : table des paramètres réglables */
table.params tbody td{white-space:normal;vertical-align:top;text-align:left}
table.params td.name{font-size:.82rem;white-space:nowrap}
table.params td.defaut{text-align:center}
table.params td.role{font-family:"IBM Plex Sans",sans-serif;font-size:.86rem;
  line-height:1.55;color:var(--muted);min-width:280px}
@media (max-width:620px){
  table.params td.name{white-space:normal}
  /* empilé : le rôle passe sous son intitulé, pleine largeur, aligné à gauche */
  table.rt.params.empile > tbody > tr > td.role{display:block;text-align:left;
    min-width:0;padding-top:6px}
  table.rt.params.empile > tbody > tr > td.role::before{display:block;margin-bottom:3px}
  table.rt.params.empile > tbody > tr > td.name{font-family:"IBM Plex Mono",monospace;
    font-size:.88rem;padding-right:0}
}

/* fiche modèle : paires clé/valeur + avertissements */
.kvgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:0 22px}
.kv{display:flex;gap:14px;justify-content:space-between;align-items:baseline;
  padding:9px 0;border-bottom:1px dashed var(--line)}
.kv .k{color:var(--muted);font-size:.88rem}
.kv .v{color:var(--ink);font-weight:500;font-size:.9rem;text-align:right;
  overflow-wrap:anywhere}
ul.avert{margin:0;padding-left:0;list-style:none;display:grid;gap:10px}
ul.avert li{border:1px solid var(--line);border-left:3px solid var(--warn);
  border-radius:0 10px 10px 0;background:var(--panel);padding:12px 16px;
  color:var(--muted);font-size:.92rem;line-height:1.6}
.repro{font-family:"IBM Plex Mono",monospace;font-size:.8rem;line-height:1.8}
.repro div{display:flex;gap:12px;justify-content:space-between;
  border-bottom:1px dashed var(--line);padding:4px 0}
.repro span:last-child{color:var(--faint)}

/* md */
.md h1{font-family:"Newsreader",serif;font-weight:400;font-size:1.9rem;margin:0 0 8px}
.md h2{font-family:"Newsreader",serif;font-weight:500;font-size:1.35rem;margin:1.8em 0 .5em}
.md h3{font-size:.98rem;margin:1.5em 0 .4em;color:var(--muted)}
.md p,.md ul{color:var(--muted)}
.md code{font-family:"IBM Plex Mono",monospace;font-size:.85em;background:var(--panel2);
  padding:2px 5px;border-radius:4px}
.md .tablewrap{border:1px solid var(--line);border-radius:10px;margin:1em 0;
  background:var(--panel);overflow-x:auto}
.md table{border-collapse:collapse;width:100%;font-size:.84rem}
.md th,.md td{padding:9px 11px;border-bottom:1px solid var(--line);text-align:right}
.md th:first-child,.md td:first-child{text-align:left}
.md thead th{background:var(--panel2);font:500 .7rem/1 "IBM Plex Mono",monospace;
  text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.md td{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}
.md blockquote{margin:1em 0;padding:.4em 1em;border-left:3px solid var(--trace);
  background:var(--panel);border-radius:0 8px 8px 0;color:var(--ink)}
.md table.rank td:nth-child(2){text-align:left}
.md table.rank td:first-child{color:var(--faint)}
.ic{color:var(--faint);font-size:.85em;font-weight:400}
#ecoute .md .tablewrap{margin:.4em 0 1.1em}

footer{border-top:1px solid var(--line);margin-top:56px}
footer .wrap{padding:24px 22px 44px;color:var(--faint);
  font:.78rem/1.7 "IBM Plex Mono",monospace;display:flex;flex-wrap:wrap;gap:6px 22px}
footer a{color:var(--muted)}
footer a:hover{color:var(--trace)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&'
         'family=IBM+Plex+Sans:wght@400;500;600&'
         'family=IBM+Plex+Mono:wght@400;500&display=swap">')

TOGGLE_JS = """
(function(){var r=document.documentElement,K='tts-bench-theme';
try{var s=localStorage.getItem(K);if(s)r.setAttribute('data-theme',s);}catch(e){}
var b=document.getElementById('tgl');if(!b)return;
function cur(){return r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');}
b.onclick=function(){var n=cur()==='dark'?'light':'dark';r.setAttribute('data-theme',n);
try{localStorage.setItem(K,n);}catch(e){}};})();
"""

# Menu hamburger (mobile) : le panneau n'existe qu'en CSS sous 620 px ; ici on
# ne gère que l'état ouvert/fermé + les sorties clavier et clic extérieur.
MENU_JS = """
(function(){var b=document.getElementById('burger'),p=document.getElementById('navliens');
if(!b||!p)return;
function etat(ouvert){p.classList.toggle('ouvert',ouvert);
  b.setAttribute('aria-expanded',ouvert?'true':'false');
  b.setAttribute('aria-label',ouvert?'Fermer le menu':'Ouvrir le menu');}
b.addEventListener('click',function(e){e.stopPropagation();
  etat(b.getAttribute('aria-expanded')!=='true');});
p.addEventListener('click',function(e){if(e.target.tagName==='A')etat(false);});
document.addEventListener('click',function(e){
  if(p.classList.contains('ouvert')&&!p.contains(e.target)&&e.target!==b)etat(false);});
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'&&p.classList.contains('ouvert')){etat(false);b.focus();}});
addEventListener('resize',function(){if(innerWidth>620)etat(false);});})();
"""

# --------------------------------------------------------------------------
# Composant table générique : tri asc/desc par colonne, cartes sur mobile,
# code couleur bon/à-surveiller, détail dépliable. Config via window[cfgId].
# cfg = {cols:[{k,label,dir,fmt,g,b,kind}], rows:[{_nom,_sub,_href,_detail,...}],
#        sort:{k,asc}, rankcol:bool}
# --------------------------------------------------------------------------
TABLE_JS = r"""
function ttsTable(mountSel, cfg){
  var mount=document.querySelector(mountSel);
  var sort=cfg.sort||{k:cfg.cols[1]?cfg.cols[1].k:cfg.cols[0].k, asc:true};
  var open={};
  function fmt(c,x){ if(x===null||x===undefined) return '\u2014';
    if(c.fmt==='pct') return (x*100).toFixed(1)+'%';
    if(c.fmt==='num1') return (+x).toFixed(1);
    if(c.fmt==='num2') return (+x).toFixed(2);
    if(c.fmt==='num3') return (+x).toFixed(3);
    if(c.fmt==='x') return (+x).toFixed(2)+'\u00d7';
    if(c.fmt==='oui') return x?'oui':'non';
    return ''+x; }
  function cls(c,x){ if(x===null||x===undefined||!c.dir||c.g===null||c.g===undefined) return '';
    if(c.dir<0) return x<=c.g?'m-good':(x>=c.b?'m-bad':'m-mid');
    return x>=c.g?'m-good':(x<=c.b?'m-bad':'m-mid'); }
  function arrow(k){ if(sort.k!==k) return '';
    return '<span class="ar">'+(sort.asc?'\u25B2':'\u25BC')+'</span>'; }
  function dirGlyph(c){ return c.dir<0?' \u2193':(c.dir>0?' \u2191':''); }
  function sorted(){
    var r=cfg.rows.slice();
    r.sort(function(a,b){ var x=a[sort.k],y=b[sort.k];
      if(x===null||x===undefined)x=Infinity; if(y===null||y===undefined)y=Infinity;
      if(typeof x==='boolean'){x=x?1:0;y=y?1:0;}
      if(typeof x==='string'){ return x.localeCompare(y)*(sort.asc?1:-1); }
      return (x<y?-1:x>y?1:0)*(sort.asc?1:-1); });
    return r;
  }
  function render(){
    var rows=sorted();
    var th='<tr>'+(cfg.rankcol?'<th class="rk">#</th>':'');
    cfg.cols.forEach(function(c){
      var pc=c.p?' p'+c.p:'';
      th+='<th class="'+(c.k==='_nom'?'name':'')+pc.trim()+'" data-k="'+c.k+'"'
        +(sort.k===c.k?' data-active':'')
        +(c.desc?' title="'+c.desc.replace(/"/g,'&quot;')+'"':'')+'>'
        +(c.desc?'<span class="hlabel">'+c.label+'</span>':c.label)
        +'<span style="color:var(--faint)">'+dirGlyph(c)+'</span>'+arrow(c.k)+'</th>'; });
    th+='</tr>';
    var body='';
    rows.forEach(function(row,i){
      var nm=row._href?'<a href="'+row._href+'">'+row._nom+'</a>':row._nom;
      var sub=row._sub?'<span class="sub">'+row._sub+'</span>':'';
      var tr='<tr class="'+(row._detail?'exp ':'')+(i===0&&sort.k==='wer'&&sort.asc?'top':'')+'" data-i="'+i+'">';
      if(cfg.rankcol) tr+='<td class="rk">'+(i+1)+'</td>';
      tr+='<td class="name">'+nm+sub+'</td>';
      cfg.cols.slice(1).forEach(function(c){
        var v=row[c.k], k=cls(c,v), pc=c.p?' p'+c.p:'';
        var inner=fmt(c,v);
        if(c.kind==='werbar' && v!=null){
          var w=Math.max(6, 62*v/(cfg.wermax||0.1));
          inner='<span class="werbar"><i style="width:'+w.toFixed(0)+'px"></i>'+(v*100).toFixed(1)+'%</span>';
        } else if(c.kind==='chip'){
          inner='<span class="chip '+(k==='m-bad'?'crit':k==='m-good'?'ok':k==='m-mid'?'warn':'')+'">'+inner+'</span>'; k='';
        } else if(c.kind==='lic'){
          inner=row._lic; k='';
        } else if(c.kind==='mos'){
          inner=(v==null)?'—':(v.toFixed(2)+' <span class="ic">±'+(row[c.k+'_ic']||0).toFixed(2)+'</span>');
        }
        tr+='<td class="'+(k+pc).trim()+'" data-label="'+c.label+'">'+inner+'</td>';
      });
      tr+='</tr>';
      if(row._detail){
        tr+='<tr class="detail" data-i="'+i+'"'+(open[row._nom]?'':' hidden')+'><td colspan="'
          +(cfg.cols.length+(cfg.rankcol?1:0))+'">'+row._detail+'</td></tr>';
      }
      body+=tr;
    });
    mount.innerHTML='<div class="tablewrap"><table class="rt empile"><thead>'+th
      +'</thead><tbody>'+body+'</tbody></table></div>';
    mount.querySelectorAll('thead th[data-k]').forEach(function(h){
      h.onclick=function(){ var k=h.dataset.k;
        if(sort.k===k){ sort.asc=!sort.asc; }
        else { sort.k=k; var c=cfg.cols.find(function(x){return x.k===k;});
          sort.asc=!(c&&c.dir>0); }        /* ↑-mieux -> desc d'abord, sinon asc */
        render(); if(cfg.msort) cfg.msort.value=sort.k+'|'+(sort.asc?'a':'d'); };
    });
    mount.querySelectorAll('tr.exp').forEach(function(tr){
      tr.onclick=function(){ var d=tr.nextElementSibling;
        if(d&&d.classList.contains('detail')){ d.hidden=!d.hidden;
          open[cfg.rows[+tr.dataset.i]._nom]=!d.hidden; } };
    });
  }
  if(cfg.msort){ cfg.msort.onchange=function(){
    var p=cfg.msort.value.split('|'); sort.k=p[0]; sort.asc=p[1]==='a'; render(); }; }
  cfg.rerender=render;
  render();
}
"""


def _shell(titre: str, actif: str, corps: str, hero: str = "", js: str = "",
           standalone: bool = False) -> str:
    def cl(k):
        return ' class="on"' if k == actif else ""
    h_obj = "#classement" if standalone else "objectif.html"
    h_ec = "#ecoute" if standalone else "ecoute.html"
    nav = (f'<a href="{"#top" if standalone else "index.html"}"{cl("index")}>Aperçu</a>'
           f'<a href="{h_obj}"{cl("objectif")}>Recap</a>'
           f'<a href="{h_ec}"{cl("ecoute")}>Écoute</a>'
           f'<a href="{REPO}" class="link" style="text-decoration:none">Dépôt&nbsp;↗</a>')
    gen = f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC"
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(titre)}</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header class="bar"><div class="wrap">
  <span class="brand">Benchmark&nbsp;TTS<span class="fr">FR</span></span>
  <nav>
    <div class="navliens" id="navliens">{nav}</div>
    <button class="tgl" id="tgl" title="Thème" aria-label="Changer de thème">◑</button>
    <button class="burger" id="burger" aria-label="Ouvrir le menu" aria-expanded="false"
      aria-controls="navliens"><span class="bg"></span></button>
  </nav>
</div></header>
{hero}
<main><div class="wrap">
{corps}
</div></main>
<footer><div class="wrap">
  <span>Généré {gen} · <span style="color:var(--muted)">benchmark/build_pages.py</span></span>
  <span>Métriques automatiques — <span style="color:var(--muted)">l'écoute humaine tranche</span></span>
  <span><a href="{REPO}">github.com/chvalois/benchmark-tts</a></span>
</div></footer>
<script>{TOGGLE_JS}
{MENU_JS}
{TABLE_JS}
{js}</script>
</body></html>
"""


LEGENDE = ('<div class="legend">'
           '<b><i class="sw-g"></i>meilleur</b>'
           '<b><i class="sw-m"></i>correct</b>'
           '<b><i class="sw-b"></i>à surveiller</b>'
           '<b>↓ plus bas = mieux</b><b>↑ plus haut = mieux</b>'
           '</div>')


# --------------------------------------------------------------------------
# Collecte des données
# --------------------------------------------------------------------------
def _licences() -> dict:
    if not LICENCES.is_file():
        return {}
    import yaml
    return yaml.safe_load(LICENCES.read_text(encoding="utf-8")) or {}


def _lock() -> dict:
    if not MODELS_LOCK.is_file():
        return {}
    return (json.loads(MODELS_LOCK.read_text(encoding="utf-8")) or {}).get("modeles", {})


def _collecter() -> dict:
    lic, lock = _licences(), _lock()
    modeles: dict[str, dict] = {}
    exclus: list[dict] = []
    voix_vues: set[str] = set()
    for f in sorted(RESULTATS.glob("*.json")):
        if f.stem == "ecoute":
            continue
        lk = lock.get(f.stem, {})
        statut = lk.get("statut", "verifie")
        if statut != "verifie":
            exclus.append({"nom": f.stem, "motif": STATUT_MOTIF.get(statut, statut)})
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        li = lic.get(f.stem, {})
        par_voix: dict[str, dict] = {}
        for voix, r in data.items():
            voix_vues.add(voix)
            s, g, st = r["synthese"], r["vitesse"]["global"], r["stabilite"]
            par_voix[voix] = {
                "n": s.get("n_verifiees") or s.get("n_runs") or 0,
                "clonage": r["meta"].get("params", {}).get("clonage", True),
                "wer": s["wer_moyen"], "wer_sigma": s["wer_ecart_type"],
                "wer_net": s.get("wer_net_plancher"),
                "sim": s.get("sim_moyen"),
                "hallu": s["taux_hallucination"], "rep": s["taux_repetition"],
                "tronc": s["taux_troncature"],
                "rtf": g["rtf"]["moyenne"], "ttfa": g["ttfa_s"]["moyenne"],
                "cv": st["cv_median"], "n_suspects": st["n_suspects"],
                "wer_longueur": s.get("wer_par_longueur", {}),
                "wer_registre": s.get("wer_par_registre", {}),
                "wer_piege": s.get("wer_par_piege", {}),
                "flags": {
                    "hallucination": s.get("phrases_hallucination", []),
                    "repetition": s.get("phrases_repetition", []),
                    "troncature": s.get("phrases_troncature", []),
                },
            }
        modeles[f.stem] = {
            "licence": li.get("licence", "?"),
            "usage_commercial": li.get("usage_commercial", "?"),
            "vram_go": lk.get("vram_go_estimee"),
            "revision": (lk.get("revision") or "")[:10],
            "role": lk.get("role", ""),
            "par_voix": par_voix,
            "global": _agrege(par_voix),
        }
    # « voix de référence » = les voix de narration (hors registres émotionnels
    # d'un même locuteur et hors voix interne de modèle).
    narration = {v for v in voix_vues
                 if not re.fullmatch(r"papa_(joie|colere|peur|tristesse)", v)
                 and v != "ff_siwis"}
    return {"modeles": modeles, "exclus": exclus,
            "n_voix": len(narration) or len(voix_vues)}


SEUIL_WER_COMBO = 0.30   # au-delà, la (modèle, voix) est écartée de la moyenne :
#                          clips inexploitables (échec de clonage sur cette voix)


def _agrege(par_voix: dict) -> dict | None:
    """Combine les stats d'un modèle sur **toutes ses voix** — moyenne
    pondérée par le nb de runs vérifiés. Les (modèle, voix) au WER moyen
    > `SEUIL_WER_COMBO` sont écartées (clips inexploitables). Les buckets
    WER (longueur / registre / piège) sont recombinés clé à clé."""
    toutes = [r for r in par_voix.values() if r.get("n")]
    if not toutes:
        return None
    rows = [r for r in toutes if (r.get("wer") or 0) < SEUIL_WER_COMBO] or toutes
    n_ecartees = len(toutes) - len(rows)
    ntot = sum(r["n"] for r in rows)

    def wmean(k: str):
        pts = [(r["n"], r[k]) for r in rows if r.get(k) is not None]
        return sum(n * v for n, v in pts) / sum(n for n, _ in pts) if pts else None

    def merge(key: str) -> dict:
        acc: dict[str, dict] = {}
        for r in rows:
            for b, x in (r.get(key) or {}).items():
                a = acc.setdefault(b, {"n": 0, "s": 0.0})
                a["n"] += x["n"]
                a["s"] += x["n"] * x["wer_moyen"]
        return {b: {"n": a["n"], "wer_moyen": a["s"] / a["n"]}
                for b, a in acc.items() if a["n"]}

    return {
        "n": ntot, "n_voix": len(rows), "n_voix_ecartees": n_ecartees,
        "clonage": any(r.get("clonage") for r in rows),
        "wer": wmean("wer"), "wer_sigma": wmean("wer_sigma"),
        "wer_net": wmean("wer_net"), "sim": wmean("sim"),
        "hallu": wmean("hallu"), "rep": wmean("rep"), "tronc": wmean("tronc"),
        "rtf": wmean("rtf"), "ttfa": wmean("ttfa"), "cv": wmean("cv"),
        "n_suspects": sum(r.get("n_suspects", 0) for r in rows),
        "wer_longueur": merge("wer_longueur"),
        "wer_registre": merge("wer_registre"),
        "wer_piege": merge("wer_piege"),
        "flags": {kind: sorted({p for r in rows
                                for p in (r.get("flags") or {}).get(kind, [])})
                  for kind in ("hallucination", "repetition", "troncature")},
    }


# --------------------------------------------------------------------------
# Page projet
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Score global — bornes **fixes**, choisies une fois pour toutes (pas
# dérivées des modèles présents dans le run). Le score d'un modèle ne
# dépend donc que de ses 3 métriques : ajouter ou retirer un concurrent ne
# fait jamais bouger le score des autres — seul leur rang peut changer.
# C'est la convention des benchmarks IA établis (SWE-bench/MMLU publient
# un taux brut déjà absolu ; les index composites comme l'Artificial
# Analysis Intelligence Index normalisent chaque sous-score par des bornes
# gelées, ex. clamp((Elo-500)/2000), jamais par le min/max du comparatif
# du jour). Revoir ces bornes = décision méthodologique explicite, à
# documenter ici et dans docs/METHODOLOGIE.md — jamais un recalcul auto.
WER_PLANCHER, WER_PLAFOND = 0.0, 0.15   # 0 % = parfait ; 15 % = déjà jugé
#   peu fiable pour un usage narratif (à mi-chemin du seuil d'exclusion
#   de combo (modèle, voix) à 30 %, cf. SEUIL_WER_COMBO)
SIM_PLANCHER, SIM_PLAFOND = 0.60, 0.90  # cosinus ECAPA : 0.60 = timbre
#   nettement différent ; 0.90 = quasi la meilleure similarité observée
#   en clonage zero-shot dans ce benchmark
MOS_PLANCHER, MOS_PLAFOND = 1.0, 5.0    # échelle MOS native, aucune borne
#   à choisir : 1-5 est déjà un barème absolu


def _normalise(x: float | None, plancher: float, plafond: float,
               inverse: bool = False) -> float | None:
    """Ramène `x` sur [0,1] via des bornes fixes, clampé aux extrémités.
    `inverse=True` pour une métrique où plus bas = meilleur (WER)."""
    if x is None:
        return None
    v = (plafond - x) if inverse else (x - plancher)
    return max(0.0, min(1.0, v / (plafond - plancher)))


def _calc_score(rows: list[dict]) -> None:
    """Ajoute `score` (0-100) à chaque ligne : moyenne de 3 métriques
    normalisées sur des **bornes fixes** (voir plus haut) — WER inversé
    (auto, intelligibilité), SIM (auto, identité de timbre), Naturalité =
    MOS « Naturel » du test d'écoute humain (seul juge de la naturalité,
    cf. [[remplacer-utmos-naturalite]]). Un modèle sans les 3 valeurs n'a
    pas de score (classé après ceux qui en ont un)."""
    for r in rows:
        if r["wer"] is None or r["sim"] is None or r["naturel"] is None:
            r["score"] = None
            continue
        nw = _normalise(r["wer"], WER_PLANCHER, WER_PLAFOND, inverse=True)
        ns = _normalise(r["sim"], SIM_PLANCHER, SIM_PLAFOND)
        nn = _normalise(r["naturel"], MOS_PLANCHER, MOS_PLAFOND)
        r["score"] = round(100 * (nw + ns + nn) / 3, 1)


def _scope_svg(rows: list[dict]) -> str:
    items = sorted(
        ((r["score"], r["_nom"]) for r in rows if r.get("score") is not None),
        key=lambda x: -x[0],
    )
    if not items:
        return ""
    W, rowh, padL, padR = 560, 28, 140, 46
    span = W - padL - padR
    H = 28 + rowh * len(items)
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
           f'aria-label="Score global par modèle" '
           f'style="min-width:460px;font-family:\'IBM Plex Mono\',monospace">']
    for gx in range(0, 101, 20):
        x = padL + gx / 100 * span
        out.append(f'<line x1="{x:.0f}" y1="12" x2="{x:.0f}" y2="{H-16}" '
                   f'stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.0f}" y="{H-3}" text-anchor="middle" font-size="9" '
                   f'fill="var(--faint)">{gx}</text>')
    for i, (score, nom) in enumerate(items):
        y = 22 + i * rowh
        x2 = padL + score / 100 * span
        out.append(f'<text x="{padL-10:.0f}" y="{y+4:.0f}" text-anchor="end" '
                   f'font-size="10.5" fill="var(--muted)">{html.escape(nom)}</text>')
        out.append(f'<line x1="{padL}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y:.0f}" '
                   f'stroke="var(--trace)" stroke-width="6" stroke-linecap="round" '
                   f'opacity="{0.5 + 0.45*(score/100):.2f}"/>')
        out.append(f'<circle cx="{x2:.0f}" cy="{y:.0f}" r="3.4" fill="var(--trace)"/>')
        out.append(f'<text x="{x2+8:.0f}" y="{y+4:.0f}" font-size="10.5" '
                   f'fill="var(--ink)">{score:.1f}</text>')
    out.append('</svg>')
    return "".join(out)


def _duel_ratio(duel: dict, a: str, b: str) -> tuple[float | None, float, int]:
    """Ratio de victoires de `a` contre `b` (0-1), + (victoires_a, total) —
    `duel` est le dict `{"modA|modB": [victoires_modA, victoires_modB]}` (clé
    triée alphabétiquement) produit par `agreger_ecoute.calculer`."""
    lo, hi = sorted((a, b))
    v = duel.get(f"{lo}|{hi}")
    if not v or sum(v) == 0:
        return None, 0.0, 0
    wins_a = v[0] if a == lo else v[1]
    tot = sum(v)
    return wins_a / tot, wins_a, tot


def _ratio_bg(r: float) -> str:
    """Dégradé rouge (0) -> vert (1), mélangé à une opacité fixe pour rester
    lisible dans les deux thèmes (respecte les variables --ok/--crit)."""
    pct = max(0.0, min(1.0, r)) * 100
    return (f'background:color-mix(in oklab,color-mix(in oklab,'
            f'var(--ok) {pct:.0f}%,var(--crit)) 42%,transparent)')


def _matrice_html(duel: dict, ordre: list[str]) -> str:
    """Matrice des duels : ligne vs colonne, verdâtre si la ligne gagne
    majoritairement, rougeâtre si elle perd. `ordre` = slugs des modèles,
    même ordre en ligne et en colonne."""
    if not duel or len(ordre) < 2:
        return '<p class="lead">Pas assez de duels pour une matrice.</p>'
    out = ['<div class="tablewrap"><table class="rt matrice"><thead><tr><th></th>']
    for b in ordre:
        out.append(f'<th>{html.escape(_nm(b))}</th>')
    out.append('</tr></thead><tbody>')
    for a in ordre:
        out.append(f'<tr><td class="name">{html.escape(_nm(a))}</td>')
        for b in ordre:
            if a == b:
                out.append('<td class="diag">·</td>')
                continue
            r, wins, tot = _duel_ratio(duel, a, b)
            if r is None:
                out.append('<td class="nodata">—</td>')
            else:
                w = int(wins) if wins == int(wins) else wins
                out.append(f'<td style="{_ratio_bg(r)}">{w}/{tot}</td>')
        out.append('</tr>')
    out.append('</tbody></table></div>')
    return "".join(out)


def _defauts_svg(ab: dict) -> str:
    """Barres horizontales EMPILÉES : taux de chaque défaut signalé par
    duel (défauts / nb de duels du modèle) — normalisé pour rester
    comparable entre modèles inégalement exposés (pondération d'équité du
    pool d'écoute, cf. `benchmark/build_ecoute.py`)."""
    stats, defauts = ab.get("stats", {}), ab.get("defauts", {})
    modeles = [m for m in stats if stats[m]["n"]]
    if not modeles:
        return ""
    taux = {m: {dk: defauts.get(m, {}).get(dk, 0) / stats[m]["n"] for dk in DEFAUT_LABELS}
            for m in modeles}
    ordre = sorted(modeles, key=lambda m: -sum(taux[m].values()))
    maxi = max((sum(taux[m].values()) for m in ordre), default=0)
    if maxi <= 0:
        return ""
    W, rowh, padL, padR = 620, 28, 150, 30
    span = W - padL - padR
    H = 18 + rowh * len(ordre) + 30
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
           f'aria-label="Défauts entendus par modèle, taux par duel" '
           f'style="min-width:460px;font-family:\'IBM Plex Mono\',monospace">']
    for i, m in enumerate(ordre):
        y = 14 + i * rowh
        out.append(f'<text x="{padL-10}" y="{y+4}" text-anchor="end" font-size="10.5" '
                   f'fill="var(--muted)">{html.escape(_nm(m))}</text>')
        x = padL
        for dk in DEFAUT_LABELS:
            w = taux[m].get(dk, 0) / maxi * span
            if w <= 0.4:
                continue
            out.append(f'<rect x="{x:.1f}" y="{y-7}" width="{w:.1f}" height="14" rx="2" '
                       f'fill="{DEFAUT_COULEURS[dk]}"><title>{html.escape(_nm(m))} — '
                       f'{DEFAUT_LABELS[dk]} : {taux[m][dk]*100:.0f}% des duels</title></rect>')
            x += w
    y_leg = H - 10
    lx = padL
    for dk, lab in DEFAUT_LABELS_COURT.items():
        out.append(f'<rect x="{lx:.0f}" y="{y_leg-8}" width="9" height="9" rx="2" '
                   f'fill="{DEFAUT_COULEURS[dk]}"/>')
        out.append(f'<text x="{lx+13:.0f}" y="{y_leg}" font-size="9.5" '
                   f'fill="var(--muted)">{html.escape(lab)}</text>')
        lx += 15 + len(lab) * 6.2
    out.append('</svg>')
    return "".join(out)


def _ecoute_json() -> dict | None:
    """Charge `resultats/ecoute.json` (données structurées produites par
    `benchmark/agreger_ecoute.py::calculer`). Source unique pour la page
    écoute ET pour la Naturalité du score global de la page projet."""
    f = RESULTATS / "ecoute.json"
    if not f.is_file():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def _ecoute_donnees() -> dict | None:
    """Vue adaptée pour `page_index()` : {panel:(n,a,m,e), mos:{modele:{axe:(moy,ic)}}}."""
    d = _ecoute_json()
    if not d:
        return None
    p = d["panel"]
    mos = {
        m: {axe: (v["moyenne"], v["ic"]) for axe, v in axes.items()}
        for m, axes in (d.get("mos") or {}).get("par_modele", {}).items()
    } if d.get("mos") else {}
    return {"panel": (p["auditeurs"], p["ab"], p["mos"], p["emo"]), "mos": mos}


def _detail_html(r: dict) -> str:
    def sub(t, obj):
        ks = sorted(obj or {}, key=lambda k: -obj[k]["wer_moyen"])
        if not ks:
            return ""
        rows = "".join(
            f'<tr><td>{k}</td><td>{obj[k]["n"]}</td>'
            f'<td class="{_cls("wer", obj[k]["wer_moyen"])}">{obj[k]["wer_moyen"]*100:.1f}%</td></tr>'
            for k in ks)
        return (f'<table><thead><tr><th>{t}</th><th>n</th><th>WER</th></tr></thead>'
                f'<tbody>{rows}</tbody></table>')
    ch = []
    for kind, arr in (r.get("flags") or {}).items():
        if arr:
            ch.append(f'<span class="chip crit">{kind} : {", ".join(arr)}</span>')
    if r.get("n_suspects"):
        ch.append(f'<span class="chip warn">durée instable : {r["n_suspects"]}</span>')
    flags = (f'<div class="flags">{"".join(ch)}</div>' if ch
             else '<p style="margin-top:12px;color:var(--faint)">Aucune phrase signalée.</p>')
    return (f'<div class="grid">{sub("longueur", r.get("wer_longueur"))}'
            f'{sub("registre", r.get("wer_registre"))}{sub("piège", r.get("wer_piege"))}</div>{flags}')


def page_index(standalone: bool = False) -> str:
    d = _collecter()
    h_obj = REPO if standalone else "objectif.html"
    h_ec = "#classement" if standalone else "ecoute.html"
    lb = sorted(
        ((n, m, m["global"]) for n, m in d["modeles"].items()
         if (m.get("global") or {}).get("wer") is not None
         and m["global"]["wer"] < 0.5),
        key=lambda x: x[2]["wer"],
    )
    n_mod, n_voix = len(lb), d["n_voix"]
    dc = _ecoute_donnees()
    naturel = {slug: ax["naturel"][0] for slug, ax in (dc["mos"] if dc else {}).items() if "naturel" in ax}

    fiches = _fiches()
    rows = [{"_nom": _nm(nom), "_slug": nom, "wer": r["wer"], "sim": r["sim"],
             "naturel": naturel.get(nom),
             **({} if standalone or nom not in fiches else {"_href": fichier_modele(nom)})}
            for nom, m, r in lb]
    _calc_score(rows)
    rows.sort(key=lambda r: (r["score"] is None, -(r["score"] if r["score"] is not None else 0)))
    a_score = [r for r in rows if r["score"] is not None]
    n_score = len(a_score)

    # cartes « Les modèles » dans le même ordre que le classement (score,
    # puis WER pour les modèles sans score d'écoute).
    par_slug = {nom: (m, r) for nom, m, r in lb}
    cartes = []
    for i, row in enumerate(rows):
        m, r = par_slug[row["_slug"]]
        anom = r["hallu"] + r["rep"] + r["tronc"]
        comm = m["usage_commercial"]
        lic = (f'<span class="chip ok">{m["licence"]}</span>' if comm == "oui"
               else f'<span class="chip crit">{m["licence"]} · non&nbsp;comm.</span>' if comm == "non"
               else f'<span class="chip warn">{m["licence"]}</span>')
        vram = f'{m["vram_go"]} Go' if m["vram_go"] else "—"
        st = (
            f'<b class="{_cls("rtf", r["rtf"])}">{r["rtf"]:.2f}×</b>&nbsp;RTF'
            f'<span class="sep">·</span><b class="{_cls("cv", r["cv"])}">{r["cv"]*100:.0f}%</b>&nbsp;CV'
            f'<span class="sep">·</span><b class="{_cls("anom", anom)}">{anom*100:.0f}%</b>&nbsp;anom.'
            f'<span class="sep">·</span><b>{vram}</b>&nbsp;VRAM~'
        )
        cartes.append(
            f'<div class="mcard"><div class="mhead">'
            f'<span class="mrk">{i+1}</span>'
            f'<a href="{fichier_modele(row["_slug"]) if (not standalone and row["_slug"] in fiches) else h_obj}">'
            f'<b>{row["_nom"]}</b></a>{lic}</div>'
            f'<div class="msub mono">{m["revision"] or "—"} · {html.escape(m["role"][:70])}</div>'
            f'<div class="mstat mono">{st}</div></div>'
        )

    cols = [
        {"k": "_nom", "label": "modèle"},
        {"k": "wer", "label": "WER", "dir": -1, "fmt": "pct", "g": .05, "b": .10},
        {"k": "sim", "label": "SIM", "dir": 1, "fmt": "num3", "g": .80, "b": .72},
        {"k": "naturel", "label": "Naturalité", "dir": 1, "fmt": "num2", "g": 3.5, "b": 3.0},
        {"k": "score", "label": "Score global", "dir": 1, "fmt": "num1", "g": 66, "b": 33},
    ]
    tri_defaut = {"k": "score", "asc": False} if n_score else {"k": "wer", "asc": True}
    cfg = {"cols": cols, "rows": rows, "sort": tri_defaut, "rankcol": True}

    hero = f"""<div class="hero" id="top"><div class="wrap">
  <div class="eyebrow">Benchmark · TTS open-source · Français</div>
  <h1>Quel modèle de synthèse vocale pour le français ?</h1>
  <p class="thesis">{n_mod} modèles open-source clonent {n_voix} voix de référence sur un
    corpus français annoté (liaison, nombres, noms propres, homographes, dialogue
    émotionnel). <b>Score global</b> = WER, SIM et Naturalité (écoute humaine),
    <em>normalisés puis moyennés</em> — voir méthode ci-dessous.</p>
  <div class="scope">
    <div class="cap">Score global (0–100) — barre longue = meilleur</div>
    {_scope_svg(rows)}
  </div>
</div></div>"""

    excl = ""
    if d["exclus"]:
        excl = ('<div class="board-foot">hors classement — '
                + " · ".join(f'{_nm(e["nom"])} ({e["motif"]})' for e in d["exclus"]) + "</div>")

    ec_panel = ""
    if dc and dc["panel"]:
        n, a, m, e = dc["panel"]
        ec_panel = (f'<p class="lead" style="margin-top:22px"><b>Panel écoute</b> : {n} auditeur·rice·s, en aveugle — '
                    f'{a} comparaisons A/B, {m} notes MOS (1–5), {e} votes émotion. '
                    f'Aucun nom de voix ni de participant n\'est publié. '
                    f'<a class="link" href="{h_ec}">Détail : matrice des duels, '
                    f'MOS par axe, émotion &rarr;</a></p>')

    corps = f"""<section id="classement">
  <div class="sec-h"><h2>Classement — score global</h2>
    <span class="n">WER + SIM + Naturalité · toutes voix confondues</span></div>
  {LEGENDE}
  <div class="board"><div id="lb"></div>{excl}</div>

  <div class="lead" style="margin-top:20px">
    <p><b>WER</b> — taux d'erreur de transcription
    (<span class="mono">whisper-large-v3-french</span> + <span class="mono">jiwer</span>),
    ↓ meilleur. Mesure l'<b>intelligibilité</b> : est-ce que ce qui est dit
    correspond au texte demandé ? Automatique.</p>
    <p><b>SIM</b> — similarité au locuteur de référence (embeddings ECAPA),
    ↑ meilleur. Mesure l'<b>identité de timbre</b> : la voix générée
    ressemble-t-elle à la voix clonée ? Automatique. <i>Limite connue : SIM
    sous-pondère une dérive d'accent que l'oreille sanctionne fort
    (corrélation avec la similarité perçue à l'écoute : r≈0,16 sur les clips
    notés) — en cas de désaccord net entre SIM et l'écoute, fie-toi à
    l'écoute.</i></p>
    <p><b>Naturalité</b> — MOS « Naturel » (1–5) du test d'écoute humain en
    aveugle, ↑ meilleur. Aucune métrique automatique (UTMOS, TTSDS2, NISQA)
    ne s'est révélée fiable en français, voir <a class="link" href="{h_ec}">pourquoi</a>.</p>
    <p><b>Score global</b> — moyenne de ces 3 valeurs, chacune ramenée sur des
    <b>bornes fixes</b> (WER 0–15&nbsp;%, SIM 0,60–0,90, MOS 1–5 — jamais le
    min/max des modèles présents dans le run en cours), puis ×100 : le score
    d'un modèle ne bouge pas quand un concurrent rejoint ou quitte le
    comparatif, seul son rang peut changer. Un modèle sans note d'écoute n'a
    pas de score.</p>
    <p>Clic sur un en-tête de colonne pour trier le tableau.</p>
  </div>
  {ec_panel}
</section>

<section id="modeles">
  <div class="sec-h"><h2>Les modèles</h2><span class="n">contexte · vitesse · stabilité</span></div>
  <div class="mgrid">{"".join(cartes)}</div>
  <p class="lead" style="margin-top:16px"><a class="link" href="{h_obj}">Table
    complète (toutes métriques, toutes voix confondues, détail par phrase) &rarr;</a></p>
</section>

<section id="lecture"><div class="callout">
  <p><span class="k">Le score global mélange auto et humain — à dessein.</span>
  <span class="d">WER et SIM sont reproductibles mais ne mesurent pas la
  naturalité perçue : UTMOS, TTSDS2 et NISQA ont été essayés puis écartés en
  français (corrélation nulle voire négative avec la note humaine). Le tiers
  « Naturalité » du score vient donc du test d'écoute en aveugle, pas d'une
  métrique auto.</span></p>
</div></section>

<section id="methode">
  <div class="sec-h"><h2>Méthode</h2><span class="n">détail : docs/METHODOLOGIE.md</span></div>
  <div class="cards">
    <div class="card"><span class="tag">Corpus</span><h3>34 phrases annotées, chacune générée 3 fois</h3>
      <p>Chaque phrase est classée par longueur, par registre (narration,
      dialogue joie/colère/peur/tristesse, cours magistral) et par « piège »
      — une difficulté connue de la synthèse vocale en français :</p>
      <ul>
        <li><b>liaison</b> : un son de liaison entre deux mots doit être fait
          ou évité correctement (ex. « <i>rue des Acacias</i> » — liaison sur
          le « s » de « des »).</li>
        <li><b>nombre</b> : nombres écrits en toutes lettres (ex. « <i>mille
          sept cent quatre-vingt-neuf</i> ») — épelés chiffre par chiffre ou
          mal lus par certains modèles.</li>
        <li><b>nom propre</b> : noms composés ou d'origine étrangère (ex.
          « <i>Anne-Sophie Legrand-Dubois</i> », « <i>Grzegorz Wozniak</i> »).</li>
        <li><b>homographe hétérophone</b> : un même mot écrit pareil se
          prononce différemment selon le sens (ex. « <i>plus</i> » négatif vs
          comparatif, « <i>couvent</i> » verbe vs nom) — le modèle doit
          deviner la bonne lecture au contexte.</li>
        <li><b>silence / rythme</b> : une ponctuation (« <i>...</i> », tiret)
          qui doit se traduire par une vraie pause plutôt qu'être lue d'un
          bloc.</li>
        <li><b>emprunt anglais</b> : mots anglais intégrés au français
          courant (ex. « <i>starter pack</i> », « <i>kick-off</i> ») — accent
          anglais ou francisé ?</li>
        <li><b>ponctuation répétée</b> : ponctuation empilée pour marquer
          l'intensité (ex. « <i>Encore ! Encore lui !</i> », « <i>?!</i> ») —
          le modèle garde-t-il l'intonation ou lit-il platement ?</li>
        <li><b>onomatopée</b> : un bruit transcrit en mots (ex. «
          <i>*Vroum*</i> », « <i>Rrrmmm...</i> ») — vocalisé comme un bruit,
          ou épelé lettre par lettre (bug fréquent) ?</li>
      </ul>
      <p>Chaque phrase est générée <b>3 fois</b> (seed différente) pour
      mesurer la stabilité d'un modèle sur un même texte. Plus un volet
      long-form (podcast, journalisme).</p></div>
    <div class="card"><span class="tag">Voix de référence</span><h3>Clonage zero-shot sur {n_voix} voix</h3>
      <p>Chaque modèle clone le même jeu de voix de référence, dans plusieurs
      registres :</p>
      <ul>
        <li><b>voix « propre »</b> : enregistrement studio, sans bruit.</li>
        <li><b>voix « difficile »</b> : source brute, prise de son bruitée —
          teste la robustesse du clonage à une référence imparfaite.</li>
        <li><b>voix féminine</b>.</li>
        <li><b>2 voix âgées</b>.</li>
        <li><b>1 accent régional</b>.</li>
        <li><b>registres émotionnels</b> (joie, colère, peur, tristesse) d'une
          même voix — teste si le clonage transporte l'émotion, pas juste le
          timbre.</li>
      </ul>
      <p>Aucun nom de personne n'est publié ; les mêmes fichiers de voix
      servent à tous les modèles, d'une passe à l'autre.</p></div>
    <div class="card"><span class="tag">Pré-traitement</span><h3>Identique pour tous les modèles</h3>
      <ul>
        <li>Apostrophes typographiques (’) normalisées en apostrophe simple
          (') pour tous les modèles.</li>
        <li>Structure markdown retirée (titres <code>#</code>, listes,
          citations <code>&gt;</code>) : seul le texte brut est envoyé.</li>
        <li>Ponctuation adoucie : « <code>...</code> » → « <code>.</code> »,
          et les « <code>!</code> » à l'intérieur d'une onomatopée (ex. «
          <i>*Vroum!*</i> ») sont neutralisés pour ne pas sonner comme une
          exclamation criée.</li>
        <li>Emojis supprimés en amont (aucun modèle testé ne les vocalise
          correctement).</li>
        <li>Les nombres ne sont <b>pas</b> développés en amont (« 1789 »
          reste « 1789 ») : on teste la capacité de chaque modèle à les lire
          lui-même correctement.</li>
      </ul></div>
    <div class="card"><span class="tag">Écoute</span><h3>3 tests humains en aveugle</h3>
      <ul>
        <li><b>Test 1 — A/B</b> : la même phrase, la même voix de référence,
          générée par 2 modèles différents ; l'auditeur·rice choisit celui
          qu'il/elle préfère, sans savoir lesquels sont comparés.</li>
        <li><b>Test 2 — MOS</b> : un clip isolé et anonymisé, noté de 1 à 5 sur
          4 axes (naturel, intelligibilité, similarité, expressivité).</li>
        <li><b>Test 3 — Émotion A/B</b> : comme le test 1, mais les deux clips
          clonent la même voix de référence <i>émotionnelle</i> — lequel des
          deux modèles rend le mieux l'émotion visée ?</li>
      </ul>
      <p>C'est ce test qui fournit la <b>Naturalité</b> du score global : WER
      et SIM sont automatiques et ne mesurent pas si une voix « sonne bien ».
      Détail complet : <a class="link" href="ecoute.html">page Écoute</a>.</p></div>
    <div class="card"><span class="tag">Reproductibilité</span><h3>Révisions figées (<span class="mono">models.lock</span>)</h3>
      <p>Pour chaque modèle : identifiant du dépôt + révision exacte (SHA)
      Hugging&nbsp;Face, et commit GitHub précis pour le code — un
      re-téléchargement redonne bit-à-bit les mêmes poids ; une révision non
      épinglée est refusée. Toutes les mesures sont faites sur la même
      machine (GPU RTX&nbsp;4090, 24&nbsp;Go de VRAM), un seul modèle chargé
      à la fois.</p></div>
  </div>
</section>

<section id="repro">
  <div class="sec-h"><h2>Révisions épinglées</h2><span class="n">Hugging Face</span></div>
  <div class="card repro">{"".join(
      f'<div><span>{_nm(n)}</span><span>{m["revision"] or "—"}</span></div>'
      for n, m in sorted(d["modeles"].items()))}</div>
</section>"""

    js = f"var CFG={json.dumps(cfg, ensure_ascii=False)};ttsTable('#lb',CFG);"
    return _shell("Benchmark TTS français", "index", corps, hero=hero, js=js,
                  standalone=standalone)


# --------------------------------------------------------------------------
# Page métriques — toutes voix confondues
# --------------------------------------------------------------------------
def page_objectif() -> str:
    d = _collecter()
    fiches_obj = _fiches()
    # p2 masqué < 620px, p3 masqué < 900px — modèle/WER/SIM toujours visibles
    cols = [
        {"k": "_nom", "label": "modèle"},
        {"k": "wer", "label": "WER", "dir": -1, "fmt": "pct", "g": .05, "b": .10,
         "desc": "Word Error Rate : taux d'erreur de mot entre le texte demandé et sa "
                 "retranscription par whisper-large-v3-french (calculé avec jiwer). "
                 "Mesure l'intelligibilité. ↓ plus bas = mieux."},
        {"k": "sim", "label": "SIM", "dir": 1, "fmt": "num3", "g": .80, "b": .72,
         "desc": "Similarité de timbre : cosinus entre les embeddings de locuteur "
                 "(ECAPA-TDNN) de l'audio généré et de la voix de référence clonée. "
                 "↑ plus haut = mieux."},
        {"k": "wer_sigma", "label": "±σ", "dir": -1, "fmt": "pct", "g": .08, "b": .15, "p": 2,
         "desc": "Écart-type du WER entre les 3 répétitions (seeds différentes) d'une "
                 "même phrase : mesure la RÉGULARITÉ de la lecture, pas sa qualité — un "
                 "modèle peut avoir un bon WER moyen mais très irrégulier d'une prise à "
                 "l'autre. ↓ plus bas = plus stable."},
        {"k": "rtf", "label": "RTF", "dir": 0, "fmt": "x", "g": .6, "b": 1.5, "p": 2,
         "desc": "Real-Time Factor = temps de génération / durée de l'audio produit "
                 "(cold start du modèle exclu). < 1× = plus rapide que le temps réel."},
        {"k": "cv", "label": "CV durée", "dir": -1, "fmt": "pct", "g": .10, "b": .15, "p": 2,
         "desc": "Coefficient de variation (écart-type / moyenne) de la durée audio "
                 "produite sur les 3 répétitions d'une même phrase — un modèle stable "
                 "doit produire une durée quasi identique pour un texte identique."},
        {"k": "hallu", "label": "hallu.", "dir": -1, "fmt": "pct", "g": .001, "b": .05, "p": 3,
         "desc": "Taux d'« hallucination » : la retranscription Whisper ne retrouve "
                 "qu'une faible part (< 60 %) des mots du texte demandé — signe que le "
                 "modèle a généré un contenu qui s'écarte du texte. Détection "
                 "automatique par comparaison texte ↔ transcription (benchmark/fidelite.py)."},
        {"k": "rep", "label": "rép.", "dir": -1, "fmt": "pct", "g": .001, "b": .05, "p": 3,
         "desc": "Taux de répétition : un mot ou groupe de mots consécutifs anormalement "
                 "répété est détecté dans la transcription (bégaiement / boucle du "
                 "modèle). Détection automatique, même méthode que hallu./tronc."},
        {"k": "tronc", "label": "tronc.", "dir": -1, "fmt": "pct", "g": .001, "b": .05, "p": 3,
         "desc": "Taux de troncature : la fin du texte demandé (dernier(s) mot(s)) est "
                 "absente de la transcription — l'audio s'arrête avant la fin. Détection "
                 "automatique par comparaison texte ↔ transcription."},
        {"k": "ttfa", "label": "TTFA s", "dir": -1, "fmt": "num2", "g": 2.0, "b": 8.0, "p": 3,
         "desc": "Time To First Audio : délai (secondes) avant le premier échantillon "
                 "audio produit par le modèle, hors chargement initial (cold start) — "
                 "mesuré et journalisé par l'adaptateur de chaque modèle."},
        {"k": "vram_go", "label": "VRAM~", "dir": 0, "fmt": "int", "p": 3,
         "desc": "VRAM GPU estimée pour faire tourner le modèle (indicatif, "
                 "models.lock) — pas une mesure du pic réel par run."},
        {"k": "_lic", "label": "licence", "kind": "lic", "p": 3,
         "desc": "Licence déclarée du modèle (benchmark/licences.yaml) et verdict "
                 "d'usage commercial : vert = autorisé, orange = conditionnel, rouge = non commercial."},
    ]
    rows = []
    for n, m in sorted(d["modeles"].items()):
        r = m.get("global")
        if not r:
            continue
        comm = m["usage_commercial"]
        lic = (f'<span class="chip ok">{m["licence"]}</span>' if comm == "oui"
               else f'<span class="chip crit">{m["licence"]}</span>' if comm == "non"
               else f'<span class="chip">{m["licence"]}</span>')
        rows.append({
            "_nom": _nm(n), "_lic": lic, "_detail": _detail_html(r),
            **({"_href": fichier_modele(n)} if n in fiches_obj else {}),
            "wer": r["wer"], "wer_sigma": r["wer_sigma"], "sim": r["sim"],
            "hallu": r["hallu"], "rep": r["rep"], "tronc": r["tronc"],
            "rtf": r["rtf"], "ttfa": r["ttfa"], "cv": r["cv"], "vram_go": m["vram_go"],
        })

    n_ecart = sum((m.get("global") or {}).get("n_voix_ecartees", 0)
                  for m in d["modeles"].values())
    foot = []
    if d["exclus"]:
        foot.append("hors classement : "
                    + " · ".join(f'{_nm(e["nom"])} ({e["motif"]})' for e in d["exclus"]))
    if n_ecart:
        foot.append(f"{n_ecart} combinaison(s) (modèle, voix) au WER&nbsp;>&nbsp;30&nbsp;% "
                    "écartées de la moyenne — clips inexploitables")
    excl = " — ".join(foot)

    corps = f"""<section>
  <div class="sec-h"><h2>Métriques par modèle</h2>
    <span class="n">toutes voix confondues · triable</span></div>
  <p class="lead">Chaque ligne agrège <b>toutes les voix de référence et registres
    émotionnels</b> — moyenne <b>pondérée par le nombre de runs</b> (une voix de
    narration à 99 runs pèse plus qu'un registre émotionnel à 6), <b>hors
    combinaisons au WER&nbsp;>&nbsp;30&nbsp;%</b> (échec de clonage sur cette voix).
    <b>Aucune métrique de naturalité</b> : UTMOS, TTSDS2 et NISQA écartés (non
    pertinents en français) → naturalité = <a class="link" href="ecoute.html">test
    d'écoute</a>. Kokoro n'a qu'une voix interne fixe : ses chiffres ne portent
    que sur elle. Survole un en-tête de colonne pour son explication, clique pour
    trier ; clic sur une ligne pour le détail par phrase (longueur / registre /
    piège). Sur petit écran, seules WER / SIM restent affichées.</p>
  {LEGENDE}
  <div class="tools">
    <label>Trier&nbsp;:
      <select id="msort">
        <option value="wer|a">WER — meilleur d'abord</option>
        <option value="wer|d">WER — pire d'abord</option>
        <option value="sim|d">SIM — meilleur d'abord</option>
        <option value="rtf|a">RTF — plus rapide</option>
        <option value="cv|a">CV durée — plus stable</option>
      </select></label>
    <span class="mono" style="color:var(--muted);font-size:.8rem" id="compte"></span>
  </div>
  <div class="board"><div id="tbl"></div>
    {f'<div class="board-foot">{excl}</div>' if excl else ''}</div>
</section>"""

    js = (f"var CFG={{cols:{json.dumps(cols, ensure_ascii=False)},"
          f"rows:{json.dumps(rows, ensure_ascii=False)},"
          "sort:{k:'wer',asc:true},msort:document.getElementById('msort')};"
          "document.getElementById('compte').textContent="
          "CFG.rows.length+' modèles · toutes voix confondues';"
          "ttsTable('#tbl',CFG);")
    return _shell("Métriques par modèle — Benchmark TTS FR", "objectif", corps, js=js)


# --------------------------------------------------------------------------
# Page écoute (rendu markdown)
# --------------------------------------------------------------------------
def _inline(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def md_vers_html(md: str) -> str:
    out: list[str] = []
    lignes = md.splitlines()
    i, n = 0, len(lignes)
    while i < n:
        ligne = lignes[i]
        if not ligne.strip():
            i += 1
            continue
        m = re.match(r"(#{1,4})\s+(.*)", ligne)
        if m:
            niv = len(m.group(1))
            out.append(f"<h{niv}>{_inline(m.group(2))}</h{niv}>")
            i += 1
            continue
        if ligne.lstrip().startswith("|") and i + 1 < n and re.match(r"\s*\|?[\s:\-|]+\|?\s*$", lignes[i + 1]):
            def cells(row: str) -> list[str]:
                return [c.strip() for c in row.strip().strip("|").split("|")]
            entete = cells(ligne)
            out.append("<div class='tablewrap'><table><thead><tr>"
                       + "".join(f"<th>{_inline(c)}</th>" for c in entete)
                       + "</tr></thead><tbody>")
            i += 2
            while i < n and lignes[i].lstrip().startswith("|"):
                out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells(lignes[i])) + "</tr>")
                i += 1
            out.append("</tbody></table></div>")
            continue
        if ligne.lstrip().startswith(("- ", "* ")):
            out.append("<ul>")
            while i < n and lignes[i].lstrip().startswith(("- ", "* ")):
                out.append("<li>" + _inline(lignes[i].lstrip()[2:]) + "</li>")
                i += 1
            out.append("</ul>")
            continue
        if ligne.lstrip().startswith(">"):
            buf = []
            while i < n and lignes[i].lstrip().startswith(">"):
                buf.append(lignes[i].lstrip()[1:].strip())
                i += 1
            out.append("<blockquote>" + _inline(" ".join(buf)) + "</blockquote>")
            continue
        buf = [ligne]
        i += 1
        while i < n and lignes[i].strip() and not re.match(r"[#|>\-*]", lignes[i].lstrip()[:1]):
            buf.append(lignes[i])
            i += 1
        out.append("<p>" + _inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


def page_ecoute() -> str:
    d = _ecoute_json()
    if not d:
        corps = """<section>
  <div class="sec-h"><h2>Test d'écoute</h2><span class="n">en attente de retours</span></div>
  <p class="lead">Aucune agrégation pour l'instant. Fais passer le test
    (<span class="mono">site/ecoute/index.html</span>), dépose les exports dans
    <span class="mono">exports/</span>, puis lance
    <span class="mono">agreger_ecoute.py</span> puis <span class="mono">build_pages.py</span>.</p>
</section>"""
        return _shell("Test d'écoute — Benchmark TTS FR", "ecoute", corps)

    p = d["panel"]
    ab, mos, emo = d.get("ab"), d.get("mos"), d.get("emo")
    js_parts: list[str] = []
    blocs: list[str] = []

    intro = f"""<section id="intro">
  <div class="sec-h"><h2>Test d'écoute — méthode</h2>
    <span class="n">{p['auditeurs']} auditeur·rice·s, en aveugle</span></div>
  <p class="lead">Le classement automatique (WER, SIM) ne dit rien de ce qu'une
    oreille humaine perçoit. Ce test le complète avec <b>3 protocoles
    distincts</b>, tous en aveugle — aucun nom de modèle n'est jamais affiché,
    aucun nom de voix ni de participant n'est publié : une comparaison directe
    entre deux modèles (<b>Test&nbsp;1</b>), une notation isolée de chaque clip
    (<b>Test&nbsp;2</b>), et une comparaison ciblée sur le rendu de l'émotion
    (<b>Test&nbsp;3</b>). Panel : {p['ab']} comparaisons A/B, {p['mos']} notes
    MOS, {p['emo']} votes émotion.</p>
</section>"""
    blocs.append(intro)

    # ======================= TEST 1 — A/B =======================
    t1 = ['<section id="test1" class="testblock"><div class="testhead">'
          '<span class="eyebrow">Test 1</span><h1>Comparaison A/B</h1>'
          '<p class="lead">Ce test met en comparaison la <b>même phrase</b>, dite '
          'par la <b>même voix de référence</b> clonée, générée par <b>2 modèles '
          'différents</b>. L\'auditeur·rice écoute les deux clips à l\'aveugle '
          '(sans savoir quels modèles sont comparés) et choisit celui qu\'il ou '
          'elle préfère globalement ; il/elle peut aussi signaler des défauts '
          'précis entendus sur chaque clip (voix qui ne ressemble pas à la '
          'référence, coupure/troncature, répétition, accent, artefact).</p>'
          '</div>']
    if ab and ab.get("stats"):
        rows_ab = [{"_nom": _nm(m), "_slug": m, "winrate": s["winrate"],
                    "victoires": s["victoires"], "n": s["n"]}
                   for m, s in ab["stats"].items()]
        cols_ab = [
            {"k": "_nom", "label": "modèle"},
            {"k": "winrate", "label": "win-rate", "dir": 1, "fmt": "pct", "g": .55, "b": .45},
            {"k": "victoires", "label": "victoires", "fmt": "num1"},
            {"k": "n", "label": "duels"},
        ]
        t1.append('<h3 class="subhead">Win-rate par modèle'
                   '<span class="n">victoire = 1 point, égalité = ½ point</span></h3>')
        t1.append('<div class="board"><div id="tbl-ab"></div></div>')
        js_parts.append(
            f"var CFG_AB={{cols:{json.dumps(cols_ab, ensure_ascii=False)},"
            f"rows:{json.dumps(rows_ab, ensure_ascii=False)},"
            "sort:{k:'winrate',asc:false},rankcol:true};ttsTable('#tbl-ab',CFG_AB);")

        ordre_ab = sorted(ab["stats"], key=lambda m: -ab["stats"][m]["winrate"])
        t1.append('<h3 class="subhead">Matrice des duels'
                   '<span class="n">ligne vs colonne — vert = la ligne gagne, '
                   'rouge = elle perd</span></h3>')
        t1.append(_matrice_html(ab.get("duel", {}), ordre_ab))

        svg_def = _defauts_svg(ab)
        if svg_def:
            t1.append('<h3 class="subhead">Défauts entendus par modèle'
                       '<span class="n">taux par duel (comparable malgré des '
                       'expositions inégales)</span></h3>')
            t1.append(f'<div class="scope" style="margin-top:0">{svg_def}</div>')
            t1.append('<p class="lead" style="margin-top:10px;font-size:.82rem">'
                       + " · ".join(f"<b>{lab}</b> = {DEFAUT_LABELS[k]}"
                                     for k, lab in DEFAUT_LABELS_COURT.items())
                       + "</p>")
    else:
        t1.append('<p class="lead">Aucun vote A/B pour l\'instant.</p>')
    t1.append('</section>')
    blocs.append("".join(t1))

    # ======================= TEST 2 — MOS =======================
    t2 = ['<section id="test2" class="testblock"><div class="testhead">'
          '<span class="eyebrow">Test 2</span><h1>Notes MOS</h1>'
          '<p class="lead">Contrairement au test 1, il n\'y a pas de comparaison '
          'directe : chaque clip est écouté <b>isolément</b> et anonymisé, puis '
          'noté de 1 (mauvais) à 5 (excellent) sur 4 axes — <b>Naturel</b> '
          '(sonne-t-il comme une vraie voix humaine ?), <b>Intelligibilité</b> '
          '(comprend-on tout ?), <b>Similarité</b> (ressemble-t-il à la voix de '
          'référence ?), <b>Expressivité</b> (le ton correspond-il à la '
          'phrase ?).</p></div>']
    if mos and mos.get("par_modele"):
        axes_k = [("naturel", "Naturel"), ("intelligibilite", "Intelligibilité"),
                  ("similarite", "Similarité"), ("expressivite", "Expressivité")]
        rows_mos = []
        for m, axes in mos["par_modele"].items():
            row = {"_nom": _nm(m), "_slug": m}
            for k, _ in axes_k:
                v = axes.get(k)
                row[k] = v["moyenne"] if v else None
                row[k + "_ic"] = v["ic"] if v else None
            rows_mos.append(row)
        cols_mos = [{"k": "_nom", "label": "modèle"}] + [
            {"k": k, "label": lab, "dir": 1, "kind": "mos", "g": 3.5, "b": 2.5}
            for k, lab in axes_k
        ]
        t2.append('<h3 class="subhead">Moyenne ± IC 95&nbsp;% par axe'
                   '<span class="n">clic sur un en-tête pour trier</span></h3>')
        t2.append('<div class="board"><div id="tbl-mos"></div></div>')
        js_parts.append(
            f"var CFG_MOS={{cols:{json.dumps(cols_mos, ensure_ascii=False)},"
            f"rows:{json.dumps(rows_mos, ensure_ascii=False)},"
            "sort:{k:'naturel',asc:false},rankcol:true};ttsTable('#tbl-mos',CFG_MOS);")

        if mos.get("correlations"):
            t2.append('<h3 class="subhead">Corrélation avec les métriques automatiques'
                       '<span class="n">à titre d\'info</span></h3>')
            t2.append('<p class="lead">Le coefficient de Pearson (<span class="mono">r</span>, '
                       'de −1 à 1) mesure si la note humaine et la métrique automatique '
                       'équivalente varient ensemble, clip par clip : proche de 1 = la '
                       'métrique automatique est un bon indicateur du jugement humain sur '
                       'cet axe ; proche de 0 = aucun lien. Sert à vérifier si WER/SIM '
                       'peuvent remplacer l\'oreille humaine — ici, non : voir '
                       '<a class="link" href="index.html#lecture">pourquoi la naturalité '
                       'reste jugée à l\'écoute</a>.</p>')
            axe_labels = dict(axes_k)
            rows_c = [{"_nom": f'{axe_labels.get(c["axe_humain"], c["axe_humain"])} ↔ {c["metrique"]}',
                       "pearson": c["pearson"], "n": c["n"]} for c in mos["correlations"]]
            cols_c = [
                {"k": "_nom", "label": "axe humain ↔ métrique auto"},
                {"k": "pearson", "label": "pearson r", "dir": 1, "fmt": "num2", "g": .5, "b": .2},
                {"k": "n", "label": "n"},
            ]
            t2.append('<div class="board"><div id="tbl-corr"></div></div>')
            js_parts.append(
                f"var CFG_CORR={{cols:{json.dumps(cols_c, ensure_ascii=False)},"
                f"rows:{json.dumps(rows_c, ensure_ascii=False)},"
                "sort:{k:'pearson',asc:false}};ttsTable('#tbl-corr',CFG_CORR);")
    else:
        t2.append('<p class="lead">Aucune note MOS pour l\'instant.</p>')
    t2.append('</section>')
    blocs.append("".join(t2))

    # ======================= TEST 3 — ÉMOTION A/B =======================
    t3 = ['<section id="test3" class="testblock"><div class="testhead">'
          '<span class="eyebrow">Test 3</span><h1>Émotion A/B</h1>'
          '<p class="lead">Comme le test 1 (comparaison à l\'aveugle de 2 modèles '
          'sur la même phrase), mais les deux clips clonent ici la <b>même voix '
          'de référence émotionnelle</b> (ex. la voix « en colère » du même '
          'intervenant) sur une phrase du registre correspondant. La question '
          'n\'est plus « quel modèle est le meilleur en général ? » mais '
          '« lequel des deux rend le mieux <i>cette émotion précise</i> ? ».</p></div>']
    if emo and emo.get("global"):
        rows_g = [{"_nom": _nm(m), "_slug": m, "winrate": s["winrate"],
                   "victoires": s["victoires"], "n": s["n"]}
                  for m, s in emo["global"].items()]
        cols_g = [
            {"k": "_nom", "label": "modèle"},
            {"k": "winrate", "label": "win-rate", "dir": 1, "fmt": "pct", "g": .55, "b": .45},
            {"k": "victoires", "label": "victoires", "fmt": "num1"},
            {"k": "n", "label": "duels"},
        ]
        t3.append('<h3 class="subhead">Win-rate global par modèle</h3>')
        t3.append('<div class="board"><div id="tbl-emo"></div></div>')
        js_parts.append(
            f"var CFG_EMO={{cols:{json.dumps(cols_g, ensure_ascii=False)},"
            f"rows:{json.dumps(rows_g, ensure_ascii=False)},"
            "sort:{k:'winrate',asc:false},rankcol:true};ttsTable('#tbl-emo',CFG_EMO);")

        emotions = emo.get("emotions", [])
        if emotions:
            rows_pe = []
            for m in emo["global"]:
                row = {"_nom": _nm(m), "_slug": m}
                for e in emotions:
                    x = emo["par_emotion"].get(m, {}).get(e)
                    row[e] = (x["victoires"] / x["n"]) if x and x["n"] else None
                rows_pe.append(row)
            cols_pe = [{"k": "_nom", "label": "modèle"}] + [
                {"k": e, "label": EMOTION_LABELS.get(e, e), "dir": 1, "fmt": "pct", "g": .55, "b": .45}
                for e in emotions
            ]
            t3.append('<h3 class="subhead">Win-rate par modèle × émotion</h3>')
            t3.append('<div class="board"><div id="tbl-emo-pe"></div></div>')
            js_parts.append(
                f"var CFG_EMOPE={{cols:{json.dumps(cols_pe, ensure_ascii=False)},"
                f"rows:{json.dumps(rows_pe, ensure_ascii=False)},"
                "sort:{k:'"+ (emotions[0]) +"',asc:false},rankcol:true};"
                "ttsTable('#tbl-emo-pe',CFG_EMOPE);")

        ordre_emo = sorted(emo["global"], key=lambda m: -emo["global"][m]["winrate"])
        t3.append('<h3 class="subhead">Matrice des duels'
                   '<span class="n">ligne vs colonne — vert = la ligne gagne, '
                   'rouge = elle perd</span></h3>')
        t3.append(_matrice_html(emo.get("duel", {}), ordre_emo))
    else:
        t3.append('<p class="lead">Aucun vote émotion pour l\'instant.</p>')
    t3.append('</section>')
    blocs.append("".join(t3))

    corps = "\n\n".join(blocs)
    js = "\n".join(js_parts)
    return _shell("Test d'écoute — Benchmark TTS FR", "ecoute", corps, js=js)


# --------------------------------------------------------------------------
# Page « fiche modèle » — une par modèle scoré
# --------------------------------------------------------------------------
def fichier_modele(slug: str) -> str:
    return f"modele-{slug}.html"


_CACHE_FICHES: dict | None = None


def _fiches() -> dict:
    """Registre des fiches (vide si absent : les autres pages restent générables)."""
    global _CACHE_FICHES
    if _CACHE_FICHES is None:
        try:
            from benchmark.fiches import charger_fiches
            _CACHE_FICHES = charger_fiches()
        except Exception as e:  # noqa: BLE001 — registre cassé = fiches sautées, pas un build cassé
            print(f"[build_pages] fiches_modeles.yaml ignoré : {e}")
            _CACHE_FICHES = {}
    return _CACHE_FICHES


def _mesures_modele(slug: str) -> tuple[dict | None, dict]:
    """(agrégat toutes voix, meta du run) depuis `resultats/<slug>.json`."""
    f = RESULTATS / f"{slug}.json"
    if not f.is_file():
        return None, {}
    data = json.loads(f.read_text(encoding="utf-8"))
    par_voix: dict[str, dict] = {}
    meta: dict = {}
    for voix, r in data.items():
        s, g, st = r["synthese"], r["vitesse"]["global"], r["stabilite"]
        meta = meta or r.get("meta", {})
        par_voix[voix] = {
            "n": s.get("n_verifiees") or s.get("n_runs") or 0,
            "clonage": r["meta"].get("params", {}).get("clonage", True),
            "wer": s["wer_moyen"], "wer_sigma": s["wer_ecart_type"],
            "wer_net": s.get("wer_net_plancher"), "sim": s.get("sim_moyen"),
            "hallu": s["taux_hallucination"], "rep": s["taux_repetition"],
            "tronc": s["taux_troncature"], "rtf": g["rtf"]["moyenne"],
            "ttfa": g["ttfa_s"]["moyenne"], "cv": st["cv_median"],
            "n_suspects": st["n_suspects"],
        }
    return _agrege(par_voix), meta


def page_modele(slug: str, fiche: dict) -> str:
    lock = _lock().get(slug, {})
    lic = _licences().get(slug, {})
    agg, meta = _mesures_modele(slug)
    dc = _ecoute_json()
    nom = _nm(slug)

    comm = lic.get("usage_commercial", "?")
    chip_lic = (f'<span class="chip ok">{lic.get("licence", "?")} · usage commercial</span>'
                if comm == "oui" else
                f'<span class="chip crit">{lic.get("licence", "?")} · non commercial</span>'
                if comm == "non" else
                f'<span class="chip warn">{lic.get("licence", "?")} · conditionnel</span>')
    statut = lock.get("statut", "")
    chip_statut = (f'<span class="chip warn">{STATUT_MOTIF.get(statut, statut)}</span>'
                   if statut and statut != "verifie" else "")
    chip_clone = ('<span class="chip">clonage zero-shot</span>' if lock.get("clonage_zero_shot")
                  else '<span class="chip">voix internes (pas de clonage)</span>')

    hero = f"""<div class="hero" id="top"><div class="wrap">
  <div class="eyebrow"><a href="index.html" style="color:inherit">← Benchmark</a> · Fiche modèle</div>
  <h1>{html.escape(nom)}</h1>
  <p class="thesis">{_inline(fiche["une_phrase"].strip())}</p>
  <div class="flags" style="margin-top:4px">{chip_lic}{chip_clone}{chip_statut}</div>
</div></div>"""

    # --- ce qu'on mesure ---
    mesures = ""
    if agg:
        def li(label, val):
            return (f'<div class="kv"><span class="k">{label}</span>'
                    f'<span class="v mono">{val}</span></div>')
        sim = f'{agg["sim"]:.3f}' if agg.get("sim") is not None else "—"
        mesures = f"""
  <div class="kvgrid">
    {li("WER moyen (toutes voix)", f'{agg["wer"]*100:.1f}&nbsp;%')}
    {li("SIM (similarité de timbre)", sim)}
    {li("Facteur temps réel (RTF)", f'{agg["rtf"]:.2f}×')}
    {li("Stabilité de durée (CV)", f'{agg["cv"]*100:.1f}&nbsp;%')}
    {li("Phrases avec hallucination", f'{agg["hallu"]*100:.1f}&nbsp;%')}
    {li("Phrases avec répétition", f'{agg["rep"]*100:.1f}&nbsp;%')}
    {li("Phrases tronquées", f'{agg["tronc"]*100:.1f}&nbsp;%')}
    {li("VRAM estimée", f'{lock.get("vram_go_estimee", "?")} Go')}
    {li("Voix mesurées", f'{agg["n_voix"]} voix · {agg["n"]} runs')}
  </div>"""

    ec_bloc = ""
    if dc:
        morceaux = []
        ab = (dc.get("ab") or {}).get("stats", {}).get(slug)
        if ab:
            morceaux.append(f'<div class="kv"><span class="k">Test 1 — A/B (préférence humaine)</span>'
                            f'<span class="v mono">{ab["winrate"]*100:.0f}&nbsp;% '
                            f'<span class="ic">sur {ab["n"]} duels</span></span></div>')
        mm = (dc.get("mos") or {}).get("par_modele", {}).get(slug, {})
        for axe, lab in (("naturel", "Naturel"), ("similarite", "Similarité"),
                         ("expressivite", "Expressivité")):
            if mm.get(axe):
                morceaux.append(f'<div class="kv"><span class="k">Test 2 — MOS {lab} (1–5)</span>'
                                f'<span class="v mono">{mm[axe]["moyenne"]:.2f} '
                                f'<span class="ic">±{mm[axe]["ic"]:.2f} · n={mm[axe]["n"]}</span>'
                                f'</span></div>')
        emo = (dc.get("emo") or {}).get("global", {}).get(slug)
        if emo:
            morceaux.append(f'<div class="kv"><span class="k">Test 3 — Émotion A/B</span>'
                            f'<span class="v mono">{emo["winrate"]*100:.0f}&nbsp;% '
                            f'<span class="ic">sur {emo["n"]} duels</span></span></div>')
        if morceaux:
            ec_bloc = (f'<h3 class="subhead">À l\'oreille<span class="n">test d\'écoute en '
                       f'aveugle</span></h3><div class="kvgrid">{"".join(morceaux)}</div>')

    # --- réglages de génération réellement utilisés ---
    params = meta.get("params", {}) if meta else {}
    reglages = ""
    if params:
        lignes = "".join(
            f'<div class="kv"><span class="k mono">{html.escape(str(k))}</span>'
            f'<span class="v mono">{html.escape(json.dumps(v, ensure_ascii=False))}</span></div>'
            for k, v in sorted(params.items()))
        reglages = f"""
<section id="reglages">
  <div class="sec-h"><h2>Réglages de génération utilisés</h2>
    <span class="n">relevés dans les métadonnées de nos runs</span></div>
  <p class="lead">Ces valeurs sont celles réellement passées au modèle pour produire
    les audios mesurés — pas des réglages recommandés recopiés d'une documentation.
    Elles sont écrites par l'adaptateur dans le <span class="mono">meta.json</span>
    de chaque run.</p>
  <div class="kvgrid">{lignes}</div>
</section>"""

    cartes = "".join(
        f'<div class="card"><h3>{html.escape(b["titre"])}</h3>'
        f'<p>{_inline(b["texte"].strip())}</p></div>'
        for b in fiche["choix_techniques"])

    lg = fiche["langues"]
    langues = f"""
<section id="langues">
  <div class="sec-h"><h2>Langues couvertes</h2>
    <span class="n">{_inline(str(lg["source"]))}</span></div>
  <p class="lead" style="font-size:1.02rem;color:var(--ink)">
    <b>{_inline(str(lg["resume"]).strip())}</b></p>
  {f'<p class="lead">{_inline(str(lg["detail"]).strip())}</p>' if lg.get("detail") else ''}
</section>"""

    lignes_p = "".join(
        f'<tr><td class="name mono" data-label="paramètre">{_inline(str(p["nom"]))}</td>'
        f'<td class="mono defaut" data-label="défaut">{_inline(str(p.get("defaut", "—")))}</td>'
        f'<td class="role" data-label="ce que ça change">{_inline(str(p["role"]).strip())}</td></tr>'
        for p in fiche["parametres"])
    reglables = f"""
<section id="reglables">
  <div class="sec-h"><h2>Ce qu'on peut régler</h2>
    <span class="n">paramètres exposés par ce modèle</span></div>
  <p class="lead">Relevé dans la signature du code réellement installé pour nos runs
    (et dans la documentation officielle quand elle précise les valeurs
    recommandées). Chaque modèle expose des leviers différents : c'est souvent
    là que se joue la différence entre un résultat correct et un bon résultat.</p>
  <div class="board"><div class="tablewrap"><table class="rt params empile">
    <thead><tr><th class="name">paramètre</th><th style="text-align:center">défaut</th>
      <th class="name">ce que ça change</th></tr></thead>
    <tbody>{lignes_p}</tbody></table></div></div>
</section>"""

    savoir = ""
    if fiche.get("a_savoir"):
        items = "".join(f"<li>{_inline(str(x).strip())}</li>" for x in fiche["a_savoir"])
        savoir = f"""
<section id="a-savoir">
  <div class="sec-h"><h2>À savoir avant de l'utiliser</h2>
    <span class="n">pièges, limites, nuances de licence</span></div>
  <ul class="avert">{items}</ul>
</section>"""

    src = "".join(
        f'<div><span><a class="link" href="{html.escape(s["url"])}">{html.escape(s["label"])}</a></span>'
        f'<span>{html.escape(s["url"].split("//")[-1][:46])}</span></div>'
        for s in fiche["sources"])
    rev = lock.get("revision") or ""
    note_lic = lic.get("note") or ""

    corps = f"""<section id="distingue">
  <div class="sec-h"><h2>Ce qui le distingue</h2></div>
  <p class="lead">{_inline(fiche["particularite"].strip())}</p>
</section>

<section id="choix">
  <div class="sec-h"><h2>Choix techniques</h2>
    <span class="n">ce que ses auteurs ont décidé, et ce que ça implique</span></div>
  <div class="cards">{cartes}</div>
</section>
{langues}
{reglables}

<section id="mesures">
  <div class="sec-h"><h2>Ce qu'on mesure sur ce modèle</h2>
    <span class="n">nos runs, pas les chiffres de l'éditeur</span></div>
  {mesures or '<p class="lead">Pas encore de mesures publiées pour ce modèle.</p>'}
  {ec_bloc}
  <p class="lead" style="margin-top:14px">Détail complet :
    <a class="link" href="objectif.html">table de toutes les métriques</a> ·
    <a class="link" href="ecoute.html">résultats du test d'écoute</a>.</p>
</section>
{reglages}
{savoir}

<section id="sources">
  <div class="sec-h"><h2>Sources &amp; vérification</h2>
    <span class="n">vérifié le {html.escape(str(fiche["verifie_le"]))}</span></div>
  <p class="lead">Les comptes de paramètres cités plus haut sont lus directement dans
    les fichiers de poids de la révision épinglée ci-dessous (en-têtes safetensors /
    torch), pas repris d'une annonce. Les caractéristiques annoncées proviennent de la
    model card officielle, liée ici. Les chiffres de performance viennent de nos propres
    runs.</p>
  <div class="card repro">
    <div><span>Dépôt de poids</span><span>{html.escape(lock.get("repo_id", "—"))}</span></div>
    <div><span>Révision épinglée</span><span>{html.escape(rev[:16] or "—")}</span></div>
    {f'<div><span>Code épinglé</span><span>{html.escape(str(lock.get("code_ref"))[:60])}</span></div>' if lock.get("code_ref") else ''}
    <div><span>Licence déclarée</span><span>{html.escape(str(lic.get("licence", "?")))}</span></div>
  </div>
  {f'<p class="lead" style="margin-top:12px"><b>Note de licence</b> : {_inline(note_lic)}</p>' if note_lic else ''}
  <div class="card repro" style="margin-top:14px">{src}</div>
</section>"""
    return _shell(f"{nom} — fiche modèle · Benchmark TTS FR", "modeles", corps, hero=hero)


def build() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / "index.html").write_text(page_index(), encoding="utf-8")
    (SORTIE / "objectif.html").write_text(page_objectif(), encoding="utf-8")
    (SORTIE / "ecoute.html").write_text(page_ecoute(), encoding="utf-8")
    fiches = _fiches()
    for slug, fiche in sorted(fiches.items()):
        (SORTIE / fichier_modele(slug)).write_text(page_modele(slug, fiche), encoding="utf-8")
    print(f"[build_pages] -> {SORTIE}/ (index.html, objectif.html, ecoute.html"
          + (f", {len(fiches)} fiches modèle)" if fiches else ")"))


if __name__ == "__main__":
    build()
