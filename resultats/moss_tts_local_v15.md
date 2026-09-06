# Benchmark — moss_tts_local_v15

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | hallucination | répétition | troncature | RTF méd. | VRAM pic | CV durée méd. |
|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 7.7% | 10.8% | 1.0% | 0.0% | 1.0% | 0.63 | 16118 Mo | 14.3% |
| papa_narration | 99/99 | 7.9% | 27.8% | 2.0% | 0.0% | 1.0% | 0.69 | 16122 Mo | 7.7% |

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 7.1% |
| long | 12 | 4.6% |
| moyen | 48 | 9.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 4.2% |
| dialogue_colere | 15 | 6.3% |
| dialogue_joie | 6 | 8.3% |
| dialogue_peur | 9 | 9.0% |
| dialogue_tristesse | 6 | 2.1% |
| narration | 48 | 9.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 10.8% |
| homographe_heterophone | 21 | 6.7% |
| liaison | 24 | 2.9% |
| nom_propre | 18 | 6.2% |
| nombre | 18 | 5.5% |
| onomatopee | 6 | 19.2% |
| ponctuation_repetee | 3 | 2.6% |
| silence_rythme | 21 | 10.1% |

**Hallucination détectée sur** : p17

**Troncature détectée sur** : p32

**Durée instable (CV > seuil)** : p01, p02, p03, p05, p06, p07, p08, p09, p16, p17, p19, p22, p24, p33, p34

## papa_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 8.2% |
| long | 12 | 1.9% |
| moyen | 48 | 9.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 0.9% |
| dialogue_colere | 15 | 14.6% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 11.5% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 4.4% |
| liaison | 24 | 10.1% |
| nom_propre | 18 | 6.3% |
| nombre | 18 | 3.2% |
| onomatopee | 6 | 10.3% |
| ponctuation_repetee | 3 | 2.6% |
| silence_rythme | 21 | 3.5% |

**Hallucination détectée sur** : p02, p11

**Troncature détectée sur** : p11

**Durée instable (CV > seuil)** : p02, p03, p11, p18, p19, p20, p22, p23, p24, p29
