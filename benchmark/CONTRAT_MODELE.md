# Contrat d'interface : un modèle ↔ le module commun

Ce contrat est ce qui permet à `benchmark/` de rester **totalement
indépendant** du code de chaque modèle. Tout `models/<nom>/generer.py` doit
le respecter à la lettre.

## 1. Isolation

- **Un venv par modèle**, sous `$TTSB_VENVS/<nom>` (créé par `uv venv`).
  Jamais de dépendances partagées entre modèles (conflits `torch` /
  `transformers` / `numpy`).
- **Jamais deux modèles chargés sur le GPU en même temps.** Un run =
  un process = un modèle. L'ASR de scoring tourne dans une passe séparée,
  modèle TTS déchargé.
- Poids téléchargés uniquement via `benchmark/fetch_models.py` (révision
  épinglée dans `models.lock`). Jamais de `from_pretrained` sans `revision`.

## 2. Entrées (lues, jamais réécrites)

| Ressource | Emplacement | Règle |
|---|---|---|
| Textes | `corpus/phrases.yaml` | jamais de texte en dur dans le script du modèle |
| Voix de référence | `corpus/voix_reference/<id>.wav` | même échantillon pour tous les modèles clonants |
| Pré-traitement | `benchmark.pretraitement.pretraiter(texte, est_titre=<type == "titre">)` | appliqué **identiquement** par tous |

### Balises de famille (`<voice:>`, `<lang:>`, `[pause N.Ns]`)

Le pré-traitement commun **n'y touche pas**. À la charge de l'adaptateur :

- Modèle **sans** multi-voix : retirer les `<voice:...>` avant synthèse.
- Item `type: multi_voix` (p27) sur un modèle non multi-voix :
  statut `n/a` dans `timings.csv` — **jamais** `echec`.
- Balise de langue : si le modèle en a besoin, l'adaptateur ajoute
  `<lang:fr>` ; sinon il documente comment la langue est pilotée.

## 3. Génération

- Chaque phrase générée **N fois** (`--reps`, défaut 5).
- **Seed** = `base_seed + repetition`, fixé sur `random`, `numpy`, `torch`
  (+ `torch.cuda`), et **journalisé** par run.
- Chunking : fork par famille de modèle, mais `MAX_WORDS_PER_CHUNK` (≈ 60)
  et règles de fusion **communes** ; seules les règles de pause/silence
  diffèrent. Documenter tout écart dans `models/<nom>/NOTES.md`.
- **Cold start** (1er chargement du modèle) mesuré et reporté séparément ;
  le RTF est mesuré **à chaud**.

## 4. Sorties

### Audio

`$TTSB_AUDIO_OUT/<nom_modele>/<id_phrase>_<repetition>.wav`

- WAV PCM 16 bits, **24 000 Hz, mono**.
- `float32` → `int16` à l'encodage (tensors `bfloat16` convertis en
  `float32` d'abord — APIAVISOL §3.10).
- Forme du tenseur : garantir 1D. `squeeze()` puis, si `ndim > 1`, ne
  garder que la **ligne 0**. **Jamais** `reshape(-1)` (concatène les
  canaux → chunk joué deux fois, bug silencieux).

### `timings.csv`

`$TTSB_AUDIO_OUT/<nom_modele>/timings.csv`, une ligne par (phrase, rep) :

| colonne | type | sens |
|---|---|---|
| `id_phrase` | str | clé de `phrases.yaml` |
| `repetition` | int | 1..N |
| `seed` | int | seed effectif du run |
| `ttfa_s` | float | temps au premier échantillon audio |
| `gen_s` | float | durée totale de génération (hors cold start) |
| `audio_s` | float | durée de l'audio produit |
| `vram_pic_mo` | int | pic VRAM pendant le run (via `nvidia-ml-py`) |
| `categorie_chunk` | str | narration / dialogue / replique_courte / mixte |
| `statut` | str | `ok` \| `n/a` \| `echec:<motif>` |

### `meta.json`

`$TTSB_AUDIO_OUT/<nom_modele>/meta.json` : `repo_id`, `revision`,
`cold_start_s`, `params` (dict des paramètres de génération : passe 1
= défauts recommandés ; passe 2 = `chars_per_second` calibré par voix),
`voix_utilisee`, `date_run`, `commit_benchmark`.

## 5. Ce que l'adaptateur NE fait PAS

- Calculer le WER / les métriques : c'est `benchmark/`.
- Normaliser le volume final : passe commune avant écoute A/B.
- Décider du verdict : `benchmark/rapport.py`.
