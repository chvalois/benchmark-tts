# Comparatif TTS open source — français

Métriques **automatiques** : WER (whisper-large-v3-french), fidélité
language-agnostic, **UTMOS** (naturel prédit, ↑ mieux), **SIM**
(similarité au locuteur de réf, ↑ mieux). **Pas encore d'écoute MOS
humaine.** WER brut (aucun plancher humain soustrait).

| modèle | voix | clon. | WER | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF | CV dur. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| voxcpm2 | manou_narration | oui | 3.5% | 6.3% | 2.77 | 0.797 | 0.0% | 0.0% | 0.0% | 0.41 | 4.1% |
| firered_tts3 | papa_narration | oui | 3.6% | 6.5% | 3.26 | 0.844 | 0.0% | 0.0% | 0.0% | 1.00 | 3.5% |
| chatterbox_v3 | manou_narration | oui | 3.9% | 6.9% | 3.22 | 0.801 | 0.0% | 1.0% | 0.0% | 0.50 | 3.7% |
| voxcpm2 | tonton_marc_narration | oui | 4.0% | 7.8% | 2.49 | 0.761 | 0.0% | 0.0% | 2.0% | 0.42 | 6.5% |
| chatterbox_v3 | tonton_marc_narration | oui | 4.1% | 6.4% | 3.15 | 0.746 | 0.0% | 0.0% | 0.0% | 0.51 | 5.9% |
| voxcpm2 | papa_narration | oui | 4.2% | 8.0% | 3.14 | 0.822 | 0.0% | 0.0% | 6.1% | 0.42 | 3.3% |
| firered_tts3 | johnny | oui | 4.3% | 6.9% | 2.79 | 0.779 | 0.0% | 0.0% | 0.0% | 0.94 | 5.3% |
| chatterbox_v3 | papy_narration | oui | 4.7% | 7.1% | 3.78 | 0.794 | 0.0% | 0.0% | 0.0% | 0.52 | 5.2% |
| chatterbox_v3 | papa_narration | oui | 4.8% | 7.6% | 3.65 | 0.800 | 0.0% | 0.0% | 2.0% | 0.59 | 3.4% |
| cosyvoice3_05b | papa_narration | oui | 4.9% | 8.9% | 3.52 | 0.823 | 0.0% | 0.0% | 0.0% | 0.82 | 6.6% |
| xtts_v2 | manou_narration | oui | 4.9% | 8.1% | 3.03 | 0.687 | 0.0% | 0.0% | 4.0% | 0.24 | 10.4% |
| xtts_v2 | papy_narration | oui | 5.1% | 7.4% | 3.27 | 0.661 | 0.0% | 0.0% | 4.0% | 0.23 | 7.7% |
| chatterbox_v3 | aurore2_narration | oui | 5.3% | 9.7% | 3.26 | 0.746 | 0.0% | 1.0% | 1.0% | 0.55 | 5.7% |
| firered_tts3 | tonton_marc_narration | oui | 5.3% | 7.2% | 2.61 | 0.788 | 0.0% | 0.0% | 0.0% | 0.92 | 3.0% |
| firered_tts3 | aurore2_narration | oui | 5.5% | 8.7% | 2.44 | 0.811 | 0.0% | 0.0% | 0.0% | 0.94 | 6.2% |
| voxcpm2 | aurore2_narration | oui | 5.5% | 9.0% | 2.14 | 0.792 | 0.0% | 0.0% | 1.0% | 0.41 | 6.5% |
| cosyvoice3_05b | aurore2_narration | oui | 5.8% | 8.2% | 3.18 | 0.803 | 0.0% | 0.0% | 6.1% | 0.83 | 5.4% |
| xtts_v2 | aurore2_narration | oui | 5.9% | 9.6% | 2.85 | 0.690 | 0.0% | 0.0% | 1.0% | 0.24 | 6.8% |
| firered_tts3 | manou_narration | oui | 6.1% | 11.0% | 2.97 | 0.833 | 3.0% | 0.0% | 0.0% | 0.91 | 3.3% |
| xtts_v2 | tonton_marc_narration | oui | 6.3% | 9.0% | 2.66 | 0.632 | 0.0% | 0.0% | 2.0% | 0.23 | 6.6% |
| moss_tts_local_v15 | manou_narration | oui | 6.4% | 24.1% | 3.30 | 0.753 | 1.0% | 1.0% | 0.0% | 0.65 | 6.7% |
| moss_tts_local_v15 | tonton_marc_narration | oui | 6.8% | 18.2% | 2.70 | 0.717 | 1.0% | 1.0% | 1.0% | 0.64 | 12.4% |
| moss_tts_local_v15 | papy_narration | oui | 6.8% | 13.1% | 3.52 | 0.782 | 0.0% | 0.0% | 1.0% | 0.62 | 11.4% |
| voxcpm2 | johnny | oui | 7.3% | 10.1% | 2.69 | 0.784 | 0.0% | 0.0% | 0.0% | 0.41 | 10.9% |
| xtts_v2 | johnny | oui | 7.3% | 11.0% | 2.72 | 0.697 | 1.0% | 2.0% | 7.1% | 0.24 | 14.4% |
| xtts_v2 | papa_narration | oui | 7.4% | 19.6% | 3.33 | 0.745 | 1.0% | 0.0% | 0.0% | 0.24 | 10.1% |
| kokoro_82m | ff_siwis (voix interne) | non | 7.5% | 18.0% | 3.66 | — | 3.0% | 0.0% | 3.0% | 0.02 | 0.0% |
| moss_tts_local_v15 | johnny | oui | 7.7% | 10.8% | 3.06 | 0.643 | 1.0% | 0.0% | 1.0% | 0.63 | 14.3% |
| moss_tts_local_v15 | papa_narration | oui | 7.9% | 27.8% | 3.50 | 0.772 | 2.0% | 0.0% | 1.0% | 0.69 | 7.7% |
| chatterbox_v3 | johnny | oui | 8.3% | 10.6% | 3.26 | 0.714 | 0.0% | 0.0% | 2.0% | 0.56 | 5.1% |
| cosyvoice3_05b | manou_narration | oui | 8.4% | 11.2% | 3.31 | 0.828 | 1.0% | 0.0% | 9.1% | 0.72 | 6.4% |
| cosyvoice3_05b | johnny | oui | 10.4% | 14.4% | 2.95 | 0.742 | 1.0% | 1.0% | 6.1% | 0.75 | 10.8% |
| cosyvoice3_05b | papy_narration | oui | 15.7% | 24.9% | 3.51 | 0.834 | 6.2% | 0.0% | 12.5% | 1.26 | 7.9% |
| cosyvoice3_05b | tonton_marc_narration | oui | 16.2% | 22.1% | 2.94 | 0.779 | 3.0% | 0.0% | 3.0% | 0.98 | 9.4% |
| moss_tts_local_v15 | aurore2_narration | oui | 20.3% | 103.7% | 2.60 | 0.706 | 2.0% | 0.0% | 1.0% | 0.64 | 13.5% |
| voxcpm2 | papy_narration | oui | 60.1% | 64.3% | 3.34 | 0.816 | 49.5% | 0.0% | 20.2% | 0.51 | 39.7% |
| firered_tts3 | papy_narration | oui | 76.6% | 37.8% | 3.18 | 0.705 | 76.8% | 0.0% | 54.5% | 0.97 | 27.5% |

- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).
- **UTMOS** ~1–5, entraîné sur MOS anglophone. ⚠️ **Métrique retirée** — non calibrée
  FR (les voix humaines de réf y scorent 1,5–2,9, *sous* les TTS). Ce tableau garde
  la colonne jusqu'au re-scoring TTSDS2 + NISQA (cf. `docs/METHODOLOGIE.md` §9-10).
- **SIM** = cosinus embeddings **ECAPA-TDNN** (`speechbrain/spkrec-ecapa-voxceleb`)
  gén. vs voix de réf, silences rognés (0–1). *(`wavlm-base-plus-sv` abandonné :
  cosinus tous ~0,96, aucune discrimination.)*
- **CV durée** = écart-type / moyenne de la durée sur les 3 reps (stabilité).
- Détail par catégorie + WER par piège : `resultats/<modele>.md`.