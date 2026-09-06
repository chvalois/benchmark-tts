# Run émotions — voix de référence émotionnelle → phrases du registre

Chaque voix de référence (`papa_joie/colere/peur/tristesse`) ne génère que
les phrases de dialogue de son registre (joie : p01,p06 · colère :
p02,p07,p19,p22,p33 · peur : p03,p08,p34 · tristesse : p04,p09), 3 reps.
Kokoro exclu (pas de clonage). Question testée (APIAVISOL §3.5) : **cloner
une voix de référence émotionnelle transporte-t-il l'émotion ?** — réponse
surtout à l'écoute ; ici on vérifie que l'émotion ne casse pas
l'intelligibilité (WER) ni l'identité (SIM), et on regarde l'UTMOS.

Audio : `D:\tts-benchmark-data\audio_genere\<modèle>\papa_<émotion>\`.



Métriques **automatiques** : WER (whisper-large-v3-french), fidélité
language-agnostic, **UTMOS** (naturel prédit, ↑ mieux), **SIM**
(similarité au locuteur de réf, ↑ mieux). **Pas encore d'écoute MOS
humaine.** WER brut (aucun plancher humain soustrait).

| modèle | voix | clon. | WER | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF | CV dur. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chatterbox_v3 | papa_joie | oui | 0.0% | 0.0% | 3.57 | 0.966 | 0.0% | 0.0% | 0.0% | 0.54 | 8.2% |
| firered_tts3 | papa_joie | oui | 0.0% | 0.0% | 3.26 | 0.974 | 0.0% | 0.0% | 0.0% | 1.00 | 3.2% |
| firered_tts3 | papa_peur | oui | 0.0% | 0.0% | 3.00 | 0.975 | 0.0% | 0.0% | 0.0% | 0.94 | 4.1% |
| firered_tts3 | papa_tristesse | oui | 0.0% | 0.0% | 2.93 | 0.919 | 0.0% | 0.0% | 0.0% | 0.95 | 4.1% |
| voxcpm2 | papa_joie | oui | 0.0% | 0.0% | 3.16 | 0.965 | 0.0% | 0.0% | 0.0% | 0.40 | 5.5% |
| voxcpm2 | papa_tristesse | oui | 0.0% | 0.0% | 2.80 | 0.908 | 0.0% | 0.0% | 0.0% | 0.41 | 4.8% |
| moss_tts_local_v15 | papa_tristesse | oui | 0.0% | 0.0% | 3.03 | 0.924 | 0.0% | 0.0% | 0.0% | 0.66 | 15.6% |
| moss_tts_local_v15 | papa_joie | oui | 1.1% | 2.5% | 3.41 | 0.959 | 0.0% | 0.0% | 0.0% | 1.09 | 15.1% |
| voxcpm2 | papa_peur | oui | 1.2% | 3.5% | 2.83 | 0.969 | 0.0% | 0.0% | 0.0% | 0.40 | 9.4% |
| voxcpm2 | papa_colere | oui | 1.5% | 3.1% | 3.09 | 0.949 | 0.0% | 0.0% | 0.0% | 0.41 | 6.3% |
| chatterbox_v3 | papa_colere | oui | 2.0% | 3.3% | 3.70 | 0.956 | 0.0% | 0.0% | 0.0% | 0.58 | 4.1% |
| moss_tts_local_v15 | papa_colere | oui | 2.8% | 5.2% | 3.53 | 0.956 | 0.0% | 0.0% | 0.0% | 0.70 | 10.2% |
| chatterbox_v3 | papa_tristesse | oui | 4.8% | 10.6% | 3.37 | 0.931 | 0.0% | 0.0% | 0.0% | 0.56 | 6.0% |
| firered_tts3 | papa_colere | oui | 5.5% | 7.8% | 3.16 | 0.960 | 0.0% | 0.0% | 0.0% | 0.94 | 3.9% |
| moss_tts_local_v15 | papa_peur | oui | 9.0% | 21.7% | 3.29 | 0.966 | 0.0% | 0.0% | 0.0% | 0.68 | 25.4% |
| chatterbox_v3 | papa_peur | oui | 10.0% | 28.3% | 3.46 | 0.965 | 11.1% | 0.0% | 11.1% | 0.55 | 3.1% |

- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).
- **UTMOS** ~1–5, entraîné sur MOS anglophone → classement relatif seulement.
- **SIM** = cosinus embeddings `wavlm-base-plus-sv` gén. vs voix de réf (0–1).
- **CV durée** = écart-type / moyenne de la durée sur les 3 reps (stabilité).
- Détail par catégorie + WER par piège : `resultats/<modele>.md`.