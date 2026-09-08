# Comparatif TTS open source — français

Métriques **automatiques** : WER (whisper-large-v3-french), fidélité
language-agnostic, **TTSDS2** (naturalité distributionnelle vs vraie
parole FR, ↑ mieux), **NISQA** (naturalité prédite par énoncé, contre-
vérification, ↑ mieux), **SIM** (similarité au locuteur de réf, ↑ mieux).
**Pas encore d'écoute MOS humaine.** WER brut (aucun plancher humain
soustrait).

| modèle | voix | clon. | WER | ±σ | TTSDS2 | NISQA | SIM | hallu. | rép. | tronc. | RTF | CV dur. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| firered_tts3 | papa_narration | oui | 3.6% | 6.5% | 73.1 | 3.55 | 0.844 | 0.0% | 0.0% | 0.0% | 1.00 | 3.5% |
| voxcpm2 | papa_narration | oui | 4.2% | 8.0% | 73.6 | 3.54 | 0.822 | 0.0% | 0.0% | 6.1% | 0.42 | 3.3% |
| firered_tts3 | johnny | oui | 4.3% | 6.9% | 70.9 | 3.13 | 0.779 | 0.0% | 0.0% | 0.0% | 0.94 | 5.3% |
| chatterbox_v3 | papa_narration | oui | 4.8% | 7.6% | 73.7 | 3.72 | 0.800 | 0.0% | 0.0% | 2.0% | 0.59 | 3.4% |
| cosyvoice3_05b | papa_narration | oui | 4.9% | 8.9% | 76.3 | 3.24 | 0.823 | 0.0% | 0.0% | 0.0% | 0.82 | 6.6% |
| voxcpm2 | johnny | oui | 7.3% | 10.1% | 68.4 | 3.08 | 0.784 | 0.0% | 0.0% | 0.0% | 0.41 | 10.9% |
| xtts_v2 | johnny | oui | 7.3% | 11.0% | 75.4 | 3.36 | 0.697 | 1.0% | 2.0% | 7.1% | 0.24 | 14.4% |
| xtts_v2 | papa_narration | oui | 7.4% | 19.6% | 77.3 | 3.79 | 0.745 | 1.0% | 0.0% | 0.0% | 0.24 | 10.1% |
| kokoro_82m | ff_siwis (voix interne) | non | 7.5% | 18.0% | 78.7 | 3.95 | — | 3.0% | 0.0% | 3.0% | 0.02 | 0.0% |
| moss_tts_local_v15 | johnny | oui | 7.7% | 10.8% | 70.6 | 3.35 | 0.643 | 1.0% | 0.0% | 1.0% | 0.63 | 14.3% |
| moss_tts_local_v15 | papa_narration | oui | 7.9% | 27.8% | 70.6 | 3.51 | 0.772 | 2.0% | 0.0% | 1.0% | 0.69 | 7.7% |
| chatterbox_v3 | johnny | oui | 8.3% | 10.6% | 71.2 | 3.28 | 0.714 | 0.0% | 0.0% | 2.0% | 0.56 | 5.1% |
| cosyvoice3_05b | johnny | oui | 10.4% | 14.4% | 77.5 | 2.81 | 0.742 | 1.0% | 1.0% | 6.1% | 0.75 | 10.8% |
| f5_tts | papa_narration | oui | 104.6% | 60.9% | 60.5 | 3.43 | 0.468 | 99.0% | 3.0% | 98.0% | 0.33 | 0.0% |
| f5_tts | johnny | oui | 123.6% | 144.9% | 60.0 | 2.96 | 0.460 | 100.0% | 4.0% | 99.0% | 0.45 | 0.0% |

- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).
- **TTSDS2** = score distributionnel (0–100) vs corpus de vraie parole FR (MLS-French) ; principal pour la naturalité. UTMOS retiré (non calibré FR : les voix humaines de réf y scoraient 1,5–2,9, sous les TTS).
- **NISQA** ~1–5 (NISQA-TTS, naturalness) — biais anglophone connu, tenu en contre-vérification seulement.
- **SIM** = cosinus embeddings **ECAPA-TDNN** (`speechbrain/spkrec-ecapa-voxceleb`) gén. vs voix de réf, silences rognés (0–1).
- **CV durée** = écart-type / moyenne de la durée sur les 3 reps (stabilité).
- Détail par catégorie + WER par piège : `resultats/<modele>.md`.