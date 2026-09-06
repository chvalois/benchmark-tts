# Benchmark — voxcpm2

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | hallucination | répétition | troncature | RTF méd. | VRAM pic | CV durée méd. |
|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 7.3% | 10.1% | 0.0% | 0.0% | 0.0% | 0.41 | 10003 Mo | 10.9% |
| papa_narration | 99/99 | 4.2% | 8.0% | 0.0% | 0.0% | 6.1% | 0.42 | 10000 Mo | 3.3% |

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 8.4% |
| long | 12 | 4.8% |
| moyen | 48 | 7.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.7% |
| dialogue_colere | 15 | 6.7% |
| dialogue_joie | 6 | 7.8% |
| dialogue_peur | 9 | 10.1% |
| dialogue_tristesse | 6 | 1.2% |
| narration | 48 | 9.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 1.1% |
| homographe_heterophone | 21 | 7.0% |
| liaison | 24 | 2.2% |
| nom_propre | 18 | 7.8% |
| nombre | 18 | 7.7% |
| onomatopee | 6 | 9.0% |
| ponctuation_repetee | 3 | 5.1% |
| silence_rythme | 21 | 7.7% |

**Durée instable (CV > seuil)** : p01, p02, p11, p16, p17, p18, p24, p25, p32, p34

## papa_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.0% |
| long | 12 | 0.5% |
| moyen | 48 | 6.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.2% |
| dialogue_colere | 15 | 2.6% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 7.4% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 7.6% |
| homographe_heterophone | 21 | 2.6% |
| liaison | 24 | 1.3% |
| nom_propre | 18 | 9.3% |
| nombre | 18 | 2.6% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.5% |

**Troncature détectée sur** : p12, p28, p29, p33

**Durée instable (CV > seuil)** : p12
