# benchmark-tts — la référence FR des modèles TTS open source

Benchmark **reproductible** de modèles TTS open source, avec un focus
**français** absent des comparatifs existants (anglophones ou génériques),
et un axe **licence commerciale** en plus de qualité / vitesse / coût.

Mesuré sur matériel réel (**RTX 4090**, 24 Go), un modèle à la fois.

> Documents de cadrage :
> - [`BENCHMARK_TTS_OPENSOURCE_FR_APIAVISOL.md`](BENCHMARK_TTS_OPENSOURCE_FR_APIAVISOL.md) — retour d'expérience, méthodologie détaillée, pièges
> - [`BENCHMARK_TTS_OPENSOURCE_FR_REFLEXIONCLAUDE.md`](BENCHMARK_TTS_OPENSOURCE_FR_REFLEXIONCLAUDE.md) — architecture, corpus structuré, WER FR

## État : v1 — 7 modèles scorés + test d'écoute

| Phase | Contenu | Statut |
|---|---|---|
| 0 | Socle infra (env, `doctor.py`, stockage D:) | ✅ |
| 1 | Contrats partagés (corpus, voix, pré-traitement, `models.lock`, contrat modèle) | ✅ |
| 2 | Module commun de scoring (WER FR, fidélité, vitesse, licence, stabilité) | ✅ pur & testé (97 % cov.) |
| 3 | Adaptateurs modèles (venv-par-modèle) | ✅ 8 : chatterbox_v3, kokoro_82m, firered_tts3, voxcpm2, moss_tts_local_v15, cosyvoice3_05b, xtts_v2 (+ f5_tts = FR non supporté) · 🚧 +2 en intégration (smoke-testés, pas encore scorés corpus complet) : omnivoice, audio8_06b |
| 4 | Protocole subjectif (MOS, A/B aveugle) | ✅ `build_ecoute.py` → `site/ecoute/` ; agrégation `agreger_ecoute.py` → `resultats/ecoute.md` |
| 5 | Agrégation & rapport | ✅ `rapport.py` + `comparatif.py` → `resultats/` (par modèle + `comparatif.md` + `RESUME.md` + `EMOTIONS.md`) |
| 6 | Présence publique (site de résultats) | 🚧 `build_pages.py` → `site/resultats/` (classement, métriques, écoute + 1 fiche par modèle) ; déploiement Coolify |
| 7 | Cadence & contenu (re-run par sortie de modèle, outil de conseil) | à venir |

**Périmètre v1** : corpus de phrases annotées + WER FR + licence + vitesse + écoute humaine.
**v2** : volet narratif long-form / clonage zero-shot (méthodo APIAVISOL) — cf. `corpus/longform.yaml`.

Classement complet : [`resultats/RESUME.md`](resultats/RESUME.md) · comparatif : [`resultats/comparatif.md`](resultats/comparatif.md).

## Démarrage

```bash
cp env.sh.example env.sh          # redirige tout l'état lourd vers D:
source env.sh
python3 scripts/doctor.py         # GPU, CUDA, stockage, espace disque

# tests du module commun
uv run --with pytest --with pytest-cov python -m pytest \
  --cov=benchmark.pretraitement --cov-report=term-missing

# plan de téléchargement des poids (rien téléchargé)
python3 benchmark/fetch_models.py --check --set lean
```

## Site de résultats

`benchmark/build_pages.py` génère un site **statique autonome** dans
`site/resultats/` à partir des `.md` / `.json` de `resultats/` (stdlib + PyYAML,
**aucune donnée vocale perso** — que des métriques agrégées) :

- `index.html` — classement triable + verdict + méthode
- `objectif.html` — table complète des métriques auto, par voix
- `ecoute.html` — les 3 protocoles du test d'écoute humain (`resultats/ecoute.json`)
- `modele-<nom>.html` — une fiche par modèle : particularité, choix techniques
  vulgarisés, mesures et **sources vérifiées** (registre `benchmark/fiches_modeles.yaml`)

```bash
source env.sh
python3 benchmark/build_pages.py   # -> site/resultats/{index,objectif,ecoute}.html
```

**Déploiement (VPS managé + Coolify)** : le `Dockerfile` à la racine régénère les
pages puis les sert via `nginx`. Coolify → *Public Repository* → build pack
Dockerfile, port `80`, HTTPS automatique ; chaque push sur `main` redéploie.

> `site/ecoute/` (audio du test A/B) contient des **clones de voix perso** —
> `.gitignore`é, jamais publié.

## Contraintes matérielles (résumé)

- **VRAM** : aucun modèle candidat ne dépasse 24 Go en inférence batch 1
  (le plus lourd, MOSS-TTS 8B bf16 ≈ 17–20 Go, tient seul). Règle unique :
  un seul modèle chargé à la fois.
- **Disque** : **ne tient pas sur C:** (45 Go libres). Tout va sur **D:**
  via `env.sh` → `~55–70 Go` pour le set « lean » (8 modèles + ASR),
  `~150 Go` pour le set complet (avec MOSS 5B, Voxtral, réf. qualité).
  `models.lock` épingle chaque révision →
  tout est re-téléchargeable à l'identique.

## Structure

```
benchmark-tts/
├── env.sh.example            # redirection stockage -> D: (copier en env.sh)
├── models.lock               # repo_id + révision épinglée + licence + VRAM/disque
├── scripts/doctor.py         # vérif environnement (stdlib seule)
├── corpus/
│   ├── phrases.yaml          # 34 items annotés (longueur × registre × piège × type)
│   └── voix_reference/       # spéc de la banque de voix (fichiers hors périmètre P1)
├── benchmark/                # module commun, agnostique du modèle
│   ├── pretraitement.py      # 6 étapes §3.9 + ponctuation titre §3.1
│   ├── fetch_models.py       # téléchargement révision-épinglée vers D:
│   ├── rapport.py / comparatif.py   # agrégation -> resultats/
│   ├── build_ecoute.py      # génère site/ecoute/ (test A/B aveugle)
│   ├── build_pages.py       # génère site/resultats/ (site statique public)
│   ├── CONTRAT_MODELE.md     # interface modèle ↔ module commun
│   └── tests/
├── models/<nom>/             # un venv + un generer.py par modèle (Phase 3)
├── audio_genere/             # (généré sur D:, hors git)
├── resultats/                # rapports CSV / MD / JSON (Phases 4–5)
├── site/
│   ├── resultats/            # site statique publié via Coolify
│   └── ecoute/               # test A/B — audio hors git
└── Dockerfile                # image nginx du site de résultats
```
