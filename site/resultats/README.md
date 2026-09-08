# site/resultats/ — pages HTML de résultats

Pages **statiques et autonomes** (aucune ressource externe, données
injectées) : ouvrables en `file://`, comme `site/ecoute/`. Aucune donnée
vocale perso — que des métriques agrégées.

| page | contenu | source |
|---|---|---|
| `index.html` | classement métriques auto (WER · SIM, **toutes voix confondues**, moyenne pondérée hors combos WER > 30 %) **+ classement à l'écoute** (MOS « Naturel » + win-rate A/B) — l'élément décisif — + méthode | `resultats/*.json` + `resultats/ecoute.md` + `benchmark/licences.yaml` |
| `objectif.html` | métriques **automatiques** par modèle (WER · SIM · anomalies · vitesse · stabilité), **toutes voix confondues**, table triable + détail par modèle (WER par longueur / registre / piège, phrases signalées) | `resultats/*.json` + `benchmark/licences.yaml` |
| `ecoute.html` | agrégation du test d'écoute humain (win-rate A/B, matrice des duels, MOS par axe, émotion) | `resultats/ecoute.md` |

Aucun nom de voix de référence ni de participant n'apparaît nulle part.

## Régénérer

```bash
source env.sh
python3 benchmark/build_pages.py
```

À relancer après `rapport.py` (métriques) ou `agreger_ecoute.py` (écoute).
Tant qu'aucun auditeur n'a renvoyé d'export, `ecoute.html` est une page
d'attente.

Ouvrir : double-clic sur `index.html`, ou
`explorer.exe "C:\Users\massi\Dev\benchmark-tts\site\resultats\index.html"`.
