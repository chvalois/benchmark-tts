# Benchmark — cosyvoice3_05b

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | UTMOS | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 10.4% | 14.4% | 2.95 | 0.920 | 1.0% | 1.0% | 6.1% | 0.75 | 6378 Mo | 10.8% |
| papa_narration | 99/99 | 4.9% | 8.9% | 3.52 | 0.964 | 0.0% | 0.0% | 0.0% | 0.82 | 6258 Mo | 6.6% |

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
