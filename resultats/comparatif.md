# Comparatif TTS open source — français

Métriques **automatiques** : WER (whisper-large-v3-french), fidélité
language-agnostic, **UTMOS** (naturel prédit, ↑ mieux), **SIM**
(similarité au locuteur de réf, ↑ mieux). **Pas encore d'écoute MOS
humaine.** WER brut (aucun plancher humain soustrait).

| modèle | voix | clon. | WER | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF | CV dur. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| firered_tts3 | papa_narration | oui | 3.6% | 6.5% | 3.26 | 0.964 | 0.0% | 0.0% | 0.0% | 1.00 | 3.5% |
| voxcpm2 | papa_narration | oui | 4.2% | 8.0% | 3.13 | 0.967 | 0.0% | 0.0% | 6.1% | 0.42 | 3.3% |
| firered_tts3 | johnny | oui | 4.3% | 6.9% | 2.78 | 0.960 | 0.0% | 0.0% | 0.0% | 0.94 | 5.3% |
| chatterbox_v3 | papa_narration | oui | 4.8% | 7.6% | 3.64 | 0.961 | 0.0% | 0.0% | 2.0% | 0.59 | 3.4% |
| voxcpm2 | johnny | oui | 7.3% | 10.1% | 2.68 | 0.966 | 0.0% | 0.0% | 0.0% | 0.41 | 10.9% |
| kokoro_82m | ff_siwis (voix interne) | non | 7.5% | 18.0% | 3.66 | — | 3.0% | 0.0% | 3.0% | 0.02 | 0.0% |
| moss_tts_local_v15 | johnny | oui | 7.7% | 10.8% | 3.06 | 0.957 | 1.0% | 0.0% | 1.0% | 0.63 | 14.3% |
| moss_tts_local_v15 | papa_narration | oui | 7.9% | 27.8% | 3.50 | 0.968 | 2.0% | 0.0% | 1.0% | 0.69 | 7.7% |
| chatterbox_v3 | johnny | oui | 8.3% | 10.6% | 3.25 | 0.968 | 0.0% | 0.0% | 2.0% | 0.56 | 5.1% |

- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).
- **UTMOS** ~1–5, entraîné sur MOS anglophone → classement relatif seulement.
- **SIM** = cosinus embeddings `wavlm-base-plus-sv` gén. vs voix de réf (0–1).
- **CV durée** = écart-type / moyenne de la durée sur les 3 reps (stabilité).
- Détail par catégorie + WER par piège : `resultats/<modele>.md`.