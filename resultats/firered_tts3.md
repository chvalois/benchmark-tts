# Benchmark — firered_tts3

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 4.3% | 6.9% | 2.78 | 0.960 | 0.0% | 0.0% | 0.0% | 0.94 | 17028 Mo | 5.3% |
| papa_colere | 15/15 | 5.5% | 7.8% | 3.16 | 0.960 | 0.0% | 0.0% | 0.0% | 0.94 | 16898 Mo | 3.9% |
| papa_joie | 6/6 | 0.0% | 0.0% | 3.26 | 0.974 | 0.0% | 0.0% | 0.0% | 1.00 | 16894 Mo | 3.2% |
| papa_narration | 99/99 | 3.6% | 6.5% | 3.26 | 0.964 | 0.0% | 0.0% | 0.0% | 1.00 | 16944 Mo | 3.5% |
| papa_peur | 9/9 | 0.0% | 0.0% | 3.00 | 0.975 | 0.0% | 0.0% | 0.0% | 0.94 | 16937 Mo | 4.1% |
| papa_tristesse | 6/6 | 0.0% | 0.0% | 2.93 | 0.919 | 0.0% | 0.0% | 0.0% | 0.95 | 16942 Mo | 4.1% |

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
