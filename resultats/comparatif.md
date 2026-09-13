# Comparatif TTS open source — français

Métriques **automatiques** : WER (whisper-large-v3-french), fidélité
language-agnostic, **SIM** (similarité au locuteur de réf, ↑ mieux).
WER brut (aucun plancher humain soustrait).

**La naturalité ne figure pas ici** : UTMOS, TTSDS2 et NISQA ont tous
été testés et écartés (non pertinents / anti-corrélés avec la note
humaine en français, cf. `docs/METHODOLOGIE.md` §10). Le classement de
naturalité vient du **test d'écoute** (`resultats/ecoute.md`).

| modèle | voix | clon. | WER | ±σ | SIM | hallu. | rép. | tronc. | RTF | CV dur. |
|---|---|---|---|---|---|---|---|---|---|---|
| omnivoice | papa_narration | oui | 1.9% | 4.7% | 0.823 | 0.0% | 0.0% | 0.0% | 0.29 | 0.5% |
| audio8_06b | papa_narration | oui | 2.6% | 5.4% | 0.765 | 0.0% | 0.0% | 0.0% | 1.13 | 2.9% |
| firered_tts3 | papa_narration | oui | 2.9% | 6.3% | 0.844 | 0.0% | 0.0% | 0.0% | 1.00 | 3.5% |
| voxcpm2 | papa_narration | oui | 3.2% | 6.8% | 0.822 | 0.0% | 0.0% | 6.1% | 0.42 | 3.3% |
| omnivoice | johnny | oui | 3.6% | 7.4% | 0.797 | 0.0% | 0.0% | 1.0% | 0.23 | 0.0% |
| firered_tts3 | johnny | oui | 3.6% | 6.6% | 0.779 | 0.0% | 0.0% | 0.0% | 0.94 | 5.3% |
| audio8_06b | johnny | oui | 3.8% | 6.6% | 0.675 | 0.0% | 0.0% | 2.0% | 1.11 | 9.4% |
| cosyvoice3_05b | papa_narration | oui | 3.9% | 7.2% | 0.823 | 0.0% | 0.0% | 0.0% | 0.82 | 6.6% |
| chatterbox_v3 | papa_narration | oui | 4.2% | 7.2% | 0.800 | 0.0% | 0.0% | 2.0% | 0.59 | 3.4% |
| voxcpm2 | johnny | oui | 6.3% | 9.6% | 0.784 | 0.0% | 0.0% | 0.0% | 0.41 | 10.9% |
| xtts_v2 | papa_narration | oui | 6.6% | 19.7% | 0.745 | 1.0% | 0.0% | 0.0% | 0.24 | 10.1% |
| xtts_v2 | johnny | oui | 6.6% | 10.7% | 0.697 | 1.0% | 2.0% | 7.1% | 0.24 | 14.4% |
| kokoro_82m | ff_siwis (voix interne) | non | 6.8% | 18.1% | — | 3.0% | 0.0% | 3.0% | 0.02 | 0.0% |
| moss_tts_local_v15 | johnny | oui | 6.9% | 10.7% | 0.643 | 1.0% | 0.0% | 1.0% | 0.63 | 14.3% |
| moss_tts_local_v15 | papa_narration | oui | 7.0% | 27.7% | 0.772 | 2.0% | 0.0% | 1.0% | 0.69 | 7.7% |
| chatterbox_v3 | johnny | oui | 7.5% | 10.3% | 0.714 | 0.0% | 0.0% | 2.0% | 0.56 | 5.1% |
| cosyvoice3_05b | johnny | oui | 9.2% | 14.4% | 0.742 | 1.0% | 1.0% | 6.1% | 0.75 | 10.8% |
| f5_tts | papa_narration | oui | 104.6% | 60.9% | 0.468 | 99.0% | 3.0% | 98.0% | 0.33 | 0.0% |
| f5_tts | johnny | oui | 123.6% | 144.9% | 0.460 | 100.0% | 4.0% | 99.0% | 0.45 | 0.0% |

- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).
- **SIM** = cosinus embeddings **ECAPA-TDNN** (`speechbrain/spkrec-ecapa-voxceleb`) gén. vs voix de réf, silences rognés (0–1).
- **CV durée** = écart-type / moyenne de la durée sur les 3 reps (stabilité).
- Naturalité : `resultats/ecoute.md` (test d'écoute MOS + A/B).
- Détail par catégorie + WER par piège : `resultats/<modele>.md`.