# benchmark-tts — la référence FR des modèles TTS open source

Benchmark **reproductible** de modèles TTS open source, avec un focus
**français** absent des comparatifs existants (anglophones ou génériques),
et un axe **licence commerciale** en plus de qualité / vitesse / coût.

Mesuré sur matériel réel (**RTX 4090**, 24 Go), un modèle à la fois.

> Documents de cadrage :
> - [`BENCHMARK_TTS_OPENSOURCE_FR_APIAVISOL.md`](BENCHMARK_TTS_OPENSOURCE_FR_APIAVISOL.md) — retour d'expérience, méthodologie détaillée, pièges
> - [`BENCHMARK_TTS_OPENSOURCE_FR_REFLEXIONCLAUDE.md`](BENCHMARK_TTS_OPENSOURCE_FR_REFLEXIONCLAUDE.md) — architecture, corpus structuré, WER FR

## État : Phases 0–1 (socle)

| Phase | Contenu | Statut |
|---|---|---|
| 0 | Socle infra (env, `doctor.py`, stockage D:) | ✅ |
| 1 | Contrats partagés (corpus, voix, pré-traitement, `models.lock`, contrat modèle) | ✅ |
| 2 | Module commun de scoring (WER FR, fidélité, vitesse, licence, stabilité) | ✅ pur & testé (97 % cov.) — reste : runner ASR + helper VRAM (avec Phase 3) |
| 3 | Adaptateurs modèles (venv-par-modèle) | ✅ 5 modèles : chatterbox_v3, kokoro_82m, firered_tts3, voxcpm2, moss_tts_local_v15 |
| 4 | Protocole subjectif (MOS, A/B aveugle, panel) | à venir |
| 5 | Agrégation & rapport | ✅ `rapport.py` + `comparatif.py` → `resultats/` (par modèle + `comparatif.md` + `RESUME.md`) |
| 6 | Présence publique (leaderboard, navigateur audio, data brute) | à venir |
| 7 | Cadence & contenu (re-run par sortie de modèle, outil de conseil) | à venir |

**Périmètre v1** : corpus de phrases annotées + WER FR + licence + vitesse.
**v2** : volet narratif long-form / clonage zero-shot (méthodo APIAVISOL).

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
│   ├── CONTRAT_MODELE.md     # interface modèle ↔ module commun
│   └── tests/
├── models/<nom>/             # un venv + un generer.py par modèle (Phase 3)
├── audio_genere/             # (généré sur D:, hors git)
└── resultats/                # rapports CSV / MD / JSON (Phase 5)
```
