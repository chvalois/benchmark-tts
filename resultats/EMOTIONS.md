# Run émotions — voix de référence émotionnelle → phrases du registre

Chaque voix de référence (`papa_joie/colere/peur/tristesse`) ne génère que
les phrases de dialogue de son registre (joie : p01,p06 · colère :
p02,p07,p19,p22,p33 · peur : p03,p08,p34 · tristesse : p04,p09), 3 reps.
Kokoro exclu (pas de clonage). Question testée (APIAVISOL §3.5) : **cloner
une voix de référence émotionnelle transporte-t-il l'émotion ?** — réponse
surtout à l'écoute (voir le mode ÉMOTION du test `site/ecoute/`) ; ici on
vérifie que l'émotion ne casse pas l'intelligibilité (WER) ni l'identité
(SIM), et on regarde la NISQA (TTSDS2, distributionnel, est inexploitable
sur 6–15 clips).

Audio : `D:\tts-benchmark-data\audio_genere\<modèle>\papa_<émotion>\`.

Métriques **automatiques** : WER (whisper-large-v3-french), fidélité
language-agnostic, **NISQA** (naturalité prédite NISQA-TTS, ↑ mieux ~1–5),
**SIM** (similarité au locuteur de réf émotionnel, ECAPA, ↑ mieux). **Pas
encore d'écoute MOS humaine.** WER brut (aucun plancher humain soustrait).


| modèle | voix | clon. | WER | ±σ | NISQA | SIM | hallu. | rép. | tronc. | RTF | CV dur. |
|---|---|---|---|---|---|---|---|---|---|---|---|
| chatterbox_v3 | papa_joie | oui | 0.0% | 0.0% | 3.35 | 0.760 | 0.0% | 0.0% | 0.0% | 0.54 | 8.2% |
| firered_tts3 | papa_joie | oui | 0.0% | 0.0% | 3.30 | 0.828 | 0.0% | 0.0% | 0.0% | 1.00 | 3.2% |
| firered_tts3 | papa_peur | oui | 0.0% | 0.0% | 3.60 | 0.797 | 0.0% | 0.0% | 0.0% | 0.94 | 4.1% |
| firered_tts3 | papa_tristesse | oui | 0.0% | 0.0% | 3.43 | 0.757 | 0.0% | 0.0% | 0.0% | 0.95 | 4.1% |
| moss_tts_local_v15 | papa_tristesse | oui | 0.0% | 0.0% | 3.46 | 0.616 | 0.0% | 0.0% | 0.0% | 0.66 | 15.6% |
| voxcpm2 | papa_joie | oui | 0.0% | 0.0% | 3.39 | 0.779 | 0.0% | 0.0% | 0.0% | 0.40 | 5.5% |
| voxcpm2 | papa_tristesse | oui | 0.0% | 0.0% | 3.48 | 0.764 | 0.0% | 0.0% | 0.0% | 0.41 | 4.8% |
| xtts_v2 | papa_tristesse | oui | 0.0% | 0.0% | 3.33 | 0.665 | 0.0% | 0.0% | 0.0% | 0.28 | 5.2% |
| cosyvoice3_05b | papa_peur | oui | 1.1% | 3.1% | 3.26 | 0.792 | 0.0% | 0.0% | 0.0% | 0.82 | 6.5% |
| moss_tts_local_v15 | papa_joie | oui | 1.1% | 2.5% | 3.43 | 0.764 | 0.0% | 0.0% | 0.0% | 1.09 | 15.1% |
| xtts_v2 | papa_peur | oui | 1.1% | 3.1% | 3.83 | 0.659 | 0.0% | 0.0% | 0.0% | 0.25 | 5.4% |
| voxcpm2 | papa_peur | oui | 1.2% | 3.5% | 3.61 | 0.779 | 0.0% | 0.0% | 0.0% | 0.40 | 9.4% |
| voxcpm2 | papa_colere | oui | 1.5% | 3.1% | 3.53 | 0.739 | 0.0% | 0.0% | 0.0% | 0.41 | 6.3% |
| chatterbox_v3 | papa_colere | oui | 2.0% | 3.3% | 3.40 | 0.778 | 0.0% | 0.0% | 0.0% | 0.58 | 4.1% |
| xtts_v2 | papa_joie | oui | 2.2% | 3.1% | 3.63 | 0.692 | 0.0% | 0.0% | 0.0% | 0.24 | 10.0% |
| moss_tts_local_v15 | papa_colere | oui | 2.8% | 5.2% | 3.52 | 0.708 | 0.0% | 0.0% | 0.0% | 0.70 | 10.2% |
| xtts_v2 | papa_colere | oui | 4.1% | 7.9% | 3.62 | 0.725 | 0.0% | 0.0% | 0.0% | 0.23 | 12.0% |
| chatterbox_v3 | papa_tristesse | oui | 4.8% | 10.6% | 3.62 | 0.753 | 0.0% | 0.0% | 0.0% | 0.56 | 6.0% |
| firered_tts3 | papa_colere | oui | 5.5% | 7.8% | 3.55 | 0.806 | 0.0% | 0.0% | 0.0% | 0.94 | 3.9% |
| cosyvoice3_05b | papa_tristesse | oui | 7.1% | 7.1% | 3.05 | 0.748 | 0.0% | 0.0% | 16.7% | 0.83 | 11.3% |
| moss_tts_local_v15 | papa_peur | oui | 9.0% | 21.7% | 3.64 | 0.641 | 0.0% | 0.0% | 0.0% | 0.68 | 25.4% |
| chatterbox_v3 | papa_peur | oui | 10.0% | 28.3% | 3.91 | 0.721 | 11.1% | 0.0% | 11.1% | 0.55 | 3.1% |
| cosyvoice3_05b | papa_joie | oui | 19.4% | 6.5% | 3.08 | 0.734 | 0.0% | 0.0% | 0.0% | 0.77 | 7.6% |
| cosyvoice3_05b | papa_colere | oui | 29.1% | 30.4% | 2.93 | 0.786 | 13.3% | 0.0% | 13.3% | 1.87 | 5.8% |

*24 lignes — 6 modèles × 4 registres émotionnels.*

- **RTF** = temps de génération / durée audio (< 1 = plus rapide que le temps réel).
- **NISQA** ~1–5 (NISQA-TTS) — biais anglophone connu, en contre-vérification.
- **SIM** = cosinus embeddings **ECAPA-TDNN** gén. vs voix de réf émotionnelle (0–1).
- **CV durée** = écart-type / moyenne de la durée sur les 3 reps (stabilité).
- Détail par catégorie + WER par piège : `resultats/<modele>.md`.
