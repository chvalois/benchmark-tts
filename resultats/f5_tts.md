# Benchmark — f5_tts

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 123.6% | 144.9% | 2.74 | 0.856 | 100.0% | 4.0% | 99.0% | 0.45 | 2921 Mo | 0.0% |
| papa_narration | 99/99 | 105.4% | 60.5% | 2.86 | 0.818 | 100.0% | 3.0% | 99.0% | 0.58 | 2905 Mo | 0.0% |

## johnny — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 98.0% |
| long | 12 | 168.0% |
| moyen | 48 | 133.3% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 149.5% |
| dialogue_colere | 15 | 103.6% |
| dialogue_joie | 6 | 96.1% |
| dialogue_peur | 9 | 96.7% |
| dialogue_tristesse | 6 | 96.7% |
| narration | 48 | 133.6% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 97.9% |
| homographe_heterophone | 21 | 97.8% |
| liaison | 24 | 137.3% |
| nom_propre | 18 | 109.8% |
| nombre | 18 | 188.5% |
| onomatopee | 6 | 107.7% |
| ponctuation_repetee | 3 | 94.9% |
| silence_rythme | 21 | 135.5% |

**Hallucination détectée sur** : p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p28, p29, p30, p31, p32, p33, p34

**Répétition détectée sur** : p14, p26, p30

**Troncature détectée sur** : p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p28, p29, p30, p31, p32, p33, p34

## papa_narration — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 98.7% |
| long | 12 | 155.7% |
| moyen | 48 | 98.3% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 138.4% |
| dialogue_colere | 15 | 97.5% |
| dialogue_joie | 6 | 98.9% |
| dialogue_peur | 9 | 98.3% |
| dialogue_tristesse | 6 | 97.6% |
| narration | 48 | 100.7% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 96.7% |
| homographe_heterophone | 21 | 97.5% |
| liaison | 24 | 128.5% |
| nom_propre | 18 | 104.9% |
| nombre | 18 | 104.7% |
| onomatopee | 6 | 97.4% |
| ponctuation_repetee | 3 | 97.4% |
| silence_rythme | 21 | 130.9% |

**Hallucination détectée sur** : p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p28, p29, p30, p31, p32, p33, p34

**Répétition détectée sur** : p14, p26

**Troncature détectée sur** : p01, p02, p03, p04, p05, p06, p07, p08, p09, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23, p24, p25, p26, p28, p29, p30, p31, p32, p33, p34
