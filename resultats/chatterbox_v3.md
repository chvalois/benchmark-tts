# Benchmark — chatterbox_v3

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | hallucination | répétition | troncature | RTF méd. | VRAM pic | CV durée méd. |
|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 8.3% | 10.6% | 0.0% | 0.0% | 2.0% | 0.56 | 6737 Mo | 5.1% |
| papa_narration | 99/99 | 4.8% | 7.6% | 0.0% | 0.0% | 2.0% | 0.59 | 6449 Mo | 3.4% |

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
