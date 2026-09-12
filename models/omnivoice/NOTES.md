# OmniVoice (k2-fsa) — notes d'intégration

- **Paquet** : `omnivoice==0.2.1` (PyPI), torch 2.8 cu128. Pas de code_ref
  GitHub : `OmniVoice.from_pretrained(<chemin local>, ...)` résout un
  répertoire local directement (`os.path.isdir` en premier), donc le
  snapshot HF épinglé suffit — pas de clone séparé du dépôt.
- **API** : `model.generate(text=..., language="French", ref_text=...,
  ref_audio=<chemin wav>)` → `list[np.ndarray]` à **24 kHz** (1 item).
  Clonage = wav + transcription (`corpus/voix_reference/<voix>.prompt.txt`).
- **Langue** : paramètre `language` explicite (pas de balise inline).
  FR confirmé dans `docs/languages.md` du dépôt GitHub (code `fra`,
  23 675 h d'entraînement).
- **audio_tokenizer** (HiggsAudioV2, ~0,8 Go) déjà **bundlé** dans le
  snapshot `k2-fsa/OmniVoice` (sous-dossier `audio_tokenizer/`) → pas de
  second repo HF tiré implicitement (contrairement à MOSS).
- **Pas de seed natif** exposé par `generate()` → variance des reps portée
  uniquement par la graine globale torch (`fixer_seed`, déjà posée par
  `executer_corpus`).
- **`normalize_text=False`** en passe-1 (défaut du modèle). Le FR n'a pas
  de TN dédiée (WeTextProcessing = zh/en uniquement) ; les nombres FR
  passeraient par un repli `num2words` si activé — non testé ici.
- Warning modèle observé : "Reference audio is 24.4s long (>20s)" sur les
  wav de référence de ce projet (recommandation officielle 3–10 s) — pas
  bloquant, mais à garder en tête pour la qualité de clonage.
- **`uv run` exige `--no-project`** : le `pyproject.toml` racine ne déclare
  aucune dépendance ; sans ce flag, `uv run --python <venv>` resynchronise
  l'environnement dessus et désinstalle tout ce qui a été pip-installé
  manuellement (`ModuleNotFoundError: numpy`).

Smoke-test réel (2026-09-12) : cold start ~77 s, ~5,5 Go VRAM pic,
gen ~0,9 s/phrase courte, sortie 24 kHz mono PCM16 conforme au contrat.
