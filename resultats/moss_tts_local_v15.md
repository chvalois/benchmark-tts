# Benchmark — moss_tts_local_v15

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|
| aurore2_narration | 99/99 | 20.3% | 103.7% | 0.706 | 2.0% | 0.0% | 1.0% | 0.64 | 16902 Mo | 13.5% |
| johnny | 99/99 | 7.7% | 10.8% | 0.643 | 1.0% | 0.0% | 1.0% | 0.63 | 16118 Mo | 14.3% |
| manou_narration | 99/99 | 6.4% | 24.1% | 0.753 | 1.0% | 1.0% | 0.0% | 0.65 | 16191 Mo | 6.7% |
| papa_colere | 15/15 | 2.8% | 5.2% | 0.708 | 0.0% | 0.0% | 0.0% | 0.70 | 15293 Mo | 10.2% |
| papa_joie | 6/6 | 1.1% | 2.5% | 0.764 | 0.0% | 0.0% | 0.0% | 1.09 | 15287 Mo | 15.1% |
| papa_narration | 99/99 | 7.9% | 27.8% | 0.772 | 2.0% | 0.0% | 1.0% | 0.69 | 16122 Mo | 7.7% |
| papa_peur | 9/9 | 9.0% | 21.7% | 0.641 | 0.0% | 0.0% | 0.0% | 0.68 | 15295 Mo | 25.4% |
| papa_tristesse | 6/6 | 0.0% | 0.0% | 0.616 | 0.0% | 0.0% | 0.0% | 0.66 | 15287 Mo | 15.6% |
| papy_narration | 99/99 | 6.8% | 13.1% | 0.782 | 0.0% | 0.0% | 1.0% | 0.62 | 16896 Mo | 11.4% |
| tonton_marc_narration | 99/99 | 6.8% | 18.2% | 0.717 | 1.0% | 1.0% | 1.0% | 0.64 | 16751 Mo | 12.4% |

## aurore2_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 42.5% |
| long | 12 | 3.4% |
| moyen | 48 | 6.4% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.6% |
| dialogue_colere | 15 | 66.2% |
| dialogue_joie | 6 | 3.9% |
| dialogue_peur | 9 | 5.3% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 18.8% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 3.3% |
| homographe_heterophone | 21 | 6.8% |
| liaison | 24 | 2.2% |
| nom_propre | 18 | 34.0% |
| nombre | 18 | 5.9% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 4.9% |

**Hallucination détectée sur** : p02, p24

**Troncature détectée sur** : p32

**Durée instable (CV > seuil)** : p01, p02, p03, p13, p16, p19, p21, p24, p25, p28, p33, p34

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

## manou_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 11.4% |
| long | 12 | 3.8% |
| moyen | 48 | 3.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 17.7% |
| dialogue_colere | 15 | 2.6% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 7.8% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 5.4% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 4.2% |
| liaison | 24 | 10.7% |
| nom_propre | 18 | 4.1% |
| nombre | 18 | 4.1% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 5.5% |

**Hallucination détectée sur** : p05

**Répétition détectée sur** : p23

**Durée instable (CV > seuil)** : p02, p04, p05, p21, p23

## papa_colere — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 9 | 0.0% |
| moyen | 6 | 7.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_colere | 15 | 2.8% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| homographe_heterophone | 3 | 0.0% |
| nombre | 3 | 6.2% |
| ponctuation_repetee | 3 | 0.0% |

**Durée instable (CV > seuil)** : p07

## papa_joie — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 3 | 0.0% |
| moyen | 3 | 2.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_joie | 6 | 1.1% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| liaison | 3 | 2.2% |

**Durée instable (CV > seuil)** : p06

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

## papa_peur — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 6 | 11.7% |
| moyen | 3 | 3.7% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| dialogue_peur | 9 | 9.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| silence_rythme | 9 | 9.0% |

**Durée instable (CV > seuil)** : p03, p34

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

**Durée instable (CV > seuil)** : p09

## papy_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 10.8% |
| long | 12 | 2.6% |
| moyen | 48 | 4.6% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.1% |
| dialogue_colere | 15 | 10.1% |
| dialogue_joie | 6 | 5.6% |
| dialogue_peur | 9 | 11.1% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 7.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 5.3% |
| liaison | 24 | 2.3% |
| nom_propre | 18 | 5.3% |
| nombre | 18 | 5.8% |
| onomatopee | 6 | 9.0% |
| ponctuation_repetee | 3 | 25.6% |
| silence_rythme | 21 | 8.1% |

**Troncature détectée sur** : p23

**Durée instable (CV > seuil)** : p01, p03, p04, p08, p17, p18, p19, p20, p22, p23, p28, p30, p34

## tonton_marc_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 10.5% |
| long | 12 | 3.7% |
| moyen | 48 | 4.5% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.2% |
| dialogue_colere | 15 | 5.6% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 4.6% |
| dialogue_tristesse | 6 | 27.1% |
| narration | 48 | 7.3% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 14.6% |
| liaison | 24 | 1.6% |
| nom_propre | 18 | 4.3% |
| nombre | 18 | 4.0% |
| onomatopee | 6 | 9.0% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 4.8% |

**Hallucination détectée sur** : p04

**Répétition détectée sur** : p23

**Troncature détectée sur** : p32

**Durée instable (CV > seuil)** : p01, p02, p04, p05, p08, p09, p12, p19, p21, p24, p25, p32, p33, p34
