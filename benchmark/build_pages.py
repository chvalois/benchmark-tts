#!/usr/bin/env python3
"""Génère le site de résultats statique (`site/resultats/`).

- `index.html`    : page projet — classement (auto + écoute) + méthode.
- `objectif.html` : table complète des métriques auto, **toutes voix
  confondues** (moyenne pondérée par le nb de runs), triable, détail par
  modèle (WER par longueur / registre / piège).
- `ecoute.html`   : rendu de `resultats/ecoute.md` (test d'écoute humain).

Pages autonomes (données injectées, Google Fonts) — ouvrables en `file://`.
**Aucun nom de voix de référence ni de participant** : que des agrégats.

    source env.sh
    python3 benchmark/build_pages.py
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

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
}


def _nm(slug: str) -> str:
    return NOM_MODELE.get(slug, slug)

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
header.bar nav a{font-size:.84rem;color:var(--muted);padding:7px 9px;border-radius:7px}
header.bar nav a:hover{color:var(--ink)}
header.bar nav a.on{color:var(--ink);background:var(--panel2)}
.tgl{margin-left:4px;width:32px;height:32px;display:grid;place-items:center;border-radius:7px;
  border:1px solid var(--line);background:var(--panel);color:var(--muted);cursor:pointer}
.tgl:hover{color:var(--ink)}

/* hero */
.hero{padding:48px 0 36px;border-bottom:1px solid var(--line)}
.eyebrow{font:500 .7rem/1 "IBM Plex Mono",monospace;letter-spacing:.2em;
  text-transform:uppercase;color:var(--trace);margin-bottom:16px}
.hero h1{font-family:"Newsreader",Georgia,serif;font-weight:400;
  font-size:clamp(1.9rem,6vw,3.1rem);line-height:1.08;letter-spacing:-.012em;
  text-wrap:balance;margin:0 0 14px;max-width:16ch}
.hero .thesis{font-size:1.02rem;color:var(--muted);max-width:56ch;margin:0 0 24px}
.hero .thesis em{font-family:"Newsreader",serif;font-style:italic;color:var(--ink)}
.facts{display:flex;flex-wrap:wrap;gap:8px}
.fact{font:.76rem/1 "IBM Plex Mono",monospace;color:var(--muted);
  border:1px solid var(--line);border-radius:6px;padding:7px 9px;background:var(--panel)}
.fact b{color:var(--ink);font-weight:500}
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
.lead{color:var(--muted);max-width:66ch;margin:-4px 0 18px;font-size:.95rem}

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
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.card{border:1px solid var(--line);border-radius:12px;background:var(--panel);padding:16px 18px}
.card h3{margin:0 0 6px;font-size:.94rem;font-weight:600}
.card p{margin:0;color:var(--muted);font-size:.88rem}
.card .tag{font:.66rem/1 "IBM Plex Mono",monospace;letter-spacing:.1em;text-transform:uppercase;
  color:var(--trace);display:block;margin-bottom:9px}
.repro{font-family:"IBM Plex Mono",monospace;font-size:.8rem;line-height:1.8}
.repro div{display:flex;gap:12px;justify-content:space-between;
  border-bottom:1px dashed var(--line);padding:4px 0}
.repro span:last-child{color:var(--faint)}

/* md */
.md h1{font-family:"Newsreader",serif;font-weight:400;font-size:1.9rem;margin:0 0 8px}
.md h2{font-family:"Newsreader",serif;font-weight:500;font-size:1.35rem;margin:1.8em 0 .5em}
.md h3{font-size:.98rem;margin:1.5em 0 .4em;color:var(--muted)}
.md p,.md ul{color:var(--muted);max-width:70ch}
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
.md .ic{color:var(--faint);font-size:.85em;font-weight:400}
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
        +(sort.k===c.k?' data-active':'')+'>'+c.label
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
        }
        tr+='<td class="'+(k+pc).trim()+'">'+inner+'</td>';
      });
      tr+='</tr>';
      if(row._detail){
        tr+='<tr class="detail" data-i="'+i+'"'+(open[row._nom]?'':' hidden')+'><td colspan="'
          +(cfg.cols.length+(cfg.rankcol?1:0))+'">'+row._detail+'</td></tr>';
      }
      body+=tr;
    });
    mount.innerHTML='<div class="tablewrap"><table class="rt"><thead>'+th
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
  <nav>{nav}<button class="tgl" id="tgl" title="Thème" aria-label="Changer de thème">◑</button></nav>
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
        if lk.get("statut") == "fr_non_supporte":
            exclus.append({"nom": f.stem, "motif": "FR non supporté"})
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
def _scope_svg(d: dict) -> str:
    items = sorted(
        ((m["global"]["wer"], _nm(n)) for n, m in d["modeles"].items()
         if (m.get("global") or {}).get("wer") is not None
         and m["global"]["wer"] < 0.5),
        key=lambda x: x[0],
    )
    if not items:
        return ""
    W, rowh, padL, padR = 560, 28, 140, 46
    ech = max(0.08, max(w for w, _ in items) * 1.12)
    span = W - padL - padR
    H = 28 + rowh * len(items)
    out = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
           f'aria-label="WER par modèle" '
           f'style="min-width:460px;font-family:\'IBM Plex Mono\',monospace">']
    for gx in [g / 100 for g in range(0, int(ech * 100) + 1, 2)]:
        x = padL + gx / ech * span
        out.append(f'<line x1="{x:.0f}" y1="12" x2="{x:.0f}" y2="{H-16}" '
                   f'stroke="var(--line)" stroke-width="1"/>')
        out.append(f'<text x="{x:.0f}" y="{H-3}" text-anchor="middle" font-size="9" '
                   f'fill="var(--faint)">{gx*100:.0f}%</text>')
    for i, (wer, nom) in enumerate(items):
        y = 22 + i * rowh
        x2 = padL + wer / ech * span
        out.append(f'<text x="{padL-10:.0f}" y="{y+4:.0f}" text-anchor="end" '
                   f'font-size="10.5" fill="var(--muted)">{html.escape(nom)}</text>')
        out.append(f'<line x1="{padL}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y:.0f}" '
                   f'stroke="var(--trace)" stroke-width="6" stroke-linecap="round" '
                   f'opacity="{0.9 - 0.45*(wer/ech):.2f}"/>')
        out.append(f'<circle cx="{x2:.0f}" cy="{y:.0f}" r="3.4" fill="var(--trace)"/>')
        out.append(f'<text x="{x2+8:.0f}" y="{y+4:.0f}" font-size="10.5" '
                   f'fill="var(--ink)">{wer*100:.1f}%</text>')
    out.append('</svg>')
    return "".join(out)


_AXES_MOS = ("Naturel", "Intelligibilite", "Similarite", "Expressivite")


def _ecoute_donnees() -> dict | None:
    """Parse `resultats/ecoute.md` → {panel, mos{modele:{axe:(moy,ic)}}, ab{modele:winrate}}."""
    f = RESULTATS / "ecoute.md"
    if not f.is_file():
        return None
    txt = f.read_text(encoding="utf-8")
    panel = re.search(r"(\d+) auditeur\(s\)[^\n]*?(\d+) votes A/B, (\d+) notes MOS, "
                      r"(\d+) votes émotion", txt)

    def _bloc(titre: str) -> list[list[str]]:
        m = re.search(rf"## {re.escape(titre)}[^\n]*\n\n(.*?)(?:\n\n|\Z)", txt, re.S)
        if not m:
            return []
        out = []
        for ln in m.group(1).splitlines():
            if not ln.strip().startswith("|") or re.match(r"\s*\|[\s:\-|]+\|\s*$", ln):
                continue
            out.append([c.strip() for c in ln.strip().strip("|").split("|")])
        return out

    mos: dict[str, dict] = {}
    rows = _bloc("MOS — moyenne ± IC 95 % par axe")
    entete = rows[0] if rows else []
    for c in rows[1:]:
        if len(c) < 2:
            continue
        d: dict[str, tuple] = {}
        for j, axe in enumerate(entete[1:], 1):
            mm = re.match(r"([\d.]+)\s*±\s*([\d.]+)", c[j]) if j < len(c) else None
            if mm:
                d[axe] = (float(mm.group(1)), float(mm.group(2)))
        if d:
            mos[c[0]] = d

    ab: dict[str, str] = {}
    for c in _bloc("A/B — win-rate par modèle")[1:]:
        if len(c) >= 2 and c[1].endswith("%"):
            ab[c[0]] = c[1]

    return {"panel": panel.groups() if panel else None, "mos": mos, "ab": ab}


def _ecoute_resume(dc: dict | None = None) -> str | None:
    dc = dc if dc is not None else _ecoute_donnees()
    if not dc:
        return None
    parts = []
    if dc["panel"]:
        n, a, m, e = dc["panel"]
        parts.append(f"{n} auditeur·rice·s · {a} votes A/B · {m} notes MOS · {e} émotion")
    if dc["mos"]:
        top = max(dc["mos"].items(), key=lambda kv: kv[1].get("Naturel", (0,))[0])
        parts.append(f"plus naturel à l'oreille : <b>{_nm(top[0])}</b> "
                     f"(MOS {top[1]['Naturel'][0]:.2f}/5)")
    return " — ".join(parts) if parts else "résultats disponibles"


def _ecoute_classement_html(dc: dict) -> str:
    """Tableau : classement des modèles par MOS « Naturel » + win-rate A/B."""
    if not dc or not dc["mos"]:
        return ""
    lignes = sorted(dc["mos"].items(),
                    key=lambda kv: -kv[1].get("Naturel", (0,))[0])

    def cell(v):
        return f'<td class="num">{v[0]:.2f}</td>' if v else "<td>—</td>"

    tr = []
    for i, (mod, ax) in enumerate(lignes, 1):
        nat = ax.get("Naturel")
        natc = (f'<td class="num"><b>{nat[0]:.2f}</b> '
                f'<span class="ic">±{nat[1]:.2f}</span></td>') if nat else "<td>—</td>"
        tr.append(
            f"<tr><td>{i}</td><td><b>{_nm(mod)}</b></td>{natc}"
            f"{cell(ax.get('Intelligibilite'))}{cell(ax.get('Similarite'))}"
            f"{cell(ax.get('Expressivite'))}"
            f"<td class=\"num\">{dc['ab'].get(mod, '—')}</td></tr>"
        )
    return (
        "<div class='tablewrap'><table class='rank'>"
        "<thead><tr><th>#</th><th>modèle</th>"
        "<th>MOS «&nbsp;Naturel&nbsp;»</th><th>Intel.</th><th>Simil.</th>"
        "<th>Express.</th><th>Win-rate A/B</th></tr></thead>"
        f"<tbody>{''.join(tr)}</tbody></table></div>"
    )


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
    h_ec = "#ecoute" if standalone else "ecoute.html"
    lb = sorted(
        ((n, m, m["global"]) for n, m in d["modeles"].items()
         if (m.get("global") or {}).get("wer") is not None
         and m["global"]["wer"] < 0.5),
        key=lambda x: x[2]["wer"],
    )
    n_mod, n_voix = len(lb), d["n_voix"]
    dc = _ecoute_donnees()

    rows = []
    cartes = []
    for i, (nom, m, r) in enumerate(lb):
        anom = r["hallu"] + r["rep"] + r["tronc"]
        comm = m["usage_commercial"]
        lic = (f'<span class="chip ok">{m["licence"]}</span>' if comm == "oui"
               else f'<span class="chip crit">{m["licence"]} · non&nbsp;comm.</span>' if comm == "non"
               else f'<span class="chip warn">{m["licence"]}</span>')
        rows.append({"_nom": _nm(nom), "_rank": i + 1, "wer": r["wer"], "sim": r["sim"]})
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
            f'<a href="{h_obj}"><b>{_nm(nom)}</b></a>{lic}</div>'
            f'<div class="msub mono">{m["revision"] or "—"} · {html.escape(m["role"][:70])}</div>'
            f'<div class="mstat mono">{st}</div></div>'
        )

    cols = [
        {"k": "_nom", "label": "modèle"},
        {"k": "wer", "label": "WER", "dir": -1, "fmt": "pct", "g": .05, "b": .10},
        {"k": "sim", "label": "SIM", "dir": 1, "fmt": "num3", "g": .80, "b": .72},
    ]
    cfg = {"cols": cols, "rows": rows, "sort": {"k": "wer", "asc": True}, "rankcol": True}

    hero = f"""<div class="hero" id="top"><div class="wrap">
  <div class="eyebrow">Benchmark · TTS open-source · Français</div>
  <h1>Quel modèle de synthèse vocale pour le français ?</h1>
  <p class="thesis">Huit modèles open-source clonent {n_voix} voix de référence sur un
    corpus français annoté (liaison, nombres, noms propres, homographes, dialogue
    émotionnel). Métriques auto reproductibles pour l'intelligibilité et l'identité —
    <em>la naturalité, elle, se juge à l'écoute humaine en aveugle</em>.</p>
  <div class="facts">
    <span class="fact"><b>{n_mod}</b> modèles classés</span>
    <span class="fact"><b>34</b> phrases annotées</span>
    <span class="fact"><b>3</b> répétitions</span>
    <span class="fact"><b>{n_voix}</b> voix de référence</span>
    <span class="fact"><b>RTX&nbsp;4090</b></span>
    <span class="fact">révisions HF <b>épinglées</b></span>
  </div>
  <div class="scope">
    <div class="cap">WER moyen (toutes voix confondues) — barre courte = meilleur</div>
    {_scope_svg(d)}
  </div>
</div></div>"""

    excl = ""
    if d["exclus"]:
        excl = ('<div class="board-foot">hors classement — '
                + " · ".join(f'{_nm(e["nom"])} ({e["motif"]})' for e in d["exclus"]) + "</div>")

    # --- section « À l'écoute » : classement par MOS + win-rate ---
    ec_panel = ""
    if dc and dc["panel"]:
        n, a, m, e = dc["panel"]
        ec_panel = (f'<p class="lead"><b>Panel</b> : {n} auditeur·rice·s, en aveugle — '
                    f'{a} comparaisons A/B, {m} notes MOS (1–5), {e} votes émotion. '
                    f'Aucun nom de voix ni de participant n\'est publié.</p>')
    ec_rang = (f'<div class="md">{_ecoute_classement_html(dc)}</div>'
               if dc and dc["mos"] else "")
    ec_note = ('<p class="lead">MOS « Naturel » = moyenne des notes 1–5 sur l\'axe naturel '
               '(± IC 95 %). Win-rate A/B = part de préférences « globalement meilleur » '
               'sur l\'ensemble des duels. Le classement de naturalité du benchmark, '
               'c\'est cette colonne — pas le WER.</p>') if ec_rang else ""
    lien_ec = ("" if standalone else
               '<p class="lead" style="margin-top:14px">'
               '<a class="link" href="ecoute.html">'
               'Détail : matrice des duels, MOS par axe, émotion &rarr;</a></p>')
    ecoute_bloc = (
        '<section id="ecoute">'
        '<div class="sec-h"><h2>À l\'écoute — le classement qui compte</h2>'
        '<span class="n">MOS · A/B · émotion, en aveugle</span></div>'
        f'{ec_panel}{ec_rang}{ec_note}{lien_ec}'
        '</section>') if (dc and dc["mos"]) else (
        '<section id="ecoute">'
        '<div class="sec-h"><h2>À l\'écoute</h2><span class="n">en aveugle</span></div>'
        '<p class="lead">Test d\'écoute prêt — aucun retour agrégé pour l\'instant.</p>'
        '</section>')

    corps = f"""<section id="classement">
  <div class="sec-h"><h2>Métriques auto — intelligibilité &amp; identité</h2>
    <span class="n">toutes voix confondues · passe-1</span></div>
  <p class="lead">Moyenne pondérée (par nb de runs) sur les {n_voix} voix de référence.
    <b>WER</b> = taux d'erreur de transcription
    (<span class="mono">whisper-large-v3-french</span> + <span class="mono">jiwer</span>),
    ↓ meilleur — c'est l'<b>intelligibilité</b>. <b>SIM</b> = similarité au locuteur
    de référence (embeddings ECAPA), ↑ meilleur — c'est l'<b>identité de timbre</b>.
    <b>La naturalité n'est pas mesurée ici</b> (UTMOS, TTSDS2, NISQA tous écartés en
    français) : voir <a class="link" href="{h_ec}">le classement à l'écoute</a>.
    Clic sur un en-tête pour trier, ou&nbsp;:</p>
  {LEGENDE}
  <div class="tools"><label>Trier&nbsp;:
    <select id="msort">
      <option value="wer|a">WER — meilleur d'abord</option>
      <option value="wer|d">WER — pire d'abord</option>
      <option value="sim|d">SIM — meilleur d'abord</option>
      <option value="sim|a">SIM — pire d'abord</option>
    </select></label></div>
  <div class="board"><div id="lb"></div>{excl}</div>
</section>

{ecoute_bloc}

<section id="modeles">
  <div class="sec-h"><h2>Les modèles</h2><span class="n">contexte · vitesse · stabilité</span></div>
  <div class="mgrid">{"".join(cartes)}</div>
  <p class="lead" style="margin-top:16px"><a class="link" href="{h_obj}">Table
    complète (toutes métriques, toutes voix confondues, détail par phrase) &rarr;</a></p>
</section>

<section id="lecture"><div class="callout">
  <p><span class="k">Les métriques auto ne tranchent pas — l'écoute, oui.</span>
  <span class="d">Le WER est brut (une vraie voix humaine dans le même Whisper fait
  déjà 2–4 %). La naturalité n'a aucune métrique auto fiable en français : UTMOS,
  TTSDS2 et NISQA ont été essayés puis écartés (corrélation nulle voire négative
  avec la note humaine). Le classement de naturalité vient du test d'écoute en
  aveugle ci-dessus.</span></p>
</div></section>

<section id="methode">
  <div class="sec-h"><h2>Méthode</h2><span class="n">détail : docs/METHODOLOGIE.md</span></div>
  <div class="cards">
    <div class="card"><span class="tag">Corpus</span><h3>34 phrases annotées</h3>
      <p>Croisement longueur × registre × piège : liaison, nombre, nom propre,
      silence/rythme, homographe hétérophone, emprunt anglais, ponctuation répétée,
      onomatopée. Plus un volet long-form (podcast, journalisme).</p></div>
    <div class="card"><span class="tag">Pré-traitement</span><h3>Identique pour tous</h3>
      <p>Même pipeline de normalisation appliqué à l'entrée de chaque modèle. Les
      nombres ne sont pas développés en amont : on teste la normalisation de texte
      propre à chaque modèle.</p></div>
    <div class="card"><span class="tag">Voix de référence</span><h3>Clonage zero-shot, {n_voix} voix</h3>
      <p>Une voix propre, une « difficile » (source brute), une féminine, deux âgées,
      un accent régional, plus les registres émotionnels. Aucun nom n'est publié ;
      les voix restent identiques d'une passe à l'autre.</p></div>
    <div class="card"><span class="tag">Écoute</span><h3>Test MOS + A/B en aveugle</h3>
      <p>Panel humain, clips anonymisés, plusieurs voix et phrases tirées au hasard
      par session. C'est ce test qui produit le <b>classement de naturalité</b> ;
      WER et SIM ne font que le préparer.</p></div>
    <div class="card"><span class="tag">Reproductibilité</span><h3>models.lock</h3>
      <p>repo_id + révision SHA Hugging&nbsp;Face épinglée + commit GitHub pour le code.
      Re-téléchargement bit-à-bit ; une révision non épinglée est refusée.</p></div>
  </div>
</section>

<section id="repro">
  <div class="sec-h"><h2>Révisions épinglées</h2><span class="n">Hugging Face</span></div>
  <div class="card repro">{"".join(
      f'<div><span>{_nm(n)}</span><span>{m["revision"] or "—"}</span></div>'
      for n, m in sorted(d["modeles"].items()))}</div>
</section>"""

    js = (f"var CFG={json.dumps(cfg, ensure_ascii=False)};"
          "CFG.msort=document.getElementById('msort');"
          "ttsTable('#lb',CFG);")
    return _shell("Benchmark TTS français", "index", corps, hero=hero, js=js,
                  standalone=standalone)


# --------------------------------------------------------------------------
# Page métriques — toutes voix confondues
# --------------------------------------------------------------------------
def page_objectif() -> str:
    d = _collecter()
    # p2 masqué < 620px, p3 masqué < 900px — modèle/WER/SIM toujours visibles
    cols = [
        {"k": "_nom", "label": "modèle"},
        {"k": "wer", "label": "WER", "dir": -1, "fmt": "pct", "g": .05, "b": .10},
        {"k": "sim", "label": "SIM", "dir": 1, "fmt": "num3", "g": .80, "b": .72},
        {"k": "wer_sigma", "label": "±σ", "dir": -1, "fmt": "pct", "g": .08, "b": .15, "p": 2},
        {"k": "rtf", "label": "RTF", "dir": 0, "fmt": "x", "g": .6, "b": 1.5, "p": 2},
        {"k": "cv", "label": "CV durée", "dir": -1, "fmt": "pct", "g": .10, "b": .15, "p": 2},
        {"k": "clonage", "label": "clon.", "fmt": "oui", "p": 3},
        {"k": "wer_net", "label": "WER net", "dir": -1, "fmt": "pct", "g": .04, "b": .09, "p": 3},
        {"k": "hallu", "label": "hallu.", "dir": -1, "fmt": "pct", "g": .001, "b": .05, "p": 3},
        {"k": "rep", "label": "rép.", "dir": -1, "fmt": "pct", "g": .001, "b": .05, "p": 3},
        {"k": "tronc", "label": "tronc.", "dir": -1, "fmt": "pct", "g": .001, "b": .05, "p": 3},
        {"k": "ttfa", "label": "TTFA s", "dir": -1, "fmt": "num2", "g": 2.0, "b": 8.0, "p": 3},
        {"k": "vram_go", "label": "VRAM~", "dir": 0, "fmt": "int", "p": 3},
        {"k": "_lic", "label": "licence", "kind": "lic", "p": 3},
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
            "clonage": r["clonage"], "wer": r["wer"], "wer_sigma": r["wer_sigma"],
            "wer_net": r["wer_net"], "sim": r["sim"],
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
    <i>WER net</i> = WER après retrait d'un plancher ASR estimé.
    <b>Aucune métrique de naturalité</b> : UTMOS, TTSDS2 et NISQA écartés (non
    pertinents en français) → naturalité = <a class="link" href="ecoute.html">test
    d'écoute</a>. Kokoro n'a qu'une voix interne fixe : ses chiffres ne portent
    que sur elle. Clic sur un en-tête pour trier ; clic sur une ligne pour le
    détail par phrase (longueur / registre / piège). Sur petit écran, seules
    WER / SIM restent affichées.</p>
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
    f = RESULTATS / "ecoute.md"
    if f.is_file():
        corps = f"<section class='md'>{md_vers_html(f.read_text(encoding='utf-8'))}</section>"
    else:
        corps = """<section>
  <div class="sec-h"><h2>Test d'écoute</h2><span class="n">en attente de retours</span></div>
  <p class="lead">Aucune agrégation pour l'instant. Fais passer le test
    (<span class="mono">site/ecoute/index.html</span>), dépose les exports dans
    <span class="mono">exports/</span>, puis lance
    <span class="mono">agreger_ecoute.py</span> puis <span class="mono">build_pages.py</span>.</p>
</section>"""
    return _shell("Test d'écoute — Benchmark TTS FR", "ecoute", corps)


def build() -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    (SORTIE / "index.html").write_text(page_index(), encoding="utf-8")
    (SORTIE / "objectif.html").write_text(page_objectif(), encoding="utf-8")
    (SORTIE / "ecoute.html").write_text(page_ecoute(), encoding="utf-8")
    print(f"[build_pages] -> {SORTIE}/ (index.html, objectif.html, ecoute.html)")


if __name__ == "__main__":
    build()
