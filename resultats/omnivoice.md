# Benchmark — omnivoice

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|
| aurore2_narration | 99/99 | 3.3% | 6.3% | 0.786 | 0.0% | 0.0% | 0.0% | 0.25 | 5468 Mo | 0.0% |
| johnny | 99/99 | 4.3% | 8.2% | 0.797 | 0.0% | 0.0% | 1.0% | 0.23 | 5468 Mo | 0.0% |
| manou_narration | 99/99 | 3.3% | 6.4% | 0.803 | 0.0% | 0.0% | 1.0% | 0.27 | 6367 Mo | 1.4% |
| papa_colere | 15/15 | 1.5% | 3.1% | 0.788 | 0.0% | 0.0% | 0.0% | 0.36 | 5252 Mo | 4.8% |
| papa_joie | 6/6 | 0.0% | 0.0% | 0.792 | 0.0% | 0.0% | 0.0% | 0.31 | 5248 Mo | 0.0% |
| papa_narration | 99/99 | 2.3% | 4.8% | 0.823 | 0.0% | 0.0% | 0.0% | 0.29 | 5475 Mo | 0.5% |
| papa_peur | 9/9 | 0.0% | 0.0% | 0.776 | 0.0% | 0.0% | 0.0% | 0.29 | 5854 Mo | 0.0% |
| papa_tristesse | 6/6 | 0.0% | 0.0% | 0.775 | 0.0% | 0.0% | 0.0% | 0.27 | 5854 Mo | 0.0% |
| papy_narration | 99/99 | 12.7% | 19.7% | 0.862 | 3.0% | 0.0% | 1.0% | 0.22 | 6739 Mo | 0.0% |
| tonton_marc_narration | 99/99 | 2.7% | 5.1% | 0.792 | 0.0% | 0.0% | 0.0% | 0.25 | 6739 Mo | 1.2% |

## aurore2_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.5% |
| long | 12 | 3.3% |
| moyen | 48 | 3.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.2% |
| dialogue_colere | 15 | 2.4% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 5.3% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.6% |
| liaison | 24 | 1.4% |
| nom_propre | 18 | 4.0% |
| nombre | 18 | 5.2% |
| onomatopee | 6 | 5.1% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 1.8% |

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 4.1% |
| long | 12 | 5.0% |
| moyen | 48 | 4.3% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.9% |
| dialogue_colere | 15 | 3.0% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 4.0% |
| dialogue_tristesse | 6 | 2.4% |
| narration | 48 | 6.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.9% |
| liaison | 24 | 1.2% |
| nom_propre | 18 | 6.3% |
| nombre | 18 | 5.2% |
| onomatopee | 6 | 6.4% |
| ponctuation_repetee | 3 | 2.6% |
| silence_rythme | 21 | 4.1% |

**Troncature détectée sur** : p09

## manou_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 2.6% |
| long | 12 | 5.8% |
| moyen | 48 | 3.2% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 4.2% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 1.1% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 4.8% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 1.6% |
| liaison | 24 | 2.5% |
| nom_propre | 18 | 5.1% |
| nombre | 18 | 4.0% |
| onomatopee | 6 | 3.8% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 3.3% |

**Troncature détectée sur** : p32

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
| court | 39 | 2.4% |
| long | 12 | 3.2% |
| moyen | 48 | 2.1% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 2.2% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 3.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 1.6% |
| liaison | 24 | 0.2% |
| nom_propre | 18 | 2.4% |
| nombre | 18 | 3.0% |
| onomatopee | 6 | 3.8% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 1.4% |

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
| court | 39 | 17.5% |
| long | 12 | 17.5% |
| moyen | 48 | 7.6% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 9.5% |
| dialogue_colere | 15 | 23.7% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 17.0% |
| dialogue_tristesse | 6 | 11.9% |
| narration | 48 | 11.1% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 1.1% |
| homographe_heterophone | 21 | 9.8% |
| liaison | 24 | 7.1% |
| nom_propre | 18 | 7.8% |
| nombre | 18 | 11.1% |
| onomatopee | 6 | 9.0% |
| ponctuation_repetee | 3 | 38.5% |
| silence_rythme | 21 | 15.6% |

**Hallucination détectée sur** : p03, p25, p33

**Troncature détectée sur** : p03

## tonton_marc_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 3.0% |
| long | 12 | 3.3% |
| moyen | 48 | 2.4% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.6% |
| dialogue_colere | 15 | 1.5% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 0.0% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 4.6% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 0.0% |
| homographe_heterophone | 21 | 2.6% |
| liaison | 24 | 1.1% |
| nom_propre | 18 | 3.7% |
| nombre | 18 | 3.4% |
| onomatopee | 6 | 3.8% |
| ponctuation_repetee | 3 | 0.0% |
| silence_rythme | 21 | 2.0% |
