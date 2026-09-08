# Benchmark TTS open source FR — synthèse (v1, 7 modèles)

**Protocole** : 34 phrases annotées × 3 répétitions × voix de référence.
Cœur du classement = `papa_narration` (27 s / 24 kHz / propre) ; `johnny`
(21 s / converti 44 kHz stéréo / brut) = réf « difficile ». \+ 3 voix
narration : `aurore2` (femme), `papy` (âgé, poème), `tonton_marc` (accent
Sud-Ouest) — cf. « Sensibilité à la voix de référence ». Transcription
`whisper-large-v3-french`, WER `jiwer` + détecteurs de fidélité
*language-agnostic* (portés d'`avisol`). RTX 4090, un modèle à la fois.

> ⚠️ **Métriques auto = WER (intelligibilité) + SIM (identité) seulement.**
> WER **brut** (aucun plancher humain soustrait ; une vraie voix humaine
> passée dans le même Whisper fait déjà ~2–4 %). **La naturalité n'a aucune
> métrique auto** (UTMOS / TTSDS2 / NISQA essayés puis retirés — voir §
> « Naturalité ») : elle se classe au **test d'écoute** (`resultats/ecoute.md`,
> n=80), qui devient l'élément décisif du classement.

## Classement (voix `papa_narration`, la plus propre)

| # | modèle | WER | ±σ | SIM | anom. (h/r/t) | RTF | VRAM | clon. | licence |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **FireRedTTS3** | **3,6 %** | 6,5 | 0,844 | 0/0/0 | 1,00 | 17 Go | oui | Apache-2.0 |
| 2 | **VoxCPM2** | 4,2 % | 8,0 | 0,822 | 0/0/**6,1 %** | 0,42 | 10 Go | oui | Apache-2.0 |
| 3 | **Chatterbox v3** | 4,8 % | 7,6 | 0,800 | 0/0/2 % | 0,59 | 6,5 Go | oui | MIT |
| 4 | **CosyVoice3-0.5B** | 4,9 % | 8,9 | 0,823 | 0/0/0 | 0,82 | 5 Go | oui | Apache-2.0 |
| 5 | **XTTS-v2** | 7,4 % | 19,6 | 0,745 | 1 %/0/0 | **0,24** | 4 Go | oui | **CPML — non comm.** |
| 6 | **Kokoro-82M** | 7,5 % | 18,0 | — | 3 %/0/3 % | **0,01** | 3 Go | **non** | Apache-2.0 |
| 7 | **MOSS-1.5** *(défauts)* | 7,9 % | **27,8** | 0,772 | 2 %/0/1 % | 0,69 | 16 Go | oui | Apache-2.0 |

*(WER = intelligibilité, ↓ mieux ; h/r/t = hallucination / répétition / troncature ;
SIM = cosinus **ECAPA-TDNN** ↑ mieux 0–1 ; RTF < 1 = + rapide que le temps réel.
**Ce tableau ne classe pas la naturalité** — voir « Naturalité » ci-dessous.)*

**Naturalité → test d'écoute uniquement.** Aucune métrique automatique de
naturalité dans le benchmark : UTMOS, TTSDS2 et NISQA ont été essayés puis
retirés (§ « Naturalité : pourquoi aucune métrique auto » plus bas). Le
classement de naturalité vient du MOS humain « Naturel » (`resultats/ecoute.md`,
n=80, IC ±0,45–0,70) :
**FireRed 4,08 · MOSS 3,25 · XTTS 3,22 · Chatterbox 3,17 · VoxCPM 3,10 ·
CosyVoice3 2,42**. FireRed se détache nettement ; CosyVoice3 décroche.

Sur la voix difficile `johnny` : FireRed 4,3 % (WER quasi inchangé, il
encaisse le mieux) ; ensuite VoxCPM/XTTS 7,3 %, Kokoro 7,5 %, MOSS 7,7 %,
Chatterbox 8,3 %, CosyVoice3 10,4 %. **Le SIM tombe à ~0,64–0,78 pour tous
sur `johnny`** (réf 44 kHz stéréo convertie, brute) contre ~0,75–0,84 sur
`papa_narration` → l'identité de timbre est captée mais moins nettement ;
l'écart de classement vient surtout de l'intelligibilité / la prosodie.

### Modèles non aboutis

| modèle | statut | raison |
|---|---|---|
| **F5-TTS** | ❌ FR non supporté | checkpoint de référence `F5TTS_v1_Base` = EN/ZH ; sortie FR inintelligible (WER > 100 %). Finetunes FR communautaires non maintenus seulement. |
| **PocketTTS** (Kyutai) | 🔒 bloqué | poids voice-cloning + voix catalogue derrière l'acceptation explicite des conditions sur huggingface.co/kyutai/pocket-tts (le token seul ne suffit pas). Déblocable côté compte HF. |
| **Audio8-0.6B**, **Parler-TTS FR** | ⬜ non tentés | prévus, pas encore intégrés |

### Naturalité : pourquoi aucune métrique automatique

**Trois métriques essayées, trois échecs sur le français** (corrélations
mesurées sur les 60 premières notes MOS « Naturel » ; le code de ces
métriques a depuis été retiré) :

| métrique | ce qu'elle mesure | résultat |
|---|---|---|
| **UTMOS** (`utmos22_strong`) | MOS prédit sans référence, SSL entraîné VoiceMOS EN | non calibré FR : les voix de réf **humaines** y scoraient 1,5–2,9, *sous* les TTS. Corr. MOS humain ≈ **−0,12**. |
| **TTSDS2** | distance distributionnelle vs vraie parole FR (MLS-French) | **anti-corrélé** : Spearman ≈ **−0,77** avec le MOS humain. Récompense les modèles plats/propres (Kokoro, XTTS) qui collent à la réf amateur ; pénalise FireRed/MOSS, jugés plus naturels à l'oreille. |
| **NISQA-TTS** | *Naturalness* prédite par énoncé, modèle 2020 EN | corr. MOS humain ≈ **−0,03** (nulle). |

**Cause commune** : ces métriques sont calibrées sur du MOS anglophone et/ou
sur une notion « proche de la vraie parole » qui, sur du TTS FR moderne
tous à quasi-parité (bande étroite), ne capte pas ce que l'oreille entend
— expressivité, chaleur, micro-prosodie. La proximité distributionnelle
n'est pas la qualité perçue.

**Conséquence** : la naturalité (et l'expressivité) se classent **à
l'écoute**, point. WER + SIM restent les seules métriques auto retenues
(intelligibilité, identité). Sur n=80 la corrélation MOS↔auto reste faible
(1−WER : r 0,02 ; SIM : r 0,14) — normal, ces axes bougent peu entre
modèles corrects. Cf. `docs/METHODOLOGIE.md` §10.

## Run émotions (`resultats/EMOTIONS.md`)

Voix de référence émotionnelle → phrases du registre correspondant.
**6 modèles** (FireRed, VoxCPM2, Chatterbox, MOSS, CosyVoice3, XTTS-v2 ;
Kokoro exclu, voix interne).
- **L'émotion ne casse pas l'intelligibilité** pour FireRed / VoxCPM2 /
  XTTS-v2 / MOSS (hors peur) : WER 0–5 %. Exceptions :
  `chatterbox_v3/papa_peur` (WER 10 %, hallu + troncature 11 % — cale sur
  le registre peur chuchoté), `moss/papa_peur` (WER 9 % ± 21,7 —
  instabilité MOSS), et surtout **CosyVoice3 sur les phrases courtes et
  sèches** : `papa_colere` WER 29 % (p02 « Non, mais ça suffit ! »
  s'effondre à 0,16 s sur 2 reps / 3 → troncature 13 %), `papa_joie`
  WER 19 % (TN parasite « Tu te » → « Tuesday »). CosyVoice3 a besoin de
  phrases longues.
- **L'identité tient** : SIM (ECAPA) 0,62–0,83 selon registre. La
  **tristesse** est le registre le plus dur pour l'identité (SIM la plus
  basse chez tous : min 0,62, médiane ~0,75 — cohérent avec §3.4, faible
  énergie/voisement).
- **Quel modèle *rend* le mieux l'émotion ?** → le mode **« A/B émotion »**
  du test `site/ecoute/` compare deux modèles clonant la **même** voix de
  réf émotionnelle sur la même phrase (« lequel rend le mieux
  l'émotion <X> ? ») → win-rate par (modèle, émotion). *(Ancien
  protocole « réf émotionnelle vs neutre » : résultat joué d'avance,
  abandonné ; data archivée toujours agrégée.)*

## Sensibilité à la voix de référence (`comparatif.md`, 7 voix)

4 voix ajoutées en narration : `aurore2` (femme, 24 s), `tonton_marc`
(accent du Sud-Ouest, 30 s, conte), `papy` (homme âgé, 30 s, **récitation
d'un poème très connu**), `manou` (femme âgée, 30 s, conte original).
SIM = ECAPA-TDNN (cf. §9), même-locuteur ~0,75–0,85.

- **Voix féminine** (`aurore2`) : clonage **propre**, WER 5,3–5,9 % (5
  modèles sur 6), SIM 0,69–0,81. MOSS seul déraille (WER 20 % — un run en
  boucle).
- **Accent du Sud-Ouest** (`tonton_marc`) : **pas de casse**, WER 4–6 %,
  accent capté. CosyVoice3 seul à 16 % (fragilité passe-1 générale). →
  **pas d'« accent parasite »**.
- **Femme âgée** (`manou`, conte **original**) : **rien ne casse** — WER
  3,5–8,4 % pour les 6 modèles (VoxCPM2 3,5 %, Chatterbox 3,9 % ;
  CosyVoice3 8,4 % tronc. 9 %). SIM 0,69–0,83 (FireRed devant, XTTS
  dernier). Une voix âgée se clone très bien.
- **Homme âgé + poème connu** (`papy`) : **effondrement des modèles
  “audio + transcript”** — VoxCPM2 **60 %** WER (49 % hallu, écho du
  prompt : « à l'heure où blanchit la campagne » → « Tombe au blanchi »),
  FireRed **77 %** WER. Les modèles **audio seul** (Chatterbox, XTTS, MOSS)
  encaissent (4,7–6,8 %).
- **Conclusion** — en comparant `papy` (poème) et `manou` (conte original),
  la cause est **le transcript de référence, pas l'âge** : « Demain, dès
  l'aube… » est un poème archi-mémorisé ; le modèle de texte
  auto-régressif *continue le poème* au lieu de basculer sur la phrase
  cible. **Le clonage audio+transcript est fragile aux références dont le
  texte a un prior de continuation fort** (poème/chanson connus) ; l'audio
  seul est immunisé. → éviter les textes de référence célèbres.

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

**CosyVoice3-0.5B — solide et léger, dépendances lourdes.**
WER 4,9 % sur `papa_narration`, **zéro anomalie**, seulement 5 Go de VRAM,
RTF 0,82. Mais **dernier à l'écoute pour la naturalité** (MOS 2,42). Se
dégrade sur `johnny` (WER 10,4 %, SIM 0,74).
Installation la plus pénible du lot (dépôt + sous-module Matcha-TTS, deps
pinnées, `<|endofprompt|>` obligatoire dans le prompt).
→ *Bon rapport qualité/VRAM si on accepte le coût de mise en place.*

**XTTS-v2 — le plus rapide des clonants, mais non commercial et instable.**
RTF 0,24 (4× temps réel), 4 Go. Mais WER 7,4 % ± 19,6 (forte variance),
cale complètement sur le registre `peur` (WER 28 %), et **licence CPML
bloquante**. Référence historique, plus un candidat produit.

## Décision rapide

| Contrainte dominante | Modèle |
|---|---|
| Fidélité maximale, GPU ≥ 20 Go | **FireRedTTS3** |
| Qualité + débit, GPU ~12 Go | **VoxCPM2** |
| Qualité, VRAM serrée (~5 Go), install one-off acceptée | **CosyVoice3-0.5B** |
| GPU ≤ 8 Go / beaucoup d'instances | **Chatterbox v3** |
| Débit extrême, voix neutre imposée OK | **Kokoro-82M** |
| Déjà investi sur MOSS en prod | **MOSS** (avec le handler calibré, pas les défauts) |

Tous les candidats retenus sont **Apache-2.0 ou MIT** → usage commercial OK.

## Limites de cette v1 (à lever)

1. **Écoute pas encore dépouillée** — le test en aveugle est prêt
   (`site/ecoute/` : MOS 1–5, A/B préférence, A/B émotion) mais aucun
   auditeur n'a encore renvoyé d'export. Obligatoire avant de publier un
   classement « officiel ».
2. **WER brut** — enregistrer les 34 phrases en voix humaine pour poser le
   plancher ASR et lire les WER *au-dessus*.
3. **Passe-1 seulement** — `chars_per_second` calibré par voix non appliqué
   (surtout critique pour MOSS).
4. **Voix de référence** : 1 féminine (`aurore2`), 4 masculines. `papy`
   cumule âge + registre poème (confond). Manque : locuteur âgé en
   narration neutre, voix d'enfant, qualité téléphone.
5. Artefact ASR connu : Whisper écrit « seconde » → « 2nde » (p33),
   « quatre-vingt-onze… » → « 91,3 % » (p15) — gonfle le WER de ces items.
