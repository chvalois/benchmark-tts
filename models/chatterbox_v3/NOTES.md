# Chatterbox Multilingual — notes d'intégration

- **Repo** : `ResembleAI/chatterbox` @ `5bb1f6ee…` — MIT, multilingue 23 langues.
- **Checkpoint réellement chargé** : `chatterbox-tts==0.1.7` →
  `from_pretrained(device)` charge **`t3_mtl23ls_v2` + `s3gen.pt`** (pas le v3).
  `t3_mtl23ls_v3.safetensors` / `s3gen_v3` sont dans le repo mais `from_local`
  de la lib code en dur les noms `_v2` → le « V3 » de la veille n'est pas
  câblé par cette version de la lib. À revisiter si Resemble publie une lib
  gérant v3 (clé `chatterbox_v3` conservée comme identifiant).
- **API 0.1.7** : `ChatterboxMultilingualTTS.from_pretrained(device)` puis
  `.generate(text, language_id="fr", audio_prompt_path=ref, exaggeration,
  cfg_weight=0.5, temperature=0.8, repetition_penalty=2.0, min_p=0.05,
  top_p=1.0)` → tensor `(1, N)`. `model.sr` = 24000.
  `repetition_penalty` **défaut 2.0 ≥ 1.0** (cf. piège §3.6 — OK).
- **Dépendance piège** : `resemble-perth` importe `pkg_resources` (retiré de
  setuptools ≥ 81) → `setuptools<80` épinglé dans requirements, sinon
  `PerthImplicitWatermarker = None` et le chargement crashe.
- **exaggeration dynamique** : 0.3 narration / 0.9 dialogue / 0.5 réplique
  courte ; détection de dialogue sur `—` / `-` / `«` (chunker commun).
- **Borne dure** : `FAMILLE_CHATTERBOX.max_cars = 160`.
- **Clonage** : voix de référence unique par run → `multi_voix` (p27) = `n/a`.

## Observations du 1er smoke (2026-09-05, 3 phrases × 2 reps, papa_normal)

- 6/6 runs `ok`, WAV 24 kHz mono, `timings.csv` + `meta.json` conformes.
- **cold start 52 s** ; VRAM pic ~5.9 Go ; `gen_s` ~1,5–1,8 s / phrase courte
  APRÈS le 1er run (p01_1 = 15,7 s : compilation kernels CUDA au 1er appel
  → **ajouter un warm-up non chronométré** avant la boucle).
- ⚠️ `alignment_stream_analyzer` de Chatterbox a **forcé l'EOS** sur 5/6
  générations (« Detected 2x repetition of token 6405 »). À écouter : soit
  répétition réelle, soit arrêt prématuré sur phrases courtes. C'est
  précisément ce que le scoring fidélité doit trancher.

## Checklist des 16 pièges (APIAVISOL §5) — à remplir au 1er run réel

| # | Piège | Résultat | Note |
|---|---|---|---|
| 1 | Texte long en un seul appel (contrôle de durée) | ⬜ | via p26, chunker désactivé en test A/B |
| 2 | Référence courte ~6 s (`vf_court`) | ⬜ | perte d'identité ? |
| 3 | Référence chuchotée pure (`vf_chuchote`) | ⬜ | identité clonable ? |
| 4 | `repetition_penalty < 1.0` | ⬜ | param non exposé par l'API mtl → s/o probable |
| 5 | Resserrage paramètres texte / continuation | ⬜ | s/o (pas de `text_*` chez Chatterbox) |
| 6 | Température audio élevée, 2 runs même seed | ⬜ | via `cfg_weight` / exaggeration hauts |
| 7 | Répliques 1–3 mots (p01, p02, p22) | ⬜ | sur-génération ? diction ? |
| 8 | Ponctuation répétée / onomatopées (p21, p22, p23) | ⬜ | coupure au milieu de réplique ? |
| 9 | Titre sans ponctuation finale (p24, p25) | ⬜ | `pretraiter(est_titre=True)` ajoute le `.` |
| 10 | `<lang:fr>` explicite vs absent | ⬜ | `language_id` global ici, pas de balise |
| 11 | Clonage cross-lingue FR→EN | ⬜ | hors périmètre FR, test de non-régression seulement |
| 12 | Champ style / instruction | ⬜ | `exaggeration` = seul levier |
| 13 | Micro-phrase isolée dans son bloc de voix | ⬜ | s/o (voix unique) |
| 14 | Nombres / heures / dates (p10, p15, p20, p30) | ⬜ | verbalisation FR ? |
| 15 | Forme du tenseur de sortie | ✅ | `preparer_audio` garantit 1D (garde ligne 0) |
| 16 | `bfloat16` en sortie | ✅ | `.float().cpu().numpy()` dans `_synthetiser` |

## Écarts vs défauts recommandés

_(à documenter : passe 1 = défauts, passe 2 = `chars_per_second` calibré par voix)_
