# Benchmark — chatterbox_v3

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 8.3% | 10.6% | 3.25 | 0.968 | 0.0% | 0.0% | 2.0% | 0.56 | 6737 Mo | 5.1% |
| papa_colere | 15/15 | 2.0% | 3.3% | 3.70 | 0.956 | 0.0% | 0.0% | 0.0% | 0.58 | 6106 Mo | 4.1% |
| papa_joie | 6/6 | 0.0% | 0.0% | 3.57 | 0.966 | 0.0% | 0.0% | 0.0% | 0.54 | 6097 Mo | 8.2% |
| papa_narration | 99/99 | 4.8% | 7.6% | 3.64 | 0.961 | 0.0% | 0.0% | 2.0% | 0.59 | 6449 Mo | 3.4% |
| papa_peur | 9/9 | 10.0% | 28.3% | 3.46 | 0.965 | 11.1% | 0.0% | 11.1% | 0.55 | 6182 Mo | 3.1% |
| papa_tristesse | 6/6 | 4.8% | 10.6% | 3.37 | 0.931 | 0.0% | 0.0% | 0.0% | 0.56 | 6189 Mo | 6.0% |

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 7.8% |
| long | 12 | 4.3% |
| moyen | 48 | 9.6% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 5.1% |
| dialogue_colere | 15 | 4.4% |
| dialogue_joie | 6 | 11.1% |
| dialogue_peur | 9 | 4.4% |
| dialogue_tristesse | 6 | 6.5% |
| narration | 48 | 11.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 10.6% |
| homographe_heterophone | 21 | 9.1% |
| liaison | 24 | 7.4% |
| nom_propre | 18 | 9.5% |
| nombre | 18 | 7.0% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 5.1% |
| silence_rythme | 21 | 5.1% |

**Troncature détectée sur** : p16, p25

**Durée instable (CV > seuil)** : p30

## papa_colere — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 9 | 0.0% |
| moyen | 6 | 4.9% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_colere | 15 | 2.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| homographe_heterophone | 3 | 0.0% |
| nombre | 3 | 2.1% |
| ponctuation_repetee | 3 | 0.0% |

## papa_joie — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 3 | 0.0% |
| moyen | 3 | 0.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_joie | 6 | 0.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| liaison | 3 | 0.0% |

## papa_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.3% |
| long | 12 | 6.5% |
| moyen | 48 | 5.7% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 3.0% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.6% |
| dialogue_tristesse | 6 | 5.7% |
| narration | 48 | 7.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 5.4% |
| liaison | 24 | 2.8% |
| nom_propre | 18 | 5.4% |
| nombre | 18 | 4.3% |
| onomatopee | 6 | 11.5% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 4.3% |

**Troncature détectée sur** : p13, p32

## papa_peur — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 6 | 15.0% |
| moyen | 3 | 0.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_peur | 9 | 10.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| silence_rythme | 9 | 10.0% |

**Hallucination détectée sur** : p34

**Troncature détectée sur** : p34

## papa_tristesse — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 3 | 0.0% |
| moyen | 3 | 9.5% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_tristesse | 6 | 4.8% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| homographe_heterophone | 6 | 4.8% |
