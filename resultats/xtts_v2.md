# Benchmark — xtts_v2

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 7.3% | 11.0% | 2.72 | 0.956 | 1.0% | 2.0% | 7.1% | 0.24 | 5509 Mo | 14.4% |
| papa_narration | 99/99 | 7.4% | 19.6% | 3.33 | 0.966 | 1.0% | 0.0% | 0.0% | 0.24 | 4904 Mo | 10.1% |

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
