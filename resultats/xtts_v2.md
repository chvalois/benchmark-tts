# Benchmark — xtts_v2

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | TTSDS2 | NISQA | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aurore2_narration | 99/99 | 5.9% | 9.6% | 78.8 | 3.86 | 0.690 | 0.0% | 0.0% | 1.0% | 0.24 | 5596 Mo | 6.8% |
| johnny | 99/99 | 7.3% | 11.0% | 75.4 | 3.36 | 0.697 | 1.0% | 2.0% | 7.1% | 0.24 | 5509 Mo | 14.4% |
| manou_narration | 99/99 | 4.9% | 8.1% | 80.2 | 3.93 | 0.687 | 0.0% | 0.0% | 4.0% | 0.24 | 5667 Mo | 10.4% |
| papa_colere | 15/15 | 4.1% | 7.9% | — | 3.62 | 0.725 | 0.0% | 0.0% | 0.0% | 0.23 | 3952 Mo | 12.0% |
| papa_joie | 6/6 | 2.2% | 3.1% | — | 3.63 | 0.692 | 0.0% | 0.0% | 0.0% | 0.24 | 3844 Mo | 10.0% |
| papa_narration | 99/99 | 7.4% | 19.6% | 77.3 | 3.79 | 0.745 | 1.0% | 0.0% | 0.0% | 0.24 | 4904 Mo | 10.1% |
| papa_peur | 9/9 | 1.1% | 3.1% | — | 3.83 | 0.659 | 0.0% | 0.0% | 0.0% | 0.25 | 4095 Mo | 5.4% |
| papa_tristesse | 6/6 | 0.0% | 0.0% | — | 3.33 | 0.665 | 0.0% | 0.0% | 0.0% | 0.28 | 4095 Mo | 5.2% |
| papy_narration | 99/99 | 5.1% | 7.4% | 74.1 | 3.33 | 0.661 | 0.0% | 0.0% | 4.0% | 0.23 | 5609 Mo | 7.7% |
| tonton_marc_narration | 99/99 | 6.3% | 9.0% | 76.7 | 2.82 | 0.632 | 0.0% | 0.0% | 2.0% | 0.23 | 5859 Mo | 6.6% |

## aurore2_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 4.6% |
| long | 12 | 3.7% |
| moyen | 48 | 7.4% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.2% |
| dialogue_colere | 15 | 7.4% |
| dialogue_joie | 6 | 3.3% |
| dialogue_peur | 9 | 4.4% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 7.9% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 1.6% |
| liaison | 24 | 2.4% |
| nom_propre | 18 | 6.8% |
| nombre | 18 | 7.3% |
| onomatopee | 6 | 12.8% |
| ponctuation_repetee | 3 | 2.6% |
| silence_rythme | 21 | 6.1% |

**Troncature détectée sur** : p31

**Durée instable (CV > seuil)** : p02, p16, p20, p21, p28

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 6.0% |
| long | 12 | 5.5% |
| moyen | 48 | 8.8% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.7% |
| dialogue_colere | 15 | 5.5% |
| dialogue_joie | 6 | 7.2% |
| dialogue_peur | 9 | 3.3% |
| dialogue_tristesse | 6 | 2.1% |
| narration | 48 | 11.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 5.4% |
| homographe_heterophone | 21 | 4.0% |
| liaison | 24 | 5.9% |
| nom_propre | 18 | 10.3% |
| nombre | 18 | 7.3% |
| onomatopee | 6 | 12.8% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 7.0% |

**Hallucination détectée sur** : p25

**Répétition détectée sur** : p32, p34

**Troncature détectée sur** : p13, p15, p25, p26, p31

**Durée instable (CV > seuil)** : p01, p02, p04, p05, p06, p11, p16, p17, p20, p22, p23, p28, p31, p32, p34

## manou_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 4.6% |
| long | 12 | 4.0% |
| moyen | 48 | 5.4% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 5.1% |
| dialogue_colere | 15 | 5.0% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 1.1% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 6.8% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 4.2% |
| homographe_heterophone | 21 | 4.2% |
| liaison | 24 | 1.2% |
| nom_propre | 18 | 7.5% |
| nombre | 18 | 3.9% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 3.1% |

**Troncature détectée sur** : p15, p29, p31

**Durée instable (CV > seuil)** : p02, p04, p13, p20, p23, p29

## papa_colere — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 9 | 0.9% |
| moyen | 6 | 9.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_colere | 15 | 4.1% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| homographe_heterophone | 3 | 0.0% |
| nombre | 3 | 0.0% |
| ponctuation_repetee | 3 | 2.6% |

**Durée instable (CV > seuil)** : p02

## papa_joie — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 3 | 0.0% |
| moyen | 3 | 4.4% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_joie | 6 | 2.2% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| liaison | 3 | 4.4% |

## papa_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 10.8% |
| long | 12 | 1.5% |
| moyen | 48 | 6.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 0.7% |
| dialogue_colere | 15 | 6.4% |
| dialogue_joie | 6 | 2.2% |
| dialogue_peur | 9 | 27.8% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 7.6% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.6% |
| liaison | 24 | 1.9% |
| nom_propre | 18 | 6.6% |
| nombre | 18 | 5.0% |
| onomatopee | 6 | 14.1% |
| ponctuation_repetee | 3 | 5.1% |
| silence_rythme | 21 | 16.3% |

**Hallucination détectée sur** : p34

**Durée instable (CV > seuil)** : p02, p03, p06, p16, p17, p24, p29, p32, p33, p34

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
| court | 39 | 4.0% |
| long | 12 | 3.4% |
| moyen | 48 | 6.3% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.6% |
| dialogue_colere | 15 | 5.4% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 1.1% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 7.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 2.1% |
| homographe_heterophone | 21 | 3.2% |
| liaison | 24 | 2.6% |
| nom_propre | 18 | 7.6% |
| nombre | 18 | 7.9% |
| onomatopee | 6 | 10.3% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 4.2% |

**Troncature détectée sur** : p15, p24, p29, p30

**Durée instable (CV > seuil)** : p03, p12, p17, p34

## tonton_marc_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.7% |
| long | 12 | 4.0% |
| moyen | 48 | 9.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 3.5% |
| dialogue_colere | 15 | 6.8% |
| dialogue_joie | 6 | 3.3% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 7.1% |
| narration | 48 | 8.5% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 2.1% |
| homographe_heterophone | 21 | 4.2% |
| liaison | 24 | 4.7% |
| nom_propre | 18 | 7.7% |
| nombre | 18 | 5.8% |
| onomatopee | 6 | 15.4% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 5.0% |

**Troncature détectée sur** : p31, p32

**Durée instable (CV > seuil)** : p01, p09, p13, p33
