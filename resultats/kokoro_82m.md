# Benchmark — kokoro_82m

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | SIM | hallu. | rép. | tronc. | RTF méd. | VRAM pic | CV durée |
|---|---|---|---|---|---|---|---|---|---|---|
| ff_siwis | 99/99 | 6.8% | 18.1% | — | 3.0% | 0.0% | 3.0% | 0.02 | 2965 Mo | 0.0% |

## ff_siwis — WER par catégorie

**Par longueur**

| longueur | n | WER moyen |
|---|---|---|
| court | 39 | 5.6% |
| long | 12 | 1.8% |
| moyen | 48 | 9.0% |

**Par registre**

| registre | n | WER moyen |
|---|---|---|
| cours_magistral | 15 | 1.1% |
| dialogue_colere | 15 | 4.6% |
| dialogue_joie | 6 | 0.0% |
| dialogue_peur | 9 | 6.7% |
| dialogue_tristesse | 6 | 0.0% |
| narration | 48 | 11.0% |

**Par piège**

| piège | n | WER moyen |
|---|---|---|
| emprunt_en | 6 | 6.7% |
| homographe_heterophone | 21 | 1.6% |
| liaison | 24 | 0.6% |
| nom_propre | 18 | 0.3% |
| nombre | 18 | 0.8% |
| onomatopee | 6 | 61.5% |
| ponctuation_repetee | 3 | 15.4% |
| silence_rythme | 21 | 21.1% |

**Hallucination détectée sur** : p23

**Troncature détectée sur** : p23
