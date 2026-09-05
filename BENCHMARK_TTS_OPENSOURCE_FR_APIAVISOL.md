# Benchmark TTS open source (français) — Base de connaissances

> Document de cadrage pour un futur projet de **benchmark de modèles TTS open source,
> évalués uniquement en français**. Il regroupe :
> 1. le retour d'expérience accumulé sur `avisol-api` (moteurs Chatterbox + MOSS) ;
> 2. les leçons transverses indépendantes du modèle ;
> 3. une méthodologie de benchmark dérivée de ces leçons ;
> 4. une checklist de pièges à tester explicitement ;
> 5. les contraintes d'infrastructure (RunPod serverless) ;
> 6. une liste de modèles candidats.
>
> Périmètre : **synthèse vocale narrative** (livre audio, conte, histoire pour
> enfants, dialogue de roman) avec **clonage de voix zero-shot**. Pas de TTS
> temps réel / assistant vocal. Langue cible : **français** exclusivement (le
> multilingue n'est évalué que comme risque de régression sur le FR).

---

## 1. Objectif & critères de succès

Un moteur TTS est retenu pour ce cas d'usage s'il coche, dans l'ordre de priorité :

1. **Fidélité au texte** — il dit exactement le texte fourni, sans hallucination,
   sans répétition parasite, sans troncature du dernier mot.
2. **Qualité de voix clonée** — timbre proche de la référence, prosodie naturelle
   en français, pas d'accent étranger sur du texte FR.
3. **Stabilité** — deux générations du même texte donnent un résultat
   comparable en durée et en qualité (faible variance).
4. **Contrôle de la durée** — l'audio produit correspond au débit attendu, y
   compris sur un texte long (> 5 min).
5. **Expressivité** — capacité à rendre narration posée vs dialogue vivant vs
   réplique courte.
6. **Coût / perf** — RTF (real-time factor), cold start, VRAM, € par minute
   d'audio.
7. **Licence** — compatible usage commercial (à vérifier modèle par modèle,
   voir §7).

> ⚠️ Leçon centrale du projet (voir §3.3) : **ne jamais classer un modèle sur les
> seules métriques automatiques de durée/budget**. L'écoute humaine en aveugle
> reste l'arbitre final ; les métriques servent à filtrer et à prioriser
> l'écoute, pas à trancher.

---

## 2. Modèles déjà explorés dans `avisol-api` (retour d'expérience)

| Modèle | Taille | Chargement | Clonage zero-shot | Multilingue FR | Statut projet | Cold start |
|---|---|---|---|---|---|---|
| **Chatterbox Multilingual TTS** | ~0.5B (T3 v3) | `chatterbox-tts` + source `resemble-ai/chatterbox` | Oui (référence WAV) | Oui — `language_id` global **+** balise `<lang:XX>` | **Moteur de prod** | ~30 s |
| **MOSS-TTS-Local-Transformer-v1.5** | 5B | HF `AutoModel`/`AutoProcessor`, `trust_remote_code=True` | Oui (référence WAV) | Oui — **balise `<lang:XX>` uniquement**, pas de `language_id` global | **Moteur de prod (complément)** | ~5 min (poids 5B depuis volume) |
| MOSS-TTS-v1.5 | 8B | idem | Oui | idem | Testé avant la 5B, écarté au profit de la variante allégée | plus lourd encore |
| **VibeVoice** | — | in-process (`ModelLoader`) | — | — | **Abandonné** — code `api/` legacy, non branché | — |
| **Voxtral-4B-TTS-2603** (Mistral) | 4B | vLLM (`vllm/vllm-omni`) | Oui | À vérifier | **Test en pause** — conflit torch local, à reprendre sur RunPod via Docker officiel `vllm/vllm-omni:v0.18.0` | — |

### Modèles auxiliaires utilisés (utiles pour le harnais de benchmark)

| Rôle | Modèle / lib | Note |
|---|---|---|
| Validation par transcription | `faster-whisper` **small** int8 (CTranslate2) | Indépendant de la stack torch (aucun conflit). `medium` testé puis écarté (~18 s/chunk, trop lourd). `small` ~3× plus rapide, suffisant pour une grosse dérive. |
| Normalisation des nombres | `num2words` | Indispensable avant comparaison de transcription (« 73 » vs « soixante-treize »). |
| Phonémisation (sauvetage faux positifs) | `espeak-ng` + `phonemizer` | Compare des phonèmes, pas des graphèmes — absorbe élisions/liaisons FR. |
| Nettoyage voix de référence | ClearerVoice `MossFormer2_SE_48K`, DeepFilterNet, Silero VAD | Cascade SNR-adaptative. ⚠️ DeepFilterNet cassé en torchaudio ≥ 2.9. |

### 2.1 Chatterbox — points clés

- Clonage zero-shot à partir d'un WAV de référence (3–80 s acceptés, 3–15 s
  recommandés, **30 s max réellement utilisés**).
- Paramètre `exaggeration` (expressivité) ; détection de dialogue native si la
  ligne commence par `—`/`-`/`«`.
- **Chunking phrase par phrase** (`runpod/chatterbox_chunker.py`) — insertion des
  sons ponctuels à la granularité de la phrase.
- Détecteur d'hallucination intégré (`_detect_hallucination`) mais **limité aux
  chunks ≤ 2 mots** avec retry automatique.
- Hallucinations observées : étirement de phonème (« Aliccccce »), passage de
  mots incohérents — apparues après un changement de pipeline de nettoyage de la
  référence, non reproduites de façon stable.

### 2.2 MOSS-TTS-Local-Transformer-v1.5 — points clés

- **Codec audio à débit fixe : 12,5 frames/seconde.** 1 token de durée = 1 frame
  = 0,08 s d'audio. Propriété physique, non réglable.
- **Piloté par une durée cible** qu'il cherche à remplir → le handler calcule un
  **budget de tokens** via une heuristique `chars_per_second` (≈ 17–18 car/s par
  défaut, réglable 10–30, **réglable par voix**).
- `bfloat16` sur CUDA, `attn_implementation` = `sdpa` (flash-attn non requis,
  repli systématique validé).
- **Catégorisation automatique** narration / dialogue / réplique courte, avec des
  paramètres de génération dédiés par catégorie (température plus haute en
  dialogue, quasi-déterministe en réplique courte).
- **Deux jeux de paramètres de sampling distincts** (piège majeur, voir §3.6) :
  `audio_temperature/top_p/top_k/repetition_penalty` (timbre, expressivité) vs
  `text_temperature/top_p/top_k` (mécanisme interne de continuation : décide
  frame par frame si le modèle continue ou s'arrête).
- Tag natif `[pause N.Ns]` documenté — **uniquement en milieu de texte**, jamais
  après la ponctuation finale d'un segment.
- **Pas de `language_id` global** : la langue de synthèse est portée **uniquement
  par la balise `<lang:XX>`** ; en son absence, repli « French ». Une voix de
  référence native ne pilote **pas** la langue.
- Multi-voix `<voice:alias>` : un changement de voix **casse toujours** la fusion
  de bloc (un appel `generate()` = une seule voix de référence).

### 2.3 Décisions d'architecture transposables au benchmark

- **Un endpoint / un process par modèle** — jamais deux modèles chargés sur le
  même GPU. Le benchmark doit isoler chaque moteur (image Docker + endpoint
  dédiés).
- **Chunking non partagé entre moteurs** (`chatterbox_chunker.py` vs
  `moss_chunker.py`, forks indépendants) — les règles de pause/silence diffèrent
  trop. Pour le benchmark : prévoir un chunker paramétrable **par famille de
  modèle**, pas un chunker unique.
- **Assemblage sons/musique/effets partagé** (`runpod/audio_mixing.py`,
  `runpod/audio_effects.py`) — générique, indépendant du moteur TTS. Peut être
  réutilisé tel quel dans le harnais.

---

## 3. Leçons transverses (indépendantes du modèle)

Ce sont les enseignements les plus coûteux à réapprendre — chacun est à re-tester
sur tout nouveau moteur.

### 3.1 Chunking obligatoire, fusion par blocs

- **Ne jamais générer un texte long en un seul appel.** Sur MOSS, une histoire
  complète (~3 400 caractères) générée d'un coup a produit +50 % de durée
  (plafonnée par `max_new_tokens`) avec effondrement de la cohérence. Le contrôle
  de durée du modèle **décroche complètement** au-delà d'une certaine longueur.
  → Le chunking + une borne dure `MAX_WORDS_PER_CHUNK` (≈ 60 mots) sont une
  **nécessité technique**, pas une optimisation de style.
- **Fusionner les phrases en blocs** (paragraphe / dialogue), jusqu'à un saut de
  paragraphe, un changement narration↔dialogue, ou la borne de mots. Générer
  chaque phrase isolément introduit trop de variation de timbre/débit d'un chunk
  à l'autre (une seule conditioning de voix par bloc).
- **Deux mécanismes de pause à ne pas confondre** :
  - pause de **fin de chunk** = silence pur (`torch.zeros`) ajouté **après**
    génération, jamais envoyé au modèle, jamais compté au budget ;
  - pause **inline** = tag natif `[pause N.Ns]` inséré dans le texte, en milieu
    de chunk seulement, **compté** au budget.
- Un `.` collé juste avant un `[pause]` inline rejoue une intonation de « point
  final » + blanc → hache la lecture. Le retirer (garder `?`/`!` qui portent du
  sens).
- **Titre sans ponctuation terminale** → ajouter un `.` automatiquement, sinon
  intonation ouverte.

### 3.2 Contrôle de durée & budget de tokens

- Le budget de tokens reste une **heuristique** (`chars_per_second`), pas une
  mesure du débit réel de la voix clonée — il varie selon la voix et la langue.
- Le **débit `chars_per_second` doit être calibré par voix.** Une voix « excitée »
  à répliques courtes et un narrateur posé n'ont pas le même débit ; un débit
  unique sur- ou sous-dimensionne le budget d'une partie des chunks (remplissage
  ou troncature). Mesure automatique du débit hors silences (via un WAV de
  référence nettoyé transcrit) = bon point de départ ; l'oreille cale ~1 point
  au-dessus.
- Pistes de correction de la **troncature du dernier mot** toutes essayées et
  **écartées** sur MOSS : marge de tokens artificielle (+15 / +30 %, dégrade la
  diction sans rien régler), `text_*` resserré (aide sur les pauses mi-phrase
  mais **aggrave** la troncature), plancher `min_new_frames` (rythme plus lent ET
  troncature persistante), espaces en fin de texte (effet nul), budget de queue
  asymétrique (effet < 25 ms, retiré). → La cause n'est probablement **pas** le
  budget/durée mais le rendu des frames terminales par le modèle/vocodeur.

### 3.3 « Les métriques de durée ne sont pas un proxy de qualité perçue » ⚠️

À encadrer. Constats répétés sur MOSS :

- Toutes les interventions « budget » ci-dessus pouvaient faire coller
  `obtenu ≈ cible` presque partout **pendant que la troncature audible
  persistait**.
- `hit_cap` (le clip occupe ~tout son budget de tokens) : ~90 % des chunks
  flaggés sont des répliques d'1–3 mots (`Oui.`, `Non.`, `Pourquoi ?`)
  **parfaitement rendues** — `hit_cap` seul a été **retiré** de la détection
  d'anomalie.
- `n_anomalies` **n'est pas un proxy de qualité** : la version `cps=27`, préférée
  à l'écoute, montait *plus* d'anomalies que `cps=22`.
- Conséquence pour le benchmark : les métriques automatiques **priorisent
  l'écoute**, elles ne notent pas.

### 3.4 Clonage de voix : longueur & voisement de la référence

- **Identité clonable ∝ longueur + voisement de la référence.** Viser **12–20 s
  de parole réelle voisée** (30 s max réellement utilisés par les handlers). Des
  clips de ~6 s font *décrocher* le modèle (identité perdue + durée bâclée).
- **Un chuchotement pur (0 % de voisement) = identité non clonable** — le
  pitch/les harmoniques des cordes vocales portent ~90 % de l'identité. Pour un
  registre chuchoté, enregistrer un « chuchotement de scène » (soufflé mais
  voisé).
- Le **format** de la référence (stéréo / sample rate / mp3) n'est pas un
  problème : le processor down-mixe + loudnorm proprement.
- Le **nettoyage** de la référence (ClearerVoice + VAD + loudnorm) améliore
  identité + tenue de durée. Mais un `loudnorm` + `acompressor` **inconditionnel**
  est une piste de déstabilisation de la prosodie (référence « trop poussée »
  envoyée au modèle de clonage).
- **Double référence** `[ancrage identité + clip émotion]` : testée, jugée
  inefficace sur MOSS.

### 3.5 Pilotage de l'émotion / du style

- Sur MOSS, le champ **`instruction` / `sound_event` a un effet nul** (A/B
  contrôlé : « whisper » vs « shout angry » sortent au même RMS ± 4 % ;
  « clearing throat » ne produit aucune vocalisation). Câblage vérifié correct de
  bout en bout — c'est une **limite du modèle** (le conditionnement audio domine
  en clonage zero-shot).
- **Le seul levier fiable d'émotion = la voix de référence** : enregistrer une
  référence longue par registre (normal, narration, dialogue, surprise,
  chuchotement, peur, tendresse, joie, colère…) et taguer les phrases avec
  `<voice:registre>`.
- **Ne jamais taguer un `<voice:>` sur une phrase < ~10 mots** — isoler une
  micro-phrase dans son propre bloc de voix casse la fusion et fait dériver la
  durée. Soit la fusionner dans la phrase voisine du même registre, soit la
  laisser en voix par défaut.
- **Éviter un registre « rire »** (« ha ha ha » articulés) — 0 % de voisement →
  perte d'identité + rendu plat. Utiliser « joie » à la place.

### 3.6 Paramètres de sampling

- **`audio_repetition_penalty` doit toujours être ≥ 1.0.** En dessous, le
  mécanisme s'inverse et **récompense** la répétition → boucle « dudududu » sur
  presque tous les chunks. À verrouiller par validation (borne `ge=1.0`), pas
  seulement par la doc.
- **`text_temperature` / `text_top_p` / `text_top_k`** (mécanisme de continuation
  interne) : ne pas les exposer / ne pas les resserrer. Resserrés (0.3 / 0.9 / 5)
  ils réduisent les pauses aléatoires mi-phrase mais provoquent une **troncature
  systématique du dernier mot**.
- Mode **greedy (`do_sample=False`)** : testé, dégrade fortement l'audio.
- Température audio élevée (1.7 sur MOSS Local Transformer) → **instabilité de
  longueur** : même voix, un run s'arrête net à 48 s en plein texte, le run
  suivant dérive jusqu'au plafond dur sans émettre de token de fin. Fixer un
  **seed** pour isoler la variance ; tester des températures plus basses
  (1.0–1.3).

### 3.7 Hallucinations & répétitions — signatures observées

- **MOSS peut halluciner un contenu de « conte pour enfants » récurrent** quand
  il « perd le fil » du texte source : « il était une fois… », « dans une forêt
  pas si lointaine… », « un petit renard qui n'avait jamais… », « tapis tout
  blanc / premiers flocons ». Signature reproductible, ~100 % de vrais positifs.
  ⚠️ **Ne pas coder de liste de mots-clés** dans le harnais générique (choix
  explicite : rester *language-agnostic*) — c'est une observation de debug, pas
  un détecteur.
- **Ponctuation répétée** (`« Encore !! Encore le crabe… »`,
  `« Rrrmmm !!! Rrrmmm !!! »`) : le chunker coupe au milieu de la réplique sur
  les `!`/`.` répétés, le second fragment perd son marqueur de dialogue → mal
  catégorisé, isolé, souvent en anomalie de durée. Contournement : nettoyage
  amont (ponctuation répétée → virgules). **À tester** sur onomatopées.

### 3.8 Multilingue / cross-lingue & balises de langue

- **Le clonage cross-lingue garde l'accent de la référence.** Une voix FR clonée
  puis synthétisée en `<lang:en>` garde un **accent français marqué**, même avec
  la balise de langue correcte (recall/hallucination ne mesurent pas l'accent).
  → Pour du multilingue, préférer des **voix natives par langue**.
- **Toujours vérifier que la balise `<lang:XX>` est présente** — ne jamais
  supposer qu'une voix de référence native suffit à piloter la langue de
  synthèse (vrai sur MOSS, à re-vérifier par modèle).
- Pour un benchmark **FR uniquement**, le multilingue sert surtout de **test de
  non-régression** : vérifier que le modèle en mode « français » ne prend pas un
  accent anglais sur des mots ambigus (noms propres, emprunts).

### 3.9 Pré-traitement du texte avant TTS (corpus FR)

Repris du pipeline de production (`PIPELINE_TRAITEMENT_SCRIPT_AVANT_API_AVISOL.md`),
à appliquer **identiquement à tous les modèles** pour comparer à conditions égales :

1. Retirer les titres markdown / structure.
2. Retirer la **virgule d'incise avant un verbe de parole rapportée**
   (`", répond Juliette."` → `" répond Juliette."`) — casse le débit sinon.
3. Normaliser `...` et `…` → `.` (mal interprétés : hésitation / coupure).
4. Désamorcer les `!` dans les onomatopées entre astérisques (`*Vroum!*` → `*Vroum*`).
5. Insérer un saut de ligne en fin de phrase **seulement** si une vraie nouvelle
   phrase suit (garde majuscule/chiffre, exclut `M.`/`Mme`).
6. **Supprimer les émojis** (regex Unicode couvrant tous les blocs) — font planter
   les moteurs.

### 3.10 Pièges techniques audio

- Tensors `bfloat16` → **convertir en `float32` avant l'encodage** WAV/MP3.
- Charger l'audio via `soundfile` / `librosa`, **pas `torchaudio.load()`**
  (problèmes de backend ; torchaudio ≥ 2.9 route tout via `torchcodec`).
- Toujours **convertir en mono + rééchantillonner explicitement**
  (`librosa.load(path, sr=24000, mono=True)`).
- **Forme du tenseur de sortie** : `squeeze(0)` / `squeeze()` ne garantit pas un
  résultat 1D. **Ne jamais faire `reshape(-1)`** : si une dimension non singleton
  subsiste (ex. `(2, N)`), ça concatène les lignes → **chaque chunk joué deux
  fois** (bug silencieux, invisible sur un test court). Bon fix : `squeeze()`
  puis, si `ndim > 1`, ne garder que la **ligne 0**.
- **Un fix qui supprime un crash n'est pas forcément correct** — vérifier le
  *contenu* (durée attendue, écoute), pas seulement l'absence d'erreur.

---

## 4. Méthodologie de benchmark proposée

### 4.1 Corpus de test FR

Un jeu de textes courts et ciblés, chacun stressant une capacité précise. Tous en
français, tous passés par le pré-traitement §3.9.

| # | Catégorie | Contenu | Ce qu'on mesure |
|---|---|---|---|
| C1 | Narration posée | Paragraphe de conte / roman, ~120 mots, phrases longues | Naturel, prosodie, respiration |
| C2 | Dialogue | Échange de répliques (tiret cadratin `—`), incises de parole | Vivacité, changement de ton, incises non hachées |
| C3 | Répliques courtes | `Oui.` / `Non.` / `Pourquoi ?` / `Il se leva.` | Sur-génération (budget démesuré vs texte), diction |
| C4 | Onomatopées & ponctuation répétée | `*Vroum*`, `— Encore, encore !`, `Rrrmmm…` | Robustesse chunker, catégorisation |
| C5 | Nombres & heures | « 73 marches », « 10 h 45 », « le 14 juillet 1789 » | Verbalisation FR correcte |
| C6 | Noms propres / mots rares | Prénoms inventés, toponymes (« Franfrelou ») | Prononciation, faux positifs de validation |
| C7 | Élisions / liaisons | « S'écria Flo », « qu'il aille », « les_oiseaux » | Naturel + faux positifs transcription |
| C8 | Titre sans ponctuation | « La danse mystérieuse du Kabuki » | Intonation de clôture |
| C9 | Texte long | 5–10 min d'audio cible (≥ 3 000 caractères) | Dérive de durée, stabilité du timbre sur la longueur, limites de payload |
| C10 | Multi-voix | 2–3 registres via `<voice:>` dans le même texte | Cohérence inter-blocs, respect du seuil de mots |
| C11 | Non-régression multilingue | Phrase FR avec emprunts anglais / marque | Accent anglais parasite sur du FR |

Générer **N = 3 à 5 fois** chaque item (seed varié) pour mesurer la **variance**.

### 4.2 Banque de voix de référence standardisée

Fixe pour tous les modèles. Idéalement 6–8 voix :

- **Durées** : au moins un clip court (~6 s), un moyen (~12 s), un long (~25 s) —
  pour mesurer la sensibilité à la longueur (§3.4).
- **Genres** : voix masculines et féminines.
- **Voisement** : au moins une référence « chuchotement de scène » (soufflé mais
  voisé) pour tester le registre chuchoté.
- **Registres émotionnels** : au moins une voix disponible en 3–4 registres
  (normal / narration / joie / colère) pour C10.
- Toutes **nettoyées de façon identique** (ou toutes brutes) — ne pas mélanger.
- Conserver le **débit mesuré hors silences** de chaque référence (sert de
  `chars_per_second` de départ, calibré par voix).

### 4.3 Métriques objectives

Calculées automatiquement, servent à **filtrer et prioriser l'écoute**.

**Fidélité au contenu** (via `faster-whisper small`, `num2words`, sauvetage
phonétique `espeak-ng` — tout *language-agnostic*, alignement de mots seul) :

- `recall` / `precision` mot à mot texte attendu ↔ transcription.
- **Hallucination** : `recall < 0.6` (`kind="recall"`) **ou** digression ajoutée
  (`length_ratio ≥ 1.5` **et** `precision < 0.5`, `kind="extra"`).
- **Répétition non désirée** : run de token ≥ 3, n-gramme bouclé, ratio de
  trigrammes, `avg_logprob` effondré (neutralisée si le texte demandé est
  lui-même répétitif).
- **Troncature de fin** : `trailing_missing_words` — suffixe de mots attendus
  **consécutifs** absents en repartant de la fin de la transcription (seuil bas :
  1 mot). Plus précis qu'un `tail_recall` sur fenêtre large.
- **Sauvetages anti-faux-positifs** (à intégrer, sinon bruit FR massif) :
  - nombres → `num2words` avant comparaison ;
  - suffixe mal transcrit (nom propre coupé par un trait d'union, « Franfrelou »
    → « Franc-Frelou ») → distance de Levenshtein normalisée sur les 1–2 derniers
    mots ;
  - élision / liaison (« s'écria Flo » → « ses cris à flots ») → similarité
    **phonétique** (phonémisation + Levenshtein sur phonèmes, frontières de mot
    ignorées).
- ⚠️ Whisper **complète parfois** le mot final réellement coupé (prior
  linguistique) → la validation par transcription **ne capte pas 100 %** des
  troncatures. Garder un **proxy acoustique** en complément : silence de fin
  (`_trailing_silence_ms`) à **deux seuils** (mou = informatif, sévère =
  anomalie certaine), avec une résolution de mesure (`hop_ms`) plus fine que le
  seuil sévère (sinon le seuil mesure au ras de son propre bruit de
  quantification).

**Durée & budget** :

- écart `durée obtenue` vs `durée cible` (par chunk et global) ;
- taux de chunks `hit_cap` (indicatif seulement, **pas** une pénalité) ;
- **dérive sur texte long** : ratio durée obtenue / cible sur C9 vs sur C1.

**Performance** :

- **RTF** = temps de génération / durée d'audio (à débit égal) ;
- **cold start** (chargement du modèle) ;
- **VRAM** pic ;
- **€ / minute d'audio** (prix GPU RunPod × RTF).

**Stabilité** :

- écart-type de la durée sur les N runs du même item ;
- variance de timbre inter-chunk (à défaut de métrique fiable : note d'écoute).

### 4.4 Métriques subjectives (arbitre final)

- **MOS** (1–5) sur 4 axes séparés : *naturel*, *intelligibilité*, *similarité à
  la voix de référence*, *expressivité / adéquation au registre*.
- **A/B en aveugle** entre modèles sur le même item + même référence.
- **CMOS** vs un enregistrement humain de référence (si disponible).
- Écoute **prioritairement** sur les items flaggés par les métriques objectives,
  + un échantillon aléatoire de non-flaggés (pour mesurer le taux de faux
  négatifs des métriques).
- Panel : au moins 2–3 auditeurs, francophones natifs.

### 4.5 Protocole d'exécution

1. **Isolation** : 1 image Docker + 1 endpoint (ou 1 process local) par modèle.
   Jamais deux modèles chargés sur le même GPU.
2. **Pré-traitement du texte identique** pour tous (§3.9).
3. **Chunker par famille de modèle** — paramétré aussi proche que possible entre
   modèles (même `MAX_WORDS_PER_CHUNK`, mêmes règles de fusion), mais forké si
   les règles de pause diffèrent.
4. **Paramètres** : d'abord les **défauts recommandés** du modèle ; ensuite une
   passe avec `chars_per_second` calibré par voix. Documenter chaque écart.
5. **Seed** fixé et journalisé par run ; N runs par item.
6. **Journalisation** par chunk : catégorie, `cps`, durée cible / obtenue,
   `recall` / `precision` / `trailing_missing_words`, motif d'anomalie,
   transcription brute.
7. **Sortie audio** normalisée de façon identique (peak cible commun) avant
   écoute A/B.
8. Rejouer intégralement le benchmark à chaque changement de version de modèle
   (pas de comparaison croisée entre deux dates).

### 4.6 Grille de scoring (proposition de pondération)

| Axe | Poids | Source |
|---|---|---|
| Fidélité au texte (hallucination + répétition + troncature) | 30 % | Objectif + écoute de vérification |
| Qualité de voix clonée (naturel + similarité + accent FR) | 25 % | MOS / A/B |
| Stabilité (variance durée + qualité sur N runs) | 15 % | Objectif |
| Contrôle de durée (dont dérive texte long) | 10 % | Objectif |
| Expressivité (narration vs dialogue vs court) | 10 % | MOS |
| Coût / perf (RTF, cold start, VRAM, €) | 10 % | Objectif |

**Éliminatoire** (peu importe le score) : boucle de répétition non maîtrisable,
hallucination « conte » récurrente non rattrapable par retry, accent étranger
systématique sur du FR, licence non commerciale si l'usage l'exige.

---

## 5. Checklist de pièges à tester explicitement (par modèle)

- [ ] **Texte long en un seul appel** — le contrôle de durée décroche-t-il ?
      (justifie ou non le chunking)
- [ ] **Référence courte (~6 s)** — perte d'identité ? durée bâclée ?
- [ ] **Référence chuchotée pure** — identité clonable ou non ?
- [ ] **`repetition_penalty < 1.0`** (si le paramètre existe) — boucle de
      répétition ?
- [ ] **Resserrage des paramètres texte / continuation** — troncature du dernier
      mot ?
- [ ] **Température audio élevée** — instabilité de longueur entre deux runs
      (même seed → fixer, seed varié → mesurer) ?
- [ ] **Répliques d'1–3 mots** — sur-génération (budget démesuré) ? diction ?
- [ ] **Ponctuation répétée / onomatopées** — coupure au milieu de réplique,
      perte du marqueur de dialogue ?
- [ ] **Titre sans ponctuation finale** — intonation ouverte ?
- [ ] **`<lang:fr>` explicite vs absent** — la langue est-elle pilotée par la
      balise, par un `language_id` global, ou par la référence ?
- [ ] **Clonage cross-lingue FR→EN** — accent français résiduel ?
- [ ] **Champ `instruction` / prompt de style** — effet réel mesurable (RMS,
      écoute) ou nul ?
- [ ] **Micro-phrase isolée dans son propre bloc de voix** — dérive de durée ?
- [ ] **Nombres / heures / dates** — verbalisation FR correcte ?
- [ ] **Forme du tenseur de sortie** — 1D garanti ? risque de duplication de
      chunk ?
- [ ] **`bfloat16` en sortie** — conversion `float32` nécessaire avant encodage ?
- [ ] **Payload de sortie** sur C9 — dépasse-t-il les limites de l'hébergeur
      (voir §6) ?

---

## 6. Infrastructure & contraintes de déploiement (RunPod serverless)

Retour d'expérience directement réutilisable pour héberger les modèles du
benchmark.

- **Cold start** : Chatterbox ~30 s, MOSS 5B ~5 min (chargement des poids depuis
  le volume). Prévoir le polling en conséquence.
- **`/runsync` a un timeout serveur ~90 s** indépendant du timeout client → dès
  qu'un cold start ou une génération longue est possible, utiliser **`/run`
  (async) + polling `GET /status/<id>`**.
- **Limite de payload RunPod** : `/run` ~10 Mo, `/runsync` ~20 Mo (input + output
  cumulés). Au-delà, le job passe `COMPLETED` **sans `output`** (échec
  silencieux). → Vérifier `len(audio_base64)` avant de répondre ; sauvegarder sur
  volume + renvoyer une erreur explicite en cas de dépassement. Sortie de prod :
  **MP3 96 kbps mono 24 kHz**, base64 avec préfixe `data:audio/mp3;base64,`.
  Sur un texte de 5–10 min, prévoir un mécanisme de récupération par tranches.
- **Volume réseau** : toujours **vérifier la taille réelle via l'API** avant un
  upload volumineux (un volume documenté « 30 Go » s'est révélé être 20 Go).
  Cache HF **dédié par modèle** (`/runpod-volume/hf_cache_<modèle>`).
- **Upload des poids / assets** : Pod temporaire + `rsync` SSH, **jamais** en
  payload base64 via le handler. **Vérifier la présence réelle des fichiers**
  après upload (`ls -la`, tailles, symlinks de snapshot) — un checkpoint absent a
  déjà fait tourner un modèle **non entraîné silencieusement** en prod.
- **Après un changement d'image** : un worker déjà chaud ne reprend pas la
  nouvelle image → forcer un cold start en cyclant `workersMax` 0 → 1.
- **Tester les correctifs d'image en local** (`docker run --rm <image> python3 -c
  "import <module>"`) avant de repousser — un aller-retour RunPod coûte plusieurs
  minutes.
- **Nouveau module partagé `runpod/*.py`** → l'ajouter au `COPY` de **tous** les
  Dockerfiles concernés (un oubli a fait crasher tous les workers).
- **Pièges de versions pip** (stack GPU) :
  - `scipy ≥ 1.16` n'a pas de wheel Python 3.10 → `scipy>=1.11.0` ;
  - `torchcodec` requis par `torchaudio.load()` en 2.9+ → installer la **variante
    CPU** PyPI standard (pas `--index-url .../cu128`, qui tire des dépendances
    vidéo GPU inutiles) ;
  - `deepfilternet` importe en dur `torchaudio.backend.common.AudioMetaData`,
    supprimé en torchaudio 2.9+ → cassé silencieusement ;
  - toujours **pinner en `==` exact** et **quoter** les contraintes de version
    dans un `RUN pip install \` multi-lignes (sinon bash interprète `>=` comme une
    redirection → versions flottantes).
- **API GraphQL RunPod** : introspection désactivée ; pour découvrir les champs
  d'une mutation, l'appeler avec `input: {}` (l'erreur liste les champs
  manquants). Toujours passer par `curl` (Cloudflare bloque `urllib`/`requests`
  Python avec un 403). `saveTemplate` / `saveEndpoint` **remplacent tout
  l'objet** → relire la config complète avant de muter.
- **Diag rapide** : `GET https://api.runpod.ai/v2/<endpoint>/health` (REST) donne
  l'état vivant jobs/workers ; `POST .../purge-queue` vide une queue de « poison
  jobs » qui recrashent chaque nouveau worker.

---

## 7. Modèles candidats à évaluer

> ⚠️ Liste indicative. **Vérifier pour chacun** : support réel du français,
> qualité du clonage zero-shot, **licence** (usage commercial), taille / VRAM,
> activité du projet. À confirmer au moment du benchmark — ne pas se fier à cette
> liste seule.

**Déjà en main dans ce projet :**

- **Chatterbox Multilingual TTS** (Resemble AI) — moteur de prod. Léger, clonage
  correct, multilingue.
- **MOSS-TTS-Local-Transformer-v1.5** (OpenMOSS) — 5B, très expressif, piloté par
  durée cible, coûteux.
- **Voxtral-4B-TTS-2603** (Mistral) — test à reprendre via `vllm/vllm-omni`.

**À ajouter (open source, potentiellement FR) :**

- **XTTS-v2** (Coqui) — référence historique du clonage multilingue FR ;
  attention au statut de licence / maintenance (Coqui a fermé).
- **F5-TTS** — clonage zero-shot par flow-matching, FR annoncé.
- **Fish-Speech / OpenAudio** — multilingue, clonage.
- **Parler-TTS** — contrôle du style par description ; FR limité.
- **StyleTTS 2** — très bon naturel EN ; FR à vérifier (fine-tune nécessaire).
- **Piper** — très rapide, CPU-friendly, voix FR pré-entraînées, **pas de
  clonage zero-shot** (bon comme baseline « bas coût »).
- **MeloTTS** — multi-langues dont FR, rapide, pas de clonage.
- **Bark** — expressif mais instable / hallucine, pas de contrôle fin.
- **MetaVoice-1B**, **OuteTTS**, **Zonos**, **Orpheus**, **Kokoro**,
  **Dia** — à cribler selon support FR + clonage + licence.
- **MMS-TTS** (Meta) — couverture linguistique énorme, qualité modeste, pas de
  clonage.

Baselines utiles à inclure quoi qu'il arrive : **Piper** (plancher rapide/CPU) et
un **enregistrement humain** (plafond, pour le CMOS).

---

## 8. Outillage réutilisable déjà présent dans le repo

| Besoin | Fichier | Réutilisable tel quel ? |
|---|---|---|
| Comparaison texte ↔ transcription (recall/precision, troncature, sauvetages ortho + phonétique, `num2words`) | `runpod/transcription_check.py` | **Oui** — cœur du scoring objectif, *language-agnostic* |
| Transcription d'un chunk + comparaison (CLI par chapitre/id) | `moss_tts_test/verify_transcription.py` | Oui (réexporte `transcription_check`) |
| Audit de masse d'un corpus déjà généré → rapport JSON | `moss_tts_test/audit_transcription_all.py` | Oui, comme modèle |
| Pipeline de génération livre (chunk + retry anti-hallucination + manifests) | `moss_tts_test/book_pipeline.py` | Comme référence d'architecture |
| Assemblage narration + sons ponctuels + musique + sélection LLM | `runpod/audio_mixing.py` | **Oui** — générique, indépendant du moteur |
| Effets de post-traitement `<fx:nom>` (12 presets, numpy/scipy/librosa) | `runpod/audio_effects.py` | Oui — hors périmètre benchmark mais dispo |
| Chunking (règles de pause/fusion) | `runpod/chatterbox_chunker.py`, `runpod/moss_chunker.py` | Comme base, à forker par famille de modèle |
| Nettoyage voix de référence (cascade SNR-adaptative) | `runpod/reference_audio_cleaner.py`, `runpod/clearvoice_worker.py` | Oui (venv isolé requis pour ClearerVoice) |
| Pré-traitement texte FR (5 étapes ordonnées) | `PIPELINE_TRAITEMENT_SCRIPT_AVANT_API_AVISOL.md` | Spéc à réimplémenter à l'identique pour tous les modèles |
| Détail config / bugs MOSS à ne pas réintroduire | `PLAN_HANDLER_MOSS.md` | Lecture obligatoire avant de retoucher MOSS |
| Notes validation transcription | `docs/validation-tts-moss-whisper.md` | — |

---

## 9. Risques & angles morts connus de la méthode

- **La validation par transcription ne capte pas toutes les troncatures de fin**
  (Whisper « complète » parfois le mot coupé). Toujours croiser avec un proxy
  acoustique + écoute d'un échantillon.
- **Les métriques de durée / budget ne mesurent pas la qualité perçue** (§3.3).
  Risque de sur-pénaliser un modèle « bavard mais bon » ou de sous-pénaliser un
  modèle « pile dans la cible mais tronqué ».
- **Faux positifs de la validation en français** : sans `num2words` + sauvetage
  ortho + sauvetage phonétique, le taux de faux positifs sur les élisions,
  liaisons, noms propres et nombres est massif.
- **Variance** : un seul run par item peut faire passer un modèle instable pour
  bon (ou l'inverse). N ≥ 3 obligatoire.
- **Sensibilité au chunker** : un chunker mal réglé pénalise le modèle, pas le
  chunker. Documenter et figer les réglages ; en cas de doute, tester deux
  réglages.
- **`chars_per_second` par défaut** défavorise les modèles dont le débit réel de
  la voix clonée s'écarte de l'hypothèse — prévoir la passe calibrée par voix.
- **Le cold start MOSS (~5 min)** gonfle le RTF du premier appel — mesurer le RTF
  à chaud, cold start reporté séparément.
- **Accent** : aucune métrique automatique ne le mesure — repose entièrement sur
  l'écoute (panel francophone natif).
