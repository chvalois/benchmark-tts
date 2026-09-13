# Test d'écoute — agrégation

9 auditeur(s) — 100 votes A/B, 160 notes MOS, 100 votes émotion.

## A/B — win-rate par modèle

| modèle | win-rate | (victoires / duels) | défauts entendus |
|---|---|---|---|
| firered_tts3 | 77% | 34.0 / 44 | repetition:2 accent:2 |
| omnivoice | 68% | 15.0 / 22 | tronque:1 voix_diff:1 |
| voxcpm2 | 53% | 18.5 / 35 | tronque:1 voix_diff:1 accent:1 artefact:1 |
| cosyvoice3_05b | 47% | 8.5 / 18 | voix_diff:8 accent:4 tronque:2 repetition:1 artefact:1 |
| xtts_v2 | 40% | 8.5 / 21 | voix_diff:11 artefact:5 accent:2 tronque:1 |
| chatterbox_v3 | 36% | 9.0 / 25 | voix_diff:9 accent:6 artefact:2 tronque:1 repetition:1 |
| moss_tts_local_v15 | 21% | 4.0 / 19 | voix_diff:2 artefact:1 |
| audio8_06b | 16% | 2.5 / 16 | accent:2 voix_diff:1 artefact:1 |

## A/B — matrice des duels (gauche bat haut)

| | audio8_06b | chatterbox_v3 | cosyvoice3_05b | firered_tts3 | moss_tts_local_v15 | omnivoice | voxcpm2 | xtts_v2 |
|---|---|---|---|---|---|---|---|---|
| **audio8_06b** | · | 0/1 | 0/1 | 0/2 | 1/1 | 1/9 | 0/1 | — |
| **chatterbox_v3** | 1/1 | · | 0/1 | 0/7 | 2/3 | — | 0/2 | 2/3 |
| **cosyvoice3_05b** | 1/1 | 1/1 | · | 1/4 | 1/1 | — | 1/4 | 1/2 |
| **firered_tts3** | 2/2 | 7/7 | 3/4 | · | 4/4 | 3/5 | 8/11 | 4/5 |
| **moss_tts_local_v15** | 0/1 | 1/3 | 0/1 | 0/4 | · | — | 2/6 | 0/2 |
| **omnivoice** | 8/9 | — | — | 2/5 | — | · | 3/3 | 0/1 |
| **voxcpm2** | 1/1 | 2/2 | 3/4 | 3/11 | 4/6 | 0/3 | · | 3/3 |
| **xtts_v2** | — | 1/3 | 1/2 | 1/5 | 2/2 | 1/1 | 0/3 | · |

## MOS — moyenne ± IC 95 % par axe

| modèle | Naturel | Intelligibilite | Similarite | Expressivite |
|---|---|---|---|---|
| audio8_06b | 2.50 ±0.66 | 3.58 ±0.70 | 3.50 ±0.57 | 2.67 ±0.44 |
| chatterbox_v3 | 3.05 ±0.38 | 3.41 ±0.33 | 2.23 ±0.50 | 2.95 ±0.30 |
| cosyvoice3_05b | 2.50 ±0.50 | 2.75 ±0.47 | 2.80 ±0.46 | 2.40 ±0.41 |
| firered_tts3 | 4.11 ±0.35 | 4.56 ±0.28 | 4.44 ±0.28 | 3.28 ±0.35 |
| moss_tts_local_v15 | 2.88 ±0.50 | 3.77 ±0.37 | 3.85 ±0.36 | 2.77 ±0.33 |
| omnivoice | 2.84 ±0.50 | 3.89 ±0.45 | 3.95 ±0.32 | 3.32 ±0.34 |
| voxcpm2 | 3.20 ±0.44 | 3.40 ±0.42 | 3.47 ±0.50 | 2.87 ±0.57 |
| xtts_v2 | 2.86 ±0.50 | 3.36 ±0.49 | 1.93 ±0.39 | 2.64 ±0.32 |

## Corrélation MOS (humain) ↔ métrique automatique (par clip)

| axe humain | métrique auto | Pearson r | n |
|---|---|---|---|
| intelligibilite | 1-WER | 0.21 | 160 |
| similarite | SIM | 0.23 | 160 |

## Émotion — quel modèle rend le mieux l'émotion ?

A/B en aveugle : deux modèles disent la même phrase, tous deux clonés depuis la **même** voix de réf émotionnelle. Win-rate = victoires + ½ nuls.

| modèle | win-rate | (victoires / duels) |
|---|---|---|
| firered_tts3 | 77% | 21.5 / 28 |
| omnivoice | 72% | 18.0 / 25 |
| voxcpm2 | 52% | 10.5 / 20 |
| xtts_v2 | 50% | 8.0 / 16 |
| chatterbox_v3 | 42% | 7.5 / 18 |
| cosyvoice3_05b | 33% | 5.0 / 15 |
| moss_tts_local_v15 | 25% | 4.5 / 18 |
| audio8_06b | 25% | 5.0 / 20 |

### Émotion — win-rate par (modèle, émotion)

| modèle | colere | joie | peur | tristesse |
|---|---|---|---|---|
| audio8_06b | 17% (1.5/9) | 40% (2.0/5) | 38% (1.5/4) | 0% (0.0/2) |
| chatterbox_v3 | 50% (4.0/8) | 20% (1.0/5) | 17% (0.5/3) | 100% (2.0/2) |
| cosyvoice3_05b | 33% (1.0/3) | 50% (1.0/2) | 0% (0.0/5) | 60% (3.0/5) |
| firered_tts3 | 88% (10.5/12) | 25% (1.0/4) | 100% (6.0/6) | 67% (4.0/6) |
| moss_tts_local_v15 | 21% (2.5/12) | 100% (2.0/2) | 0% (0.0/1) | 0% (0.0/3) |
| omnivoice | 80% (8.0/10) | 80% (4.0/5) | 50% (2.5/5) | 70% (3.5/5) |
| voxcpm2 | 50% (4.5/9) | 100% (2.0/2) | 60% (3.0/5) | 25% (1.0/4) |
| xtts_v2 | 43% (3.0/7) | 0% (0.0/1) | 83% (2.5/3) | 50% (2.5/5) |
