# Test d'écoute — agrégation

8 auditeur(s) — 80 votes A/B, 140 notes MOS, 80 votes émotion.

## A/B — win-rate par modèle

| modèle | win-rate | (victoires / duels) | défauts entendus |
|---|---|---|---|
| omnivoice | 86% | 9.5 / 11 | tronque:1 |
| firered_tts3 | 78% | 25.0 / 32 | accent:2 repetition:1 |
| voxcpm2 | 52% | 15.5 / 30 | tronque:1 |
| cosyvoice3_05b | 47% | 8.5 / 18 | voix_diff:8 accent:4 tronque:2 repetition:1 artefact:1 |
| chatterbox_v3 | 39% | 9.0 / 23 | voix_diff:7 accent:4 artefact:2 tronque:1 repetition:1 |
| xtts_v2 | 38% | 7.5 / 20 | voix_diff:11 artefact:5 accent:2 tronque:1 |
| moss_tts_local_v15 | 22% | 4.0 / 18 | voix_diff:2 artefact:1 |
| audio8_06b | 12% | 1.0 / 8 | voix_diff:1 artefact:1 |

## A/B — matrice des duels (gauche bat haut)

| | audio8_06b | chatterbox_v3 | cosyvoice3_05b | firered_tts3 | moss_tts_local_v15 | omnivoice | voxcpm2 | xtts_v2 |
|---|---|---|---|---|---|---|---|---|
| **audio8_06b** | · | 0/1 | 0/1 | — | 1/1 | 0/5 | — | — |
| **chatterbox_v3** | 1/1 | · | 0/1 | 0/5 | 2/3 | — | 0/2 | 2/3 |
| **cosyvoice3_05b** | 1/1 | 1/1 | · | 1/4 | 1/1 | — | 1/4 | 1/2 |
| **firered_tts3** | — | 5/5 | 3/4 | · | 4/4 | 1/2 | 6/8 | 4/5 |
| **moss_tts_local_v15** | 0/1 | 1/3 | 0/1 | 0/4 | · | — | 2/5 | 0/2 |
| **omnivoice** | 5/5 | — | — | 1/2 | — | · | 3/3 | — |
| **voxcpm2** | — | 2/2 | 3/4 | 2/8 | 3/5 | 0/3 | · | 3/3 |
| **xtts_v2** | — | 1/3 | 1/2 | 1/5 | 2/2 | — | 0/3 | · |

## MOS — moyenne ± IC 95 % par axe

| modèle | Naturel | Intelligibilite | Similarite | Expressivite |
|---|---|---|---|---|
| audio8_06b | 2.60 ±1.18 | 4.20 ±0.39 | 3.40 ±1.18 | 2.60 ±0.48 |
| chatterbox_v3 | 3.10 ±0.38 | 3.48 ±0.32 | 2.29 ±0.51 | 3.00 ±0.30 |
| cosyvoice3_05b | 2.50 ±0.50 | 2.75 ±0.47 | 2.80 ±0.46 | 2.40 ±0.41 |
| firered_tts3 | 4.06 ±0.36 | 4.53 ±0.30 | 4.41 ±0.29 | 3.24 ±0.36 |
| moss_tts_local_v15 | 2.92 ±0.52 | 3.76 ±0.38 | 3.84 ±0.37 | 2.76 ±0.34 |
| omnivoice | 2.50 ±0.73 | 3.80 ±0.49 | 3.80 ±0.39 | 3.20 ±0.39 |
| voxcpm2 | 3.20 ±0.44 | 3.40 ±0.42 | 3.47 ±0.50 | 2.87 ±0.57 |
| xtts_v2 | 2.89 ±0.52 | 3.37 ±0.50 | 1.93 ±0.40 | 2.63 ±0.33 |

## Corrélation MOS (humain) ↔ métrique automatique (par clip)

| axe humain | métrique auto | Pearson r | n |
|---|---|---|---|
| intelligibilite | 1-WER | 0.19 | 140 |
| similarite | SIM | 0.20 | 140 |

## Émotion — quel modèle rend le mieux l'émotion ?

A/B en aveugle : deux modèles disent la même phrase, tous deux clonés depuis la **même** voix de réf émotionnelle. Win-rate = victoires + ½ nuls.

| modèle | win-rate | (victoires / duels) |
|---|---|---|
| omnivoice | 86% | 9.5 / 11 |
| firered_tts3 | 77% | 17.0 / 22 |
| voxcpm2 | 53% | 9.5 / 18 |
| xtts_v2 | 50% | 6.0 / 12 |
| chatterbox_v3 | 47% | 7.5 / 16 |
| cosyvoice3_05b | 36% | 5.0 / 14 |
| moss_tts_local_v15 | 22% | 3.5 / 16 |
| audio8_06b | 18% | 2.0 / 11 |

### Émotion — win-rate par (modèle, émotion)

| modèle | colere | joie | peur | tristesse |
|---|---|---|---|---|
| audio8_06b | 20% (1.0/5) | 0% (0.0/2) | 33% (1.0/3) | 0% (0.0/1) |
| chatterbox_v3 | 57% (4.0/7) | 25% (1.0/4) | 17% (0.5/3) | 100% (2.0/2) |
| cosyvoice3_05b | 33% (1.0/3) | 50% (1.0/2) | 0% (0.0/5) | 75% (3.0/4) |
| firered_tts3 | 85% (8.5/10) | 33% (1.0/3) | 100% (4.0/4) | 70% (3.5/5) |
| moss_tts_local_v15 | 15% (1.5/10) | 100% (2.0/2) | 0% (0.0/1) | 0% (0.0/3) |
| omnivoice | 88% (3.5/4) | 100% (2.0/2) | 100% (2.0/2) | 67% (2.0/3) |
| voxcpm2 | 50% (3.5/7) | 100% (2.0/2) | 60% (3.0/5) | 25% (1.0/4) |
| xtts_v2 | 50% (2.0/4) | 0% (0.0/1) | 83% (2.5/3) | 38% (1.5/4) |
