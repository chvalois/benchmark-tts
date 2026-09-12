# Benchmark — audio8_06b

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|
| aurore2_narration | 99/99 | 4.0% | 5.9% | 0.708 | 0.0% | 0.0% | 0.0% | 1.12 | 5835 Mo | 2.5% |
| johnny | 99/99 | 5.0% | 7.9% | 0.675 | 0.0% | 0.0% | 2.0% | 1.11 | 5833 Mo | 9.4% |
| manou_narration | 99/99 | 3.7% | 6.1% | 0.749 | 0.0% | 0.0% | 0.0% | 1.13 | 8294 Mo | 2.7% |
| papa_colere | 15/15 | 2.0% | 3.3% | 0.748 | 0.0% | 0.0% | 0.0% | 1.11 | 5620 Mo | 3.8% |
| papa_joie | 6/6 | 0.0% | 0.0% | 0.727 | 0.0% | 0.0% | 0.0% | 1.52 | 5621 Mo | 3.7% |
| papa_narration | 99/99 | 3.7% | 6.2% | 0.765 | 0.0% | 0.0% | 0.0% | 1.13 | 5875 Mo | 2.9% |
| papa_peur | 9/9 | 0.0% | 0.0% | 0.759 | 0.0% | 0.0% | 0.0% | 1.12 | 6299 Mo | 5.2% |
| papa_tristesse | 6/6 | 0.0% | 0.0% | 0.641 | 0.0% | 0.0% | 0.0% | 1.14 | 6330 Mo | 4.7% |
| papy_narration | 99/99 | 3.6% | 6.1% | 0.770 | 0.0% | 0.0% | 1.0% | 1.13 | 8277 Mo | 2.3% |
| tonton_marc_narration | 99/99 | 3.0% | 5.6% | 0.713 | 0.0% | 0.0% | 0.0% | 1.12 | 8016 Mo | 4.7% |

## aurore2_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.2% |
| long | 12 | 4.3% |
| moyen | 48 | 4.7% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.8% |
| dialogue_colere | 15 | 4.8% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 5.9% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 3.1% |
| liaison | 24 | 1.8% |
| nom_propre | 18 | 5.7% |
| nombre | 18 | 6.5% |
| onomatopee | 6 | 9.0% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 3.4% |

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 2.8% |
| long | 12 | 3.6% |
| moyen | 48 | 7.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.2% |
| dialogue_colere | 15 | 3.1% |
| dialogue_joie | 6 | 5.0% |
| dialogue_peur | 9 | 0.6% |
| dialogue_tristesse | 6 | 1.2% |
| narration | 48 | 7.9% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.1% |
| liaison | 24 | 2.7% |
| nom_propre | 18 | 7.6% |
| nombre | 18 | 4.9% |
| onomatopee | 6 | 11.5% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 3.9% |

**Troncature détectée sur** : p01, p33

**Durée instable (CV > seuil)** : p01, p04, p16, p25, p29, p33

## manou_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 2.4% |
| long | 12 | 3.9% |
| moyen | 48 | 4.6% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.2% |
| dialogue_colere | 15 | 2.0% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 6.3% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.0% |
| liaison | 24 | 3.8% |
| nom_propre | 18 | 5.1% |
| nombre | 18 | 6.7% |
| onomatopee | 6 | 5.1% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 1.8% |

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
| court | 39 | 2.4% |
| long | 12 | 0.7% |
| moyen | 48 | 5.5% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 0.0% |
| dialogue_colere | 15 | 2.8% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 6.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 1.6% |
| liaison | 24 | 3.3% |
| nom_propre | 18 | 7.4% |
| nombre | 18 | 5.4% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.2% |

**Durée instable (CV > seuil)** : p02

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
| court | 39 | 2.4% |
| long | 12 | 3.2% |
| moyen | 48 | 4.7% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.4% |
| dialogue_colere | 15 | 2.8% |
| dialogue_joie | 6 | 1.1% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 6.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.0% |
| liaison | 24 | 1.7% |
| nom_propre | 18 | 6.0% |
| nombre | 18 | 6.3% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.2% |

**Troncature détectée sur** : p26

## tonton_marc_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 2.4% |
| long | 12 | 1.3% |
| moyen | 48 | 4.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 0.7% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 5.6% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 1.6% |
| liaison | 24 | 1.3% |
| nom_propre | 18 | 5.3% |
| nombre | 18 | 4.1% |
| onomatopee | 6 | 7.7% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.4% |

**Durée instable (CV > seuil)** : p02, p24
