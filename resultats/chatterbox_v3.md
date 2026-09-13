# Benchmark — chatterbox_v3

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|
| aurore2_narration | 99/99 | 4.6% | 9.6% | 0.746 | 0.0% | 1.0% | 1.0% | 0.55 | 7545 Mo | 5.7% |
| johnny | 99/99 | 7.5% | 10.3% | 0.714 | 0.0% | 0.0% | 2.0% | 0.56 | 6737 Mo | 5.1% |
| manou_narration | 99/99 | 3.0% | 6.1% | 0.801 | 0.0% | 1.0% | 0.0% | 0.50 | 7545 Mo | 3.7% |
| papa_colere | 15/15 | 2.0% | 3.3% | 0.778 | 0.0% | 0.0% | 0.0% | 0.58 | 6106 Mo | 4.1% |
| papa_joie | 6/6 | 0.0% | 0.0% | 0.760 | 0.0% | 0.0% | 0.0% | 0.54 | 6097 Mo | 8.2% |
| papa_narration | 99/99 | 4.2% | 7.2% | 0.800 | 0.0% | 0.0% | 2.0% | 0.59 | 6449 Mo | 3.4% |
| papa_peur | 9/9 | 10.0% | 28.3% | 0.721 | 11.1% | 0.0% | 11.1% | 0.55 | 6182 Mo | 3.1% |
| papa_tristesse | 6/6 | 4.8% | 10.6% | 0.753 | 0.0% | 0.0% | 0.0% | 0.56 | 6189 Mo | 6.0% |
| papy_narration | 99/99 | 4.0% | 6.4% | 0.794 | 0.0% | 0.0% | 0.0% | 0.52 | 7678 Mo | 5.2% |
| tonton_marc_narration | 99/99 | 3.3% | 6.1% | 0.746 | 0.0% | 0.0% | 0.0% | 0.51 | 7676 Mo | 5.9% |

## aurore2_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 5.8% |
| long | 12 | 6.2% |
| moyen | 48 | 3.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.8% |
| dialogue_colere | 15 | 3.3% |
| dialogue_joie | 6 | 4.4% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 1.2% |
| narration | 48 | 6.8% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 6.4% |
| liaison | 24 | 1.8% |
| nom_propre | 18 | 2.4% |
| nombre | 18 | 3.8% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 2.6% |
| silence_rythme | 21 | 3.0% |

**Répétition détectée sur** : p22

**Troncature détectée sur** : p24

**Durée instable (CV > seuil)** : p02

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 7.8% |
| long | 12 | 4.0% |
| moyen | 48 | 8.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 5.1% |
| dialogue_colere | 15 | 4.4% |
| dialogue_joie | 6 | 11.1% |
| dialogue_peur | 9 | 4.4% |
| dialogue_tristesse | 6 | 6.5% |
| narration | 48 | 9.4% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 10.6% |
| homographe_heterophone | 21 | 9.1% |
| liaison | 24 | 6.9% |
| nom_propre | 18 | 5.4% |
| nombre | 18 | 6.3% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 5.1% |
| silence_rythme | 21 | 5.0% |

**Troncature détectée sur** : p16, p25

**Durée instable (CV > seuil)** : p30

## manou_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 2.7% |
| long | 12 | 4.1% |
| moyen | 48 | 3.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.8% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 5.2% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 3.1% |
| liaison | 24 | 0.1% |
| nom_propre | 18 | 2.5% |
| nombre | 18 | 2.2% |
| onomatopee | 6 | 11.5% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 3.4% |

**Répétition détectée sur** : p23

**Durée instable (CV > seuil)** : p23

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
| long | 12 | 6.1% |
| moyen | 48 | 4.4% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 3.0% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.6% |
| dialogue_tristesse | 6 | 5.7% |
| narration | 48 | 6.3% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 5.4% |
| liaison | 24 | 2.3% |
| nom_propre | 18 | 1.6% |
| nombre | 18 | 3.6% |
| onomatopee | 6 | 11.5% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 4.1% |

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

## papy_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 4.6% |
| long | 12 | 5.1% |
| moyen | 48 | 3.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.0% |
| dialogue_colere | 15 | 2.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 6.8% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 1.1% |
| homographe_heterophone | 21 | 6.3% |
| liaison | 24 | 1.8% |
| nom_propre | 18 | 3.2% |
| nombre | 18 | 4.3% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 2.6% |
| silence_rythme | 21 | 2.4% |

## tonton_marc_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.4% |
| long | 12 | 6.2% |
| moyen | 48 | 2.6% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 4.0% |
| dialogue_colere | 15 | 2.6% |
| dialogue_joie | 6 | 1.1% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 4.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 1.0% |
| homographe_heterophone | 21 | 3.9% |
| liaison | 24 | 0.9% |
| nom_propre | 18 | 2.1% |
| nombre | 18 | 4.8% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.6% |

**Durée instable (CV > seuil)** : p02
