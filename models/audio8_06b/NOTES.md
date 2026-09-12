# Audio8-TTS-Preview-0.6b (Edge0) — notes d'intégration

- **Pas de code_ref GitHub** : le dépôt GitHub (Edge0-AI/Audio8_TTS,
  ex-Audio8-AI — l'ancien nom `Audio8-AI/Audio8_TTS` redirige en 301)
  ne contient que démo/training. Le code d'inférence custom (DualAR,
  codec) est **embarqué dans le snapshot HF** (`modeling_arktts.py`,
  `configuration_arktts.py`, ...) et chargé via
  `AutoModel`/`AutoProcessor.from_pretrained(<chemin local>,
  trust_remote_code=True)` — la révision épinglée fixe donc aussi le code.
- **API** : `processor(text=[...], reference_audio=[wav], reference_text=[transcript],
  return_tensors="pt")` → `model.generate(**inputs, max_new_tokens=4096,
  temperature=0.8, top_p=0.95, top_k=50, do_sample=True,
  return_dict_in_generate=True)` → `model.decode_audio(output.codes)`
  → waveform **44,1 kHz** (`model.config.codec_sample_rate`), resamplé
  vers 24 kHz par le pipeline commun.
- `max_new_tokens` relevé de 1024 (exemple du model card, pensé pour une
  phrase courte) à 4096 pour couvrir des chunks jusqu'à ~60 mots
  (MAX_WORDS_PER_CHUNK) sans troncature.
- **Langue** : pas de paramètre de langue explicite dans l'API — le modèle
  infère apparemment depuis le texte. FR confirmé dans la carte HF (11
  langues recommandées, dont French) ; pas de balise `<lang:fr>` à ajouter.
- **Pas de seed natif** exposé → variance des reps portée par la graine
  globale torch (`fixer_seed`).
- **`uv run` exige `--no-project`** (même piège pyproject.toml racine que
  pour OmniVoice — voir models/omnivoice/NOTES.md).
- Entrée `models.lock` (`audio8_06b`) posée dès le tout premier commit du
  projet (statut "verifie" théorique, jamais implémentée) → corrigée et
  réellement vérifiée le 2026-09-12.

Smoke-test réel (2026-09-12) : cold start ~72 s, ~5,9 Go VRAM pic,
gen 2,8–17,6 s/phrase courte (1ʳᵉ génération plus lente), sortie 24 kHz
mono PCM16 conforme au contrat après resample.
