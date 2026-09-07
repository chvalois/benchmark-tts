# Test d'écoute — agrégation

3 auditeur(s) : charles, charles_2, pyrame  — 40 votes A/B, 60 notes MOS, 40 votes émotion.

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
| chatterbox_v3 | 3.20 ±0.57 | 3.30 ±0.59 | 2.00 ±0.58 | 2.90 ±0.54 |
| cosyvoice3_05b | 2.89 ±0.69 | 3.22 ±0.44 | 2.89 ±0.69 | 2.22 ±0.54 |
| firered_tts3 | 4.12 ±0.58 | 4.75 ±0.32 | 4.38 ±0.36 | 3.38 ±0.73 |
| moss_tts_local_v15 | 3.75 ±0.60 | 4.00 ±0.59 | 4.25 ±0.43 | 2.83 ±0.63 |
| voxcpm2 | 3.43 ±0.40 | 3.57 ±0.40 | 3.43 ±0.58 | 2.86 ±1.00 |
| xtts_v2 | 3.36 ±0.79 | 3.64 ±0.67 | 1.86 ±0.54 | 2.71 ±0.52 |

## MOS — note globale moyenne (4 axes) par voix de référence

| modèle | ? | aurore2_narration | johnny | papa_narration | papy_narration | tonton_marc_narration |
|---|---|---|---|---|---|---|
| chatterbox_v3 | 2.83 (n=3) | 3.12 (n=2) | 2.25 (n=1) | 3.50 (n=1) | 2.75 (n=2) | 2.50 (n=1) |
| cosyvoice3_05b | 2.42 (n=3) | 3.25 (n=2) | 3.50 (n=1) | 2.75 (n=2) | — | 2.50 (n=1) |
| firered_tts3 | 4.42 (n=3) | 4.25 (n=2) | — | 4.12 (n=2) | — | 3.25 (n=1) |
| moss_tts_local_v15 | 3.70 (n=5) | 3.25 (n=2) | 3.50 (n=1) | 4.75 (n=1) | — | 3.75 (n=3) |
| voxcpm2 | 3.69 (n=4) | — | — | 3.00 (n=1) | — | 2.75 (n=2) |
| xtts_v2 | 2.75 (n=2) | 3.25 (n=3) | — | 2.50 (n=5) | 3.25 (n=2) | 3.12 (n=2) |

## Corrélation MOS (humain) ↔ métrique automatique (par clip)

| axe humain | métrique auto | Pearson r | n |
|---|---|---|---|
| naturel | UTMOS | -0.12 | 60 |
| intelligibilite | 1-WER | 0.12 | 60 |
| similarite | SIM | 0.22 | 60 |

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
