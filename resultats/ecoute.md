# Test d'écoute — agrégation

6 auditeur(s) — 40 votes A/B, 120 notes MOS, 40 votes émotion.

## A/B — win-rate par modèle

| modèle | win-rate | (victoires / duels) | défauts entendus |
|---|---|---|---|
| firered_tts3 | 79% | 15.0 / 19 | accent:2 |
| voxcpm2 | 71% | 10.0 / 14 | — |
| cosyvoice3_05b | 50% | 6.0 / 12 | voix_diff:6 accent:2 tronque:1 repetition:1 artefact:1 |
| chatterbox_v3 | 33% | 4.0 / 12 | voix_diff:5 accent:2 artefact:2 repetition:1 |
| moss_tts_local_v15 | 25% | 2.5 / 10 | voix_diff:1 artefact:1 |
| xtts_v2 | 19% | 2.5 / 13 | voix_diff:7 artefact:4 accent:1 |

## A/B — matrice des duels (gauche bat haut)

| | chatterbox_v3 | cosyvoice3_05b | firered_tts3 | moss_tts_local_v15 | voxcpm2 | xtts_v2 |
|---|---|---|---|---|---|---|
| **chatterbox_v3** | · | 0/1 | 0/3 | 1/2 | 0/1 | 1/1 |
| **cosyvoice3_05b** | 1/1 | · | 1/3 | 1/1 | 0/2 | 1/1 |
| **firered_tts3** | 3/3 | 2/3 | · | 3/3 | 2/3 | 4/5 |
| **moss_tts_local_v15** | 1/2 | 0/1 | 0/3 | · | 1/3 | — |
| **voxcpm2** | 1/1 | 2/2 | 1/3 | 2/3 | · | 3/3 |
| **xtts_v2** | 0/1 | 0/1 | 1/5 | — | 0/3 | · |

## MOS — moyenne ± IC 95 % par axe

| modèle | Naturel | Intelligibilite | Similarite | Expressivite |
|---|---|---|---|---|
| chatterbox_v3 | 3.05 ±0.39 | 3.45 ±0.33 | 2.20 ±0.50 | 2.95 ±0.30 |
| cosyvoice3_05b | 2.50 ±0.50 | 2.75 ±0.47 | 2.80 ±0.46 | 2.40 ±0.41 |
| firered_tts3 | 4.06 ±0.36 | 4.53 ±0.30 | 4.41 ±0.29 | 3.24 ±0.36 |
| moss_tts_local_v15 | 2.91 ±0.56 | 3.70 ±0.40 | 3.87 ±0.36 | 2.70 ±0.36 |
| voxcpm2 | 3.20 ±0.44 | 3.40 ±0.42 | 3.47 ±0.50 | 2.87 ±0.57 |
| xtts_v2 | 2.88 ±0.56 | 3.32 ±0.54 | 1.88 ±0.40 | 2.60 ±0.36 |

## Corrélation MOS (humain) ↔ métrique automatique (par clip)

| axe humain | métrique auto | Pearson r | n |
|---|---|---|---|
| intelligibilite | 1-WER | 0.17 | 120 |
| similarite | SIM | 0.16 | 120 |

## Émotion — quel modèle rend le mieux l'émotion ?

A/B en aveugle : deux modèles disent la même phrase, tous deux clonés depuis la **même** voix de réf émotionnelle. Win-rate = victoires + ½ nuls.

| modèle | win-rate | (victoires / duels) |
|---|---|---|
| firered_tts3 | 88% | 7.0 / 8 |
| xtts_v2 | 62% | 2.5 / 4 |
| chatterbox_v3 | 50% | 3.0 / 6 |
| voxcpm2 | 44% | 4.0 / 9 |
| cosyvoice3_05b | 42% | 2.5 / 6 |
| moss_tts_local_v15 | 14% | 1.0 / 7 |

### Émotion — win-rate par (modèle, émotion)

| modèle | colere | joie | peur | tristesse |
|---|---|---|---|---|
| chatterbox_v3 | 67% (2.0/3) | 0% (0.0/1) | 0% (0.0/1) | 100% (1.0/1) |
| cosyvoice3_05b | 25% (0.5/2) | 0% (0.0/1) | 0% (0.0/1) | 100% (2.0/2) |
| firered_tts3 | 80% (4.0/5) | — | 100% (1.0/1) | 100% (2.0/2) |
| moss_tts_local_v15 | 0% (0.0/4) | 100% (1.0/1) | — | 0% (0.0/2) |
| voxcpm2 | 50% (2.0/4) | 100% (1.0/1) | 50% (1.0/2) | 0% (0.0/2) |
| xtts_v2 | 75% (1.5/2) | — | 100% (1.0/1) | 0% (0.0/1) |
