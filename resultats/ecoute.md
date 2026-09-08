# Test d'écoute — agrégation

7 auditeur(s) — 60 votes A/B, 120 notes MOS, 60 votes émotion.

## A/B — win-rate par modèle

| modèle | win-rate | (victoires / duels) | défauts entendus |
|---|---|---|---|
| firered_tts3 | 78% | 19.5 / 25 | accent:2 |
| voxcpm2 | 64% | 14.0 / 22 | tronque:1 |
| cosyvoice3_05b | 44% | 7.5 / 17 | voix_diff:7 accent:4 tronque:2 repetition:1 artefact:1 |
| xtts_v2 | 38% | 7.5 / 20 | voix_diff:11 artefact:5 accent:2 tronque:1 |
| chatterbox_v3 | 36% | 7.5 / 21 | voix_diff:7 accent:4 artefact:2 tronque:1 repetition:1 |
| moss_tts_local_v15 | 27% | 4.0 / 15 | voix_diff:2 artefact:1 |

## A/B — matrice des duels (gauche bat haut)

| | chatterbox_v3 | cosyvoice3_05b | firered_tts3 | moss_tts_local_v15 | voxcpm2 | xtts_v2 |
|---|---|---|---|---|---|---|
| **chatterbox_v3** | · | 0/1 | 0/5 | 2/3 | 0/2 | 2/3 |
| **cosyvoice3_05b** | 1/1 | · | 1/4 | 1/1 | 1/4 | 1/2 |
| **firered_tts3** | 5/5 | 3/4 | · | 3/3 | 3/5 | 4/5 |
| **moss_tts_local_v15** | 1/3 | 0/1 | 0/3 | · | 2/4 | 0/2 |
| **voxcpm2** | 2/2 | 3/4 | 2/5 | 2/4 | · | 3/3 |
| **xtts_v2** | 1/3 | 1/2 | 1/5 | 2/2 | 0/3 | · |

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
| firered_tts3 | 78% | 12.5 / 16 |
| chatterbox_v3 | 54% | 6.5 / 12 |
| voxcpm2 | 53% | 9.0 / 17 |
| xtts_v2 | 50% | 4.0 / 8 |
| cosyvoice3_05b | 42% | 5.0 / 12 |
| moss_tts_local_v15 | 20% | 3.0 / 15 |

### Émotion — win-rate par (modèle, émotion)

| modèle | colere | joie | peur | tristesse |
|---|---|---|---|---|
| chatterbox_v3 | 67% (4.0/6) | 0% (0.0/2) | 25% (0.5/2) | 100% (2.0/2) |
| cosyvoice3_05b | 33% (1.0/3) | 50% (1.0/2) | 0% (0.0/4) | 100% (3.0/3) |
| firered_tts3 | 81% (6.5/8) | 0% (0.0/1) | 100% (3.0/3) | 75% (3.0/4) |
| moss_tts_local_v15 | 11% (1.0/9) | 100% (2.0/2) | 0% (0.0/1) | 0% (0.0/3) |
| voxcpm2 | 50% (3.0/6) | 100% (2.0/2) | 60% (3.0/5) | 25% (1.0/4) |
| xtts_v2 | 75% (1.5/2) | 0% (0.0/1) | 83% (2.5/3) | 0% (0.0/2) |
