# Benchmark — cosyvoice3_05b

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | TTSDS2 | NISQA | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aurore2_narration | 99/99 | 5.8% | 8.2% | 77.9 | 3.85 | 0.803 | 0.0% | 0.0% | 6.1% | 0.83 | 7042 Mo | 5.4% |
| johnny | 99/99 | 10.4% | 14.4% | 77.5 | 2.81 | 0.742 | 1.0% | 1.0% | 6.1% | 0.75 | 6378 Mo | 10.8% |
| manou_narration | 99/99 | 8.4% | 11.2% | 81.4 | 3.77 | 0.828 | 1.0% | 0.0% | 9.1% | 0.72 | 7279 Mo | 6.4% |
| papa_colere | 15/15 | 29.1% | 30.4% | — | 2.93 | 0.786 | 13.3% | 0.0% | 13.3% | 1.87 | 5750 Mo | 5.8% |
| papa_joie | 6/6 | 19.4% | 6.5% | — | 3.08 | 0.734 | 0.0% | 0.0% | 0.0% | 0.77 | 5768 Mo | 7.6% |
| papa_narration | 99/99 | 4.9% | 8.9% | 76.3 | 3.24 | 0.823 | 0.0% | 0.0% | 0.0% | 0.82 | 6258 Mo | 6.6% |
| papa_peur | 9/9 | 1.1% | 3.1% | — | 3.26 | 0.792 | 0.0% | 0.0% | 0.0% | 0.82 | 5755 Mo | 6.5% |
| papa_tristesse | 6/6 | 7.1% | 7.1% | — | 3.05 | 0.748 | 0.0% | 0.0% | 16.7% | 0.83 | 5758 Mo | 11.3% |
| papy_narration | 96/96 | 15.7% | 24.9% | 73.7 | 3.51 | 0.834 | 6.2% | 0.0% | 12.5% | 1.26 | 7100 Mo | 7.9% |
| tonton_marc_narration | 99/99 | 16.2% | 22.1% | 74.6 | 2.52 | 0.779 | 3.0% | 0.0% | 3.0% | 0.98 | 6990 Mo | 9.4% |

## aurore2_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.7% |
| long | 12 | 4.9% |
| moyen | 48 | 7.6% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.6% |
| dialogue_colere | 15 | 2.4% |
| dialogue_joie | 6 | 6.7% |
| dialogue_peur | 9 | 2.2% |
| dialogue_tristesse | 6 | 2.1% |
| narration | 48 | 8.8% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 1.0% |
| homographe_heterophone | 21 | 2.9% |
| liaison | 24 | 2.8% |
| nom_propre | 18 | 7.7% |
| nombre | 18 | 7.7% |
| onomatopee | 6 | 19.2% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 6.9% |

**Troncature détectée sur** : p03, p04, p23, p24, p29

**Durée instable (CV > seuil)** : p24, p25

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 10.7% |
| long | 12 | 4.1% |
| moyen | 48 | 11.7% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.9% |
| dialogue_colere | 15 | 9.3% |
| dialogue_joie | 6 | 16.7% |
| dialogue_peur | 9 | 5.1% |
| dialogue_tristesse | 6 | 6.8% |
| narration | 48 | 14.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 2.2% |
| homographe_heterophone | 21 | 10.5% |
| liaison | 24 | 8.2% |
| nom_propre | 18 | 12.4% |
| nombre | 18 | 9.0% |
| onomatopee | 6 | 16.7% |
| ponctuation_repetee | 3 | 5.1% |
| silence_rythme | 21 | 7.8% |

**Hallucination détectée sur** : p25

**Répétition détectée sur** : p22

**Troncature détectée sur** : p16, p17, p18, p19, p24, p25

**Durée instable (CV > seuil)** : p06, p08, p12, p17, p18, p20, p25, p31, p33, p34

## manou_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 10.4% |
| long | 12 | 3.6% |
| moyen | 48 | 7.9% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 4.4% |
| dialogue_colere | 15 | 4.1% |
| dialogue_joie | 6 | 15.0% |
| dialogue_peur | 9 | 5.1% |
| dialogue_tristesse | 6 | 13.7% |
| narration | 48 | 10.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 7.6% |
| liaison | 24 | 4.6% |
| nom_propre | 18 | 10.0% |
| nombre | 18 | 6.6% |
| onomatopee | 6 | 19.2% |
| ponctuation_repetee | 3 | 10.3% |
| silence_rythme | 21 | 8.2% |

**Hallucination détectée sur** : p01

**Troncature détectée sur** : p01, p03, p04, p05, p22, p24, p26

**Durée instable (CV > seuil)** : p16, p33

## papa_colere — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 9 | 42.4% |
| moyen | 6 | 9.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_colere | 15 | 29.1% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| homographe_heterophone | 3 | 30.8% |
| nombre | 3 | 10.4% |
| ponctuation_repetee | 3 | 23.1% |

**Hallucination détectée sur** : p02

**Troncature détectée sur** : p02

**Durée instable (CV > seuil)** : p02, p19

## papa_joie — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 3 | 16.7% |
| moyen | 3 | 22.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_joie | 6 | 19.4% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| liaison | 3 | 22.2% |

## papa_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 2.9% |
| long | 12 | 2.0% |
| moyen | 48 | 7.3% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.5% |
| dialogue_colere | 15 | 2.1% |
| dialogue_joie | 6 | 4.4% |
| dialogue_peur | 9 | 2.2% |
| dialogue_tristesse | 6 | 2.4% |
| narration | 48 | 7.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 1.0% |
| homographe_heterophone | 21 | 2.3% |
| liaison | 24 | 2.3% |
| nom_propre | 18 | 7.5% |
| nombre | 18 | 4.9% |
| onomatopee | 6 | 16.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 6.4% |

**Durée instable (CV > seuil)** : p04

## papa_peur — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 6 | 1.7% |
| moyen | 3 | 0.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_peur | 9 | 1.1% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| silence_rythme | 9 | 1.1% |

## papa_tristesse — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 3 | 0.0% |
| moyen | 3 | 14.3% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_tristesse | 6 | 7.1% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| homographe_heterophone | 6 | 7.1% |

**Troncature détectée sur** : p09

## papy_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 38 | 22.2% |
| long | 10 | 2.9% |
| moyen | 48 | 13.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 3.1% |
| dialogue_colere | 14 | 33.3% |
| dialogue_joie | 6 | 27.2% |
| dialogue_peur | 9 | 2.2% |
| dialogue_tristesse | 6 | 23.2% |
| narration | 46 | 14.6% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 4.4% |
| homographe_heterophone | 21 | 18.1% |
| liaison | 22 | 4.9% |
| nom_propre | 16 | 14.8% |
| nombre | 16 | 8.7% |
| onomatopee | 6 | 16.7% |
| ponctuation_repetee | 2 | 61.5% |
| silence_rythme | 19 | 6.6% |

**Hallucination détectée sur** : p01, p09, p19, p22, p24, p33

**Troncature détectée sur** : p01, p03, p09, p15, p16, p17, p19, p22, p23, p24, p33

**Durée instable (CV > seuil)** : p01, p04, p09, p16, p19, p22, p24, p25, p33

## tonton_marc_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 24.6% |
| long | 12 | 7.0% |
| moyen | 48 | 11.7% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 14.6% |
| dialogue_colere | 15 | 7.0% |
| dialogue_joie | 6 | 36.1% |
| dialogue_peur | 9 | 16.2% |
| dialogue_tristesse | 6 | 2.1% |
| narration | 48 | 18.9% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 6.3% |
| homographe_heterophone | 21 | 8.8% |
| liaison | 24 | 14.5% |
| nom_propre | 18 | 21.8% |
| nombre | 18 | 12.2% |
| onomatopee | 6 | 16.7% |
| ponctuation_repetee | 3 | 17.9% |
| silence_rythme | 21 | 13.8% |

**Hallucination détectée sur** : p01, p05

**Troncature détectée sur** : p01, p05, p26

**Durée instable (CV > seuil)** : p01, p02, p03, p16, p24, p25, p34
