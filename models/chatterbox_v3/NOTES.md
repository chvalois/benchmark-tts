# Chatterbox V3 Multilingual — notes d'intégration

- **Repo** : `ResembleAI/chatterbox` @ `5bb1f6ee…` — MIT, multilingue 23 langues.
  Le repo porte v2 **et** v3 des poids ; on force `t3_model="v3"`.
- **API** : `ChatterboxMultilingualTTS.from_pretrained(device, t3_model="v3")`,
  puis `.generate(texte, language_id="fr", audio_prompt_path=ref,
  exaggeration=<float>, cfg_weight=1.0)` → tensor `(1, N)`. `model.sr` = SR natif.
- **exaggeration dynamique** (repris d'avisol) : 0.3 narration / 0.9 dialogue /
  0.5 réplique courte. Détection de dialogue sur `—` / `-` / `«` (chunker commun).
- **Borne dure** : `FAMILLE_CHATTERBOX.max_cars = 160` (avisol : 200 cars →
  crash CUDA du flow model, > 6561 tokens).
- **Clonage** : voix de référence unique par run → item `multi_voix` (p27)
  marqué `n/a` (jamais `echec`).

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
