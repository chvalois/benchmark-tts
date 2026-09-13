# Benchmark — voxcpm2

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|
| aurore2_narration | 99/99 | 3.9% | 7.5% | 0.792 | 0.0% | 0.0% | 1.0% | 0.41 | 10633 Mo | 6.5% |
| johnny | 99/99 | 6.3% | 9.6% | 0.784 | 0.0% | 0.0% | 0.0% | 0.41 | 10003 Mo | 10.9% |
| manou_narration | 99/99 | 2.5% | 5.3% | 0.797 | 0.0% | 0.0% | 0.0% | 0.41 | 11068 Mo | 4.1% |
| papa_colere | 15/15 | 1.5% | 3.1% | 0.739 | 0.0% | 0.0% | 0.0% | 0.41 | 9471 Mo | 6.3% |
| papa_joie | 6/6 | 0.0% | 0.0% | 0.779 | 0.0% | 0.0% | 0.0% | 0.40 | 9466 Mo | 5.5% |
| papa_narration | 99/99 | 3.2% | 6.8% | 0.822 | 0.0% | 0.0% | 6.1% | 0.42 | 10000 Mo | 3.3% |
| papa_peur | 9/9 | 1.2% | 3.5% | 0.779 | 0.0% | 0.0% | 0.0% | 0.40 | 10485 Mo | 9.4% |
| papa_tristesse | 6/6 | 0.0% | 0.0% | 0.764 | 0.0% | 0.0% | 0.0% | 0.41 | 10476 Mo | 4.8% |
| papy_narration | 99/99 | 59.7% | 64.6% | 0.816 | 48.5% | 0.0% | 20.2% | 0.51 | 12052 Mo | 39.7% |
| tonton_marc_narration | 99/99 | 3.0% | 7.0% | 0.761 | 0.0% | 0.0% | 2.0% | 0.42 | 12060 Mo | 6.5% |

## aurore2_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.8% |
| long | 12 | 4.9% |
| moyen | 48 | 3.7% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 3.7% |
| dialogue_colere | 15 | 3.8% |
| dialogue_joie | 6 | 1.1% |
| dialogue_peur | 9 | 1.1% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 5.3% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.8% |
| liaison | 24 | 3.1% |
| nom_propre | 18 | 4.3% |
| nombre | 18 | 6.2% |
| onomatopee | 6 | 9.0% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 3.9% |

**Troncature détectée sur** : p25

**Durée instable (CV > seuil)** : p02, p06, p09

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 8.4% |
| long | 12 | 4.5% |
| moyen | 48 | 5.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.7% |
| dialogue_colere | 15 | 6.7% |
| dialogue_joie | 6 | 7.8% |
| dialogue_peur | 9 | 10.1% |
| dialogue_tristesse | 6 | 1.2% |
| narration | 48 | 7.1% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 1.1% |
| homographe_heterophone | 21 | 7.0% |
| liaison | 24 | 2.1% |
| nom_propre | 18 | 4.0% |
| nombre | 18 | 6.3% |
| onomatopee | 6 | 9.0% |
| ponctuation_repetee | 3 | 5.1% |
| silence_rythme | 21 | 7.5% |

**Durée instable (CV > seuil)** : p01, p02, p11, p16, p17, p18, p24, p25, p32, p34

## manou_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 2.7% |
| long | 12 | 2.2% |
| moyen | 48 | 2.3% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.6% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 4.1% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.1% |
| liaison | 24 | 0.4% |
| nom_propre | 18 | 1.5% |
| nombre | 18 | 2.1% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.3% |

## papa_colere — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 9 | 0.0% |
| moyen | 6 | 3.8% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_colere | 15 | 1.5% |

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
| court | 39 | 3.0% |
| long | 12 | 0.2% |
| moyen | 48 | 4.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.2% |
| dialogue_colere | 15 | 2.6% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 5.4% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 7.6% |
| homographe_heterophone | 21 | 2.6% |
| liaison | 24 | 0.1% |
| nom_propre | 18 | 4.9% |
| nombre | 18 | 0.1% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.3% |

**Troncature détectée sur** : p12, p28, p29, p33

**Durée instable (CV > seuil)** : p12

## papa_peur — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 6 | 0.0% |
| moyen | 3 | 3.7% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_peur | 9 | 1.2% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| silence_rythme | 9 | 1.2% |

**Durée instable (CV > seuil)** : p03

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
| court | 39 | 78.2% |
| long | 12 | 46.0% |
| moyen | 48 | 48.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 70.5% |
| dialogue_colere | 15 | 55.4% |
| dialogue_joie | 6 | 39.4% |
| dialogue_peur | 9 | 73.6% |
| dialogue_tristesse | 6 | 105.1% |
| narration | 48 | 52.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 44.1% |
| homographe_heterophone | 21 | 72.1% |
| liaison | 24 | 54.2% |
| nom_propre | 18 | 41.1% |
| nombre | 18 | 60.2% |
| onomatopee | 6 | 37.2% |
| ponctuation_repetee | 3 | 38.5% |
| silence_rythme | 21 | 52.4% |

**Hallucination détectée sur** : p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p23, p25, p26, p28, p29, p30, p31, p32, p33, p34

**Troncature détectée sur** : p01, p04, p05, p07, p09, p10, p12, p13, p16, p17, p20, p23, p25, p26, p30

**Durée instable (CV > seuil)** : p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p13, p15, p16, p17, p18, p19, p20, p23, p24, p25, p28, p29, p30, p31, p32, p33, p34

## tonton_marc_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 4.3% |
| long | 12 | 2.0% |
| moyen | 48 | 2.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.9% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 2.2% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 4.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 1.0% |
| homographe_heterophone | 21 | 3.2% |
| liaison | 24 | 0.1% |
| nom_propre | 18 | 2.2% |
| nombre | 18 | 1.3% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 3.3% |

**Troncature détectée sur** : p25, p29

**Durée instable (CV > seuil)** : p02, p23
