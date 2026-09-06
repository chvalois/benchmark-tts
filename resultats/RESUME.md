# Benchmark TTS open source FR — synthèse (v1, 5 modèles)

**Protocole** : 34 phrases annotées × 3 répétitions × 2 voix de référence
(`papa_narration` = 27 s / 24 kHz / propre ; `johnny` = 21 s / converti du
44 kHz stéréo / brut). Transcription `whisper-large-v3-french`, WER `jiwer`
+ détecteurs de fidélité *language-agnostic* (portés d'`avisol`). RTX 4090,
un modèle à la fois.

> ⚠️ **Métriques automatiques uniquement — pas encore d'écoute MOS/A-B.**
> WER **brut** (aucun plancher humain soustrait ; une vraie voix humaine
> passée dans le même Whisper fait déjà ~2–4 %). Les métriques **priorisent
> l'écoute**, elles ne tranchent pas seules.

## Classement (voix `papa_narration`, la plus propre)

| # | modèle | WER | ±σ | UTMOS | SIM | anomalies (h/r/t) | RTF | VRAM | clon. | licence |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **FireRedTTS3** | **3,6 %** | 6,5 | 3,26 | 0,964 | 0 / 0 / 0 | 1,00 | 17 Go | oui | Apache-2.0 |
| 2 | **VoxCPM2** | 4,2 % | 8,0 | 3,13 | **0,967** | 0 / 0 / **6,1 %** | 0,42 | 10 Go | oui | Apache-2.0 |
| 3 | **Chatterbox v3** | 4,8 % | 7,6 | **3,64** | 0,961 | 0 / 0 / 2 % | 0,59 | 6,5 Go | oui | MIT |
| 4 | **Kokoro-82M** | 7,5 % | **18,0** | **3,66** | — | 3 % / 0 / 3 % | **0,01** | 3 Go | **non** | Apache-2.0 |
| 5 | **MOSS-1.5** *(défauts)* | 7,9 % | **27,8** | 3,50 | **0,968** | 2 % / 0 / 1 % | 0,69 | 16 Go | oui | Apache-2.0 |

*(h/r/t = hallucination / répétition / troncature ; UTMOS ↑ mieux, ~1–5, non calibré FR ; SIM ↑ mieux, 0–1 ; RTF < 1 = + rapide que le temps réel)*

Sur la voix difficile `johnny` : FireRed 4,3 % (WER quasi inchangé) ; les
autres se dégradent (VoxCPM 7,3 %, Kokoro 7,5 %, MOSS 7,7 %, Chatterbox
8,3 %). **Mais le SIM reste ~0,96 pour tous sur `johnny`** → l'identité de
timbre est captée ; l'écart vient de l'intelligibilité / la prosodie, pas
d'une perte de voix.

### ⚠️ WER et UTMOS ne sont pas d'accord

Le meilleur WER (**FireRed**) a l'UTMOS le **plus bas** sur `johnny`
(2,78) ; **Chatterbox** et **Kokoro** ont le meilleur UTMOS (~3,65) avec un
WER moyen. Autrement dit : « dit exactement le texte » ≠ « sonne le plus
naturel ». C'est précisément pour ça qu'il faut **plusieurs métriques + de
l'écoute** — aucune ne tranche seule.

## Run émotions (`resultats/EMOTIONS.md`)

Voix de référence émotionnelle → phrases du registre correspondant.
- **L'émotion ne casse pas l'intelligibilité** : WER 0–5 % sur la plupart
  des (modèle, émotion). Deux exceptions : `chatterbox_v3/papa_peur`
  (WER 10 %, hallu + troncature 11 % — Chatterbox cale sur le registre peur
  chuchoté) et `moss/papa_peur` (WER 9 % ± 21,7 — instabilité MOSS).
- **L'identité tient** : SIM 0,91–0,98. La **tristesse** est le registre le
  plus dur pour l'identité (SIM la plus basse chez tous : 0,91–0,93 —
  cohérent avec §3.4, faible énergie/voisement).
- **Est-ce que ça *sonne* triste / en colère / apeuré ?** → question
  d'écoute pure, non mesurée ici. Audio fourni pour A/B avec la version
  neutre.

## Verdicts

**FireRedTTS3 — le plus précis et le plus robuste.**
WER 3,6–4,3 %, **zéro anomalie sur 396 générations**, et surtout **insensible
à la qualité de la voix de référence** (3,6 vs 4,3 entre les deux voix, là
où les autres explosent). Prix : **temps réel** (RTF ~1,0), **17 Go de
VRAM**, cold start ~85 s, `flash-attn` à compiler.
→ *Quand la fidélité prime et qu'on a le GPU pour.*

**VoxCPM2 — le meilleur compromis qualité/coût.**
WER 4,2 %, **2,4× temps réel**, 10 Go, 48 kHz. Deux réserves : **6 % de
troncature** sur `papa_narration` et forte variance sur `johnny`
(CV durée 11 %). Cold start ~85 s (torch.compile).
→ *Production à volume, si on tolère un filet de troncatures.*

**Chatterbox v3 — le plus léger des modèles clonants sérieux.**
WER 4,8 %, **6,5 Go de VRAM**, 1,7× temps réel. Sensible à la voix de
référence (4,8 → 8,3 sur `johnny`) et 2 % de troncature.
→ *GPU modeste, ou beaucoup d'instances en parallèle.*

**Kokoro-82M — la vitesse pure.**
**~100× temps réel**, 3 Go, parfaitement **déterministe** (CV 0 %),
excellent sur texte propre (cours magistral 1 %, homographes 1,6 %). Mais
**pas de clonage** (voix fixe `ff_siwis`), et s'effondre sur les
onomatopées (61 % WER) et le rythme/pauses.
→ *Débit massif de lecture neutre, sans besoin de voix personnalisée.*

**MOSS-TTS-Local-1.5 — instable en configuration par défaut.**
WER 7,9 % mais **σ 27,8 %** : `audio_temperature=1.7` (défaut du model
card) provoque exactement l'instabilité de longueur décrite dans le retour
d'expérience avisol (10 phrases sur 33 en durée instable). **Le handler
avisol calibré** (température plus basse, budget de tokens `chars_per_second`,
paramètres par catégorie) donnerait un résultat radicalement différent —
c'est la démonstration que *passe-1 = défauts* ne suffit pas pour MOSS.
→ *À re-tester en passe-2 avec les réglages de prod.*

## Décision rapide

| Contrainte dominante | Modèle |
|---|---|
| Fidélité maximale, GPU ≥ 20 Go | **FireRedTTS3** |
| Qualité + débit, GPU ~12 Go | **VoxCPM2** |
| GPU ≤ 8 Go / beaucoup d'instances | **Chatterbox v3** |
| Débit extrême, voix neutre imposée OK | **Kokoro-82M** |
| Déjà investi sur MOSS en prod | **MOSS** (avec le handler calibré, pas les défauts) |

Tous les candidats retenus sont **Apache-2.0 ou MIT** → usage commercial OK.

## Limites de cette v1 (à lever)

1. **Aucune écoute** — MOS / A-B en aveugle (Phase 4) obligatoire avant de
   publier un classement « officiel ».
2. **WER brut** — enregistrer les 34 phrases en voix humaine pour poser le
   plancher ASR et lire les WER *au-dessus*.
3. **Passe-1 seulement** — `chars_per_second` calibré par voix non appliqué
   (surtout critique pour MOSS).
4. **2 voix de référence**, toutes deux masculines — élargir la banque.
5. Artefact ASR connu : Whisper écrit « seconde » → « 2nde » (p33),
   « quatre-vingt-onze… » → « 91,3 % » (p15) — gonfle le WER de ces items.
