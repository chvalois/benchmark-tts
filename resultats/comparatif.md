# Comparatif TTS open source — français

Métriques automatiques uniquement (WER via whisper-large-v3-french,
détecteurs de fidélité language-agnostic). **Pas encore d'écoute MOS.**
WER brut (aucun plancher humain soustrait).

| modèle | voix | clonage | WER | ±σ | hallu. | rép. | tronc. | RTF | CV durée | WER narration | WER onomatopée |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chatterbox_v3 | papa_narration | oui | 4.8% | 7.6% | 0.0% | 0.0% | 2.0% | 0.59 | 3.4% | 7.7% | 11.5% |
| kokoro_82m | ff_siwis (voix interne) | non | 7.5% | 18.0% | 3.0% | 0.0% | 3.0% | 0.01 | 0.0% | 12.4% | 61.5% |
| chatterbox_v3 | johnny | oui | 8.3% | 10.6% | 0.0% | 0.0% | 2.0% | 0.56 | 5.1% | 11.0% | 7.7% |

- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).
- **CV durée** = écart-type / moyenne de la durée sur les 3 reps du même texte (stabilité).
- Détail par catégorie : `resultats/<modele>.md`.