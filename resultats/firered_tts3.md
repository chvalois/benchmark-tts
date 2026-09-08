# Benchmark — firered_tts3

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|
| aurore2_narration | 99/99 | 5.5% | 8.7% | 0.811 | 0.0% | 0.0% | 0.0% | 0.94 | 17913 Mo | 6.2% |
| johnny | 99/99 | 4.3% | 6.9% | 0.779 | 0.0% | 0.0% | 0.0% | 0.94 | 17028 Mo | 5.3% |
| manou_narration | 99/99 | 6.1% | 11.0% | 0.833 | 3.0% | 0.0% | 0.0% | 0.91 | 18125 Mo | 3.3% |
| papa_colere | 15/15 | 5.5% | 7.8% | 0.806 | 0.0% | 0.0% | 0.0% | 0.94 | 16898 Mo | 3.9% |
| papa_joie | 6/6 | 0.0% | 0.0% | 0.828 | 0.0% | 0.0% | 0.0% | 1.00 | 16894 Mo | 3.2% |
| papa_narration | 99/99 | 3.6% | 6.5% | 0.844 | 0.0% | 0.0% | 0.0% | 1.00 | 16944 Mo | 3.5% |
| papa_peur | 9/9 | 0.0% | 0.0% | 0.797 | 0.0% | 0.0% | 0.0% | 0.94 | 16937 Mo | 4.1% |
| papa_tristesse | 6/6 | 0.0% | 0.0% | 0.757 | 0.0% | 0.0% | 0.0% | 0.95 | 16942 Mo | 4.1% |
| papy_narration | 99/99 | 76.6% | 37.8% | 0.705 | 76.8% | 0.0% | 54.5% | 0.97 | 18084 Mo | 27.5% |
| tonton_marc_narration | 99/99 | 5.3% | 7.2% | 0.788 | 0.0% | 0.0% | 0.0% | 0.92 | 18100 Mo | 3.0% |

## aurore2_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 5.9% |
| long | 12 | 9.3% |
| moyen | 48 | 4.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 3.5% |
| dialogue_colere | 15 | 8.1% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 7.6% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 4.6% |
| liaison | 24 | 3.7% |
| nom_propre | 18 | 8.0% |
| nombre | 18 | 8.1% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 5.2% |

**Durée instable (CV > seuil)** : p02

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 5.1% |
| long | 12 | 3.7% |
| moyen | 48 | 3.8% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.6% |
| dialogue_colere | 15 | 5.5% |
| dialogue_joie | 6 | 1.1% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 6.2% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 2.2% |
| homographe_heterophone | 21 | 3.7% |
| liaison | 24 | 0.8% |
| nom_propre | 18 | 5.4% |
| nombre | 18 | 3.7% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.4% |

**Durée instable (CV > seuil)** : p01, p25, p28, p29

## manou_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 5.3% |
| long | 12 | 19.7% |
| moyen | 48 | 3.4% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 8.3% |
| dialogue_colere | 15 | 5.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 2.2% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 7.9% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 3.2% |
| liaison | 24 | 5.7% |
| nom_propre | 18 | 10.6% |
| nombre | 18 | 15.5% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 8.5% |

**Hallucination détectée sur** : p15, p26

## papa_colere — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 9 | 6.7% |
| moyen | 6 | 3.8% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_colere | 15 | 5.5% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| homographe_heterophone | 3 | 0.0% |
| nombre | 3 | 0.0% |
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
| court | 39 | 4.8% |
| long | 12 | 1.8% |
| moyen | 48 | 3.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.1% |
| dialogue_colere | 15 | 5.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 5.3% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 3.2% |
| liaison | 24 | 0.5% |
| nom_propre | 18 | 4.0% |
| nombre | 18 | 1.8% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.4% |

## papa_peur — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 6 | 0.0% |
| moyen | 3 | 0.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_peur | 9 | 0.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| silence_rythme | 9 | 0.0% |

## papa_tristesse — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 3 | 0.0% |
| moyen | 3 | 0.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_tristesse | 6 | 0.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| homographe_heterophone | 6 | 0.0% |

## papy_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 94.4% |
| long | 12 | 52.5% |
| moyen | 48 | 68.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 62.4% |
| dialogue_colere | 15 | 93.4% |
| dialogue_joie | 6 | 63.3% |
| dialogue_peur | 9 | 57.3% |
| dialogue_tristesse | 6 | 117.3% |
| narration | 48 | 75.9% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 61.0% |
| homographe_heterophone | 21 | 89.5% |
| liaison | 24 | 66.9% |
| nom_propre | 18 | 68.1% |
| nombre | 18 | 65.7% |
| onomatopee | 6 | 85.9% |
| ponctuation_repetee | 3 | 97.4% |
| silence_rythme | 21 | 66.0% |

**Hallucination détectée sur** : p01, p02, p03, p04, p05, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p28, p29, p30, p31, p32, p33, p34

**Troncature détectée sur** : p01, p02, p03, p04, p05, p07, p09, p10, p11, p12, p14, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p28, p30, p31, p32, p33, p34

**Durée instable (CV > seuil)** : p01, p03, p04, p05, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p23, p25, p26, p30, p31, p32, p33

## tonton_marc_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 6.4% |
| long | 12 | 5.0% |
| moyen | 48 | 4.4% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 3.3% |
| dialogue_colere | 15 | 9.6% |
| dialogue_joie | 6 | 1.1% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 6.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 5.4% |
| homographe_heterophone | 21 | 5.4% |
| liaison | 24 | 1.8% |
| nom_propre | 18 | 6.2% |
| nombre | 18 | 5.1% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 5.1% |
| silence_rythme | 21 | 3.5% |
