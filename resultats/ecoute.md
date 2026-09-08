# Test d'écoute — agrégation

4 auditeur(s) — 40 votes A/B, 80 notes MOS, 40 votes émotion.

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

## A/B — win-rate par voix de référence (victoires / duels)

| modèle | ? | aurore2_narration | johnny | papy_narration | tonton_marc_narration |
|---|---|---|---|---|---|
| chatterbox_v3 | 30% (1.5/5) | 0% (0.0/1) | 50% (0.5/1) | 50% (2.0/4) | 0% (0.0/1) |
| cosyvoice3_05b | 20% (1.0/5) | 67% (2.0/3) | — | 75% (1.5/2) | 75% (1.5/2) |
| firered_tts3 | 73% (8.0/11) | 100% (3.0/3) | 100% (2.0/2) | — | 67% (2.0/3) |
| moss_tts_local_v15 | 25% (1.0/4) | 0% (0.0/2) | 0% (0.0/1) | 100% (1.0/1) | 25% (0.5/2) |
| voxcpm2 | 78% (7.0/9) | 100% (1.0/1) | 0% (0.0/1) | — | 67% (2.0/3) |
| xtts_v2 | 25% (1.5/6) | 0% (0.0/2) | 50% (0.5/1) | 17% (0.5/3) | 0% (0.0/1) |

## MOS — moyenne ± IC 95 % par axe

| modèle | Naturel | Intelligibilite | Similarite | Expressivite |
|---|---|---|---|---|
| chatterbox_v3 | 3.17 ±0.53 | 3.33 ±0.50 | 2.33 ±0.70 | 2.92 ±0.51 |
| cosyvoice3_05b | 2.42 ±0.70 | 2.92 ±0.51 | 2.50 ±0.66 | 2.08 ±0.51 |
| firered_tts3 | 4.08 ±0.45 | 4.58 ±0.38 | 4.33 ±0.37 | 3.25 ±0.49 |
| moss_tts_local_v15 | 3.25 ±0.66 | 3.94 ±0.49 | 4.19 ±0.37 | 2.69 ±0.50 |
| voxcpm2 | 3.10 ±0.46 | 3.30 ±0.51 | 3.60 ±0.52 | 2.80 ±0.70 |
| xtts_v2 | 3.22 ±0.66 | 3.56 ±0.62 | 1.83 ±0.51 | 2.67 ±0.45 |

## MOS — note globale moyenne (4 axes) par voix de référence

| modèle | ? | aurore2_narration | johnny | papa_narration | papy_narration | tonton_marc_narration |
|---|---|---|---|---|---|---|
| chatterbox_v3 | 2.83 (n=3) | 3.12 (n=2) | 2.38 (n=2) | 3.50 (n=1) | 2.75 (n=2) | 3.38 (n=2) |
| cosyvoice3_05b | 2.42 (n=3) | 3.25 (n=2) | 2.50 (n=2) | 2.75 (n=2) | 1.50 (n=2) | 2.50 (n=1) |
| firered_tts3 | 4.42 (n=3) | 4.31 (n=4) | — | 4.00 (n=3) | — | 3.12 (n=2) |
| moss_tts_local_v15 | 3.70 (n=5) | 3.25 (n=3) | 3.25 (n=3) | 4.75 (n=1) | 2.25 (n=1) | 3.75 (n=3) |
| voxcpm2 | 3.69 (n=4) | — | 2.62 (n=2) | 3.25 (n=2) | — | 2.75 (n=2) |
| xtts_v2 | 2.75 (n=2) | 3.25 (n=4) | — | 2.36 (n=7) | 3.17 (n=3) | 3.12 (n=2) |

## Corrélation MOS (humain) ↔ métrique automatique (par clip)

| axe humain | métrique auto | Pearson r | n |
|---|---|---|---|
| intelligibilite | 1-WER | 0.02 | 80 |
| similarite | SIM | 0.14 | 80 |

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

## Émotion — protocole archivé (réf. émotionnelle vs neutre)

*Sessions antérieures : « lequel sonne le plus <émotion> », clip cloné depuis la réf émotionnelle vs depuis la réf neutre.*

| modèle | n | choix réf. émo. | égalité | choix réf. neutre | taux de transfert |
|---|---|---|---|---|---|
| moss_tts_local_v15 | 4 | 4 | 0 | 0 | 100% |
| firered_tts3 | 2 | 2 | 0 | 0 | 100% |
| voxcpm2 | 4 | 4 | 0 | 0 | 100% |
| cosyvoice3_05b | 1 | 1 | 0 | 0 | 100% |
| xtts_v2 | 4 | 4 | 0 | 0 | 100% |
| chatterbox_v3 | 5 | 4 | 1 | 0 | 80% |
