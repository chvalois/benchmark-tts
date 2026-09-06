# Benchmark — firered_tts3

## Vue globale (par voix)

| voix | runs ok | WER moyen | ±σ | hallucination | répétition | troncature | RTF méd. | VRAM pic | CV durée méd. |
|---|---|---|---|---|---|---|---|---|---|
| johnny | 99/99 | 4.3% | 6.9% | 0.0% | 0.0% | 0.0% | 0.94 | 17028 Mo | 5.3% |
| papa_narration | 99/99 | 3.6% | 6.5% | 0.0% | 0.0% | 0.0% | 1.00 | 16944 Mo | 3.5% |

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
