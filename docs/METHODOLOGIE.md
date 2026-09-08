# Méthodologie & choix du benchmark

Récapitulatif des décisions prises. Sources de cadrage :
`BENCHMARK_TTS_OPENSOURCE_FR_APIAVISOL.md` (retour d'expérience avisol) et
`BENCHMARK_TTS_OPENSOURCE_FR_REFLEXIONCLAUDE.md` (architecture).

---

## 1. Périmètre

- **Cas d'usage** : synthèse narrative FR (livre audio, conte, dialogue de
  roman) avec **clonage de voix zero-shot**. Pas de TTS temps réel.
- **Langue** : français exclusivement. Le multilingue n'est évalué que comme
  risque de régression (accent parasite).
- **v1** = phrases annotées + WER FR + licence + vitesse + stabilité.
- **v2** = volet **long-form** (`corpus/longform.yaml`) : narration livre
  audio + **podcast** (solo, dialogue, interview, vulgarisation) +
  **journalisme** (flash desk, reportage, édito, normalisation hostile).
  Mesure la tenue du timbre sur plusieurs minutes, la respiration
  inter-paragraphes et la prosodie de registre. Corpus prêt ; le run
  complet (génération + scoring dérive/timbre) reste à lancer.

## 2. Infrastructure

| Choix | Décision | Pourquoi |
|---|---|---|
| Machine | RTX 4090 (24 Go), WSL2, **un modèle à la fois** | reproductible, pas de contention VRAM |
| Stockage | **tout sur `D:\tts-benchmark-data`** via `env.sh` (HF, uv, pip, venvs, audio) | `C:` n'a que ~45 Go libres ; aucune écriture implicite sur `C:` |
| RAM WSL | portée de 8 → 32 Go (`.wslconfig`) | VoxCPM2 (2B) et MOSS (5B) OOM au chargement sous 8 Go |
| Transfert HF | `HF_HUB_DISABLE_XET=1` (HTTPS classique) | Xet se bloquait sur le montage `/mnt/d` (DrvFs) |
| venv | **un par modèle** (`$TTSB_VENVS/<modèle>`) | stacks `torch` incompatibles (2.6 / 2.8 / 2.9.1 selon modèle) |
| Reproductibilité | `models.lock` : `repo_id` + **révision SHA HF épinglée** + `code_ref` (commit GitHub pour les modèles installés depuis la source) | re-téléchargement bit-à-bit ; `fetch_models.py` refuse une révision non épinglée |

## 3. Corpus (`corpus/phrases.yaml`)

- **34 items annotés**, croisant 3 axes : `longueur` (court/moyen/long) ×
  `registre` (narration + 4 dialogues émotionnels + cours magistral) ×
  `pieges` (liaison, nombre, nom propre, silence/rythme, homographe
  hétérophone, emprunt EN, ponctuation répétée, onomatopée).
- Types spéciaux : `titre` (p24-25, ponctuation finale ajoutée),
  `long_form` (p26), `multi_voix` (p27, balises `<voice:>`).
- **p26 réduit de 75 %** (3293 → 832 car) à ta demande — reste le seul
  item long-form.
- Le corpus est **fixe pour une release** : toute modification impose de
  rejouer l'intégralité.
- Non fait : sous-ensemble **Fharvard** (phonétiquement équilibré,
  CC BY-NC-ND) prévu pour la crédibilité.

### 3 bis. Corpus long-form v2 (`corpus/longform.yaml`)

- **12 textes multi-paragraphes**, 60–110 s cible, 3 familles :
  `narration_livre` (lf01-04), **podcast** `podcast_solo` /
  `podcast_dialogue` / `interview_reponse` / `vulgarisation` (lf05-08),
  **journalisme** `journalisme_flash` / `journalisme_reportage` / `edito`
  (lf09-12).
- Annotés par `traits` (16 valeurs) : `tenue_timbre`,
  `respiration_paragraphe`, `sigle`, `date_heure`, `nombre_complexe`,
  `nom_propre_dense`, `discours_rapporte`, `enumeration`,
  `question_rhetorique`, `incise`, `anglicisme`, `disfluence`,
  `ponctuation_dialogue`, `ironie`, `terminologie`, `bascule_registre`.
- **100 % original et fictif** (`fictif: true`, imposé par le validateur) :
  organismes / lieux / personnes inventés (univers Grismouton / Kernide /
  Mérindol). Les sigles réels (INSEE, BCE, CAC 40…) ne servent que de test
  de normalisation ; les chiffres associés sont inventés. Rien n'imite du
  journalisme réel.
- Chargé par `charger_longform()` → `TexteLong` (immuable, compatible
  `executer_corpus` et le scoring : `registre` = `genre`, `longueur` =
  `"long"`, `pieges` = `traits`).

## 4. Pré-traitement du texte (`benchmark/pretraitement.py`)

Les **6 étapes §3.9** d'avisol, appliquées **à l'identique** à tous les
modèles (comparer à conditions égales) :
retrait structure markdown · virgule d'incise avant verbe de parole ·
`...`/`…` → `.` · désamorçage des `!` dans les onomatopées `*…*` · saut de
ligne en fin de phrase (hors abréviations) · suppression des émojis.
\+ ponctuation finale sur les items `type: titre` (§3.1).

Les nombres **ne sont pas** développés en toutes lettres à l'entrée du
modèle : c'est le TN de chaque modèle qui est testé (p30). Le
`num2words` n'intervient que côté comparaison ASR.

## 5. Découpage (`benchmark/chunking.py`)

- Fusion des phrases en blocs jusqu'à une **borne dure** (mots ET
  caractères), coupure sur saut de paragraphe et bascule
  narration↔dialogue. Silences de fin de chunk = silence pur ajouté
  **après** génération (jamais envoyé au modèle).
- **Paramètres par famille** : `FAMILLE_CHATTERBOX` (160 car max — avisol :
  200 car → crash CUDA du flow model) ; `FAMILLE_DEFAUT` (60 mots / 400 car)
  pour les 4 autres.

## 6. Voix de référence (`corpus/voix_reference/`)

**Voix personnelles → jamais poussées** (`.gitignore` sur `*.wav`,
`*.prompt.txt`) ; **aucun nom n'apparaît dans les résultats ni sur le
site** — uniquement des descripteurs. Elles restent identiques d'une passe
à l'autre.

- **6 voix de narration** : une voix propre (H, ~27 s, 24 kHz) ; une voix
  « difficile » (H, source brute convertie 44 kHz stéréo) ; une voix
  féminine ; deux voix âgées (H et F) ; une voix à accent régional
  (Sud-Ouest). Choix délibéré pour mesurer la sensibilité à la référence.
- **4 registres émotionnels** (joie / colère / peur / tristesse, même
  locuteur H) pour le run émotions : chaque registre ne génère que les
  phrases de dialogue correspondantes (`--voix-phrases`). Couvert par
  **6 modèles** (FireRed, VoxCPM2, Chatterbox, MOSS, CosyVoice3, XTTS-v2 ;
  Kokoro exclu — voix interne). Résultats : `resultats/EMOTIONS.md`.
- Transcription de chaque référence (`<voix>.prompt.txt`, via
  `whisper-large-v3-french`) — requise par FireRed / VoxCPM / MOSS (clonage
  « ultimate » = audio + transcript).

## 7. Modèles — ce qui est réellement benchmarké

| clé | modèle | checkpoint / code exact | licence |
|---|---|---|---|
| `chatterbox_v3` | Chatterbox Multilingual | poids `ResembleAI/chatterbox@5bb1f6ee` + **code GitHub `@5de7a54a`** (le wheel PyPI ne câble que le T3 v2 ; on force `t3_model="v3"` comme la prod avisol) ; `setuptools<80` (pkg_resources pour resemble-perth) | MIT |
| `kokoro_82m` | Kokoro-82M | `hexgrad/Kokoro-82M@f3ff3571` ; **pas de clonage** → voix interne fixe du modèle (baseline, non comparable voix-à-voix) | Apache-2.0 |
| `firered_tts3` | FireRedTTS3 (base) | poids `@dcf1bdcd` + code `FireRedTeam/FireRedTTS3@1d32ba78` ; `flash-attn==2.8.3` **obligatoire** (redae code `flash_attention_2` en dur) | Apache-2.0 |
| `voxcpm2` | VoxCPM2 (2B) | `voxcpm==2.0.3`, poids `openbmb/VoxCPM2@32279eff`, `load_denoiser=False`, 48 kHz | Apache-2.0 |
| `moss_tts_local_v15` | MOSS-TTS-Local-Transformer-v1.5 (5B) | poids `@be7766a6` + tokenizer audio `MOSS-Audio-Tokenizer-v2` (~8 Go, implicite) + code `OpenMOSS/MOSS-TTS@fb6e6a5` ; **défauts du model card** (`audio_temperature=1.7`), **PAS le handler avisol calibré** | Apache-2.0 |
| `xtts_v2` | XTTS-v2 (Coqui) | `coqui-tts` (fork) + `transformers` 4.57.x (5.x casse le fork) ; clonage audio-only ; **clip 12 s** | **CPML — non commercial** |
| `cosyvoice3_05b` | CosyVoice3-0.5B | code `FunAudioLLM/CosyVoice@074ca6d` + submodule Matcha-TTS via PYTHONPATH ; `inference_zero_shot` ; prompt = `You are a helpful assistant.<|endofprompt|>` + transcript (clip 16 kHz 12 s) ; deps lean + `setuptools<80` + `pyarrow` | Apache-2.0 |
| `f5_tts` | F5-TTS | `f5-tts`, `F5TTS_v1_Base` = **EN/ZH uniquement** → **FR non supporté** (WER > 100 %), sorti du classement | CC-BY-NC |

**Bloqué** : `pocket_tts` (Kyutai) — poids voice-cloning + voix catalogue
derrière l'acceptation explicite des conditions sur
huggingface.co/kyutai/pocket-tts (le HF_TOKEN seul ne suffit pas).
**Non tentés** : `audio8_06b`, `parler_tts_fr`. Baseline CPU `Piper` :
envisagée, non faite.

**Paramètres de génération** = passe-1 = **défauts recommandés du modèle**
(documentés dans chaque `meta.json`). `exaggeration` dynamique pour
Chatterbox (0,3 narration / 0,9 dialogue) = seule exception, c'est une
capacité native du modèle. Passe-2 (`chars_per_second` calibré par voix,
température MOSS abaissée…) **non faite**.

## 8. Protocole d'exécution

- **3 répétitions** par (phrase, voix) — mesure la variance.
- **Seed** = `base_seed + rep`, posé sur `random`/`numpy`/`torch`
  (`fixer_seed`) ET passé aux modèles qui ont leur propre graine (FireRed ;
  VoxCPM/MOSS n'en exposent pas → variance via graine globale).
- `multi_voix` (p27) → **`n/a`**, jamais `echec`, pour les modèles à voix de
  référence unique.
- **Cold start** mesuré et reporté à part ; **warm-up** non chronométré
  (1ʳᵉ génération = compilation kernels / torch.compile).
- Sortie : `$TTSB_AUDIO_OUT/<modèle>/<voix>/<id>_<rep>.wav`, **24 kHz mono
  16 bit** (rééchantillonnage depuis le SR du modèle), tenseur garanti 1D
  (garde canal 0 — jamais `reshape(-1)`, cf. bug §3.10 « chunk joué deux
  fois »). \+ `timings.csv` + `meta.json` par voix.

## 9. Scoring (`benchmark/`)

| Axe | Comment | Fichier |
|---|---|---|
| **WER FR** | transcription `bofenghuang/whisper-large-v3-french` (révision épinglée), `jiwer`, **normalisation identique ref/hyp** (retrait balises, `num2words`) | `transcrire.py` + `mesurer_wer.py` |
| **Fidélité** *language-agnostic* | portage de `avisol/transcription_check.py` : recall/precision mot-à-mot, hallucination (recall < 0,6 ou digression), répétition (run / n-gramme / ratio trigrammes), **troncature de fin** (`trailing_missing_words`) ; sauvetages anti-faux-positifs **orthographique** (Levenshtein suffixe) puis **phonétique** (espeak-ng) | `fidelite.py` + `evaluer.py` |
| **Vitesse** | RTF = `gen_s / audio_s` (à chaud), TTFA, cold start séparé | `mesurer_vitesse.py` |
| **SIM** | similarité locuteur — cosinus embeddings **ECAPA-TDNN** (`speechbrain/spkrec-ecapa-voxceleb`), **silences rognés** (30 dB) des deux côtés. `wavlm-base-plus-sv` abandonné : cosinus tous ~0,96, aucune discrimination, corrélation nulle avec la note humaine. ECAPA : même-locuteur ~0,75–0,9, écart net entre modèles. Clip < 0,4 s → **pas de score** | `mesurer_perceptuel.py` |
| **Naturalité** | **aucune métrique automatique** — cf. §10.8. Se juge au **test d'écoute** (MOS + A/B, `benchmark/agreger_ecoute.py` → `resultats/ecoute.md`). | *(écoute)* |

> **Pas de naturalité automatique.** Trois métriques essayées et retirées :
> **UTMOS** (`utmos22_strong`, MOS SSL EN) — non calibré FR, les voix de réf
> *humaines* y scoraient 1,5–2,9, *sous* les TTS ; corr. MOS humain −0,12.
> **TTSDS2** (distance distributionnelle vs MLS-French) — **anti-corrélé**,
> Spearman −0,77 : récompense les voix plates/propres qui collent au corpus
> de réf, pénalise celles jugées plus naturelles à l'oreille. **NISQA-TTS**
> (naturalness prédite, modèle 2020 EN) — corr. MOS humain −0,03 (nulle).
> Détail et cause commune : §10.8.
| **Stabilité** | écart-type + **coefficient de variation** de la durée audio sur les 3 reps ; flag si CV > 15 % | `stabilite.py` |
| **VRAM** | pic pendant la génération (NVML) | `vram.py` |
| **Licence** | registre déclaré + vérifié à la main (`licences.yaml`), **croisé** avec `models.lock` (incohérence = bug) | `mesurer_licence.py` |

Agrégation : `rapport.py` (par modèle : global + WER par
longueur/registre/piège + phrases à écouter en priorité) →
`resultats/<modèle>.{md,json}` ; `comparatif.py` → `resultats/comparatif.md` ;
`rapport_emotions.py` → `resultats/EMOTIONS.md` ; synthèse éditoriale →
`resultats/RESUME.md`.

Pages HTML statiques (autonomes, `file://`) : `build_pages.py` →
`site/resultats/{index,objectif,ecoute}.html`. `index.html` = classement
métriques auto (toutes voix confondues, moyenne pondérée par nb de runs,
hors combinaisons au WER > 30 %) **+ le classement à l'écoute** (MOS
« Naturel » + win-rate A/B) qui est l'élément décisif. `objectif.html` =
table triable des métriques auto, toutes voix confondues, détail par
modèle. `ecoute.html` = rendu de `resultats/ecoute.md`. `f5_tts` (FR non
supporté) hors classement. **Aucun nom de voix ni de participant** sur le
site.

Le module `benchmark/` est **pur et testé** (~160 tests ; seuls les runners
qui chargent un modèle sont hors mesure).

## 10. Limites assumées de la v1 (à lever)

1. **Panel d'écoute encore réduit** — le test MOS + A/B en aveugle a tourné
   (n≈120 notes MOS, 6 auditeur·rice·s) et **fournit le classement de
   naturalité**, mais les IC 95 % restent larges (± 0,4–0,6). À élargir :
   plus d'auditeur·rice·s, couverture complète des voix et des phrases.
2. **WER brut** — aucun plancher humain soustrait (une vraie voix dans le
   même Whisper fait déjà 2-4 %). → enregistrer les 34 phrases en voix
   humaine.
3. **Passe-1 seulement** — pas de `chars_per_second` par voix ; critique
   pour MOSS (défauts model card = instable, cf. RESUME).
4. **Voix de référence** : 6 voix (voix propre, voix « difficile » brute,
   féminine, deux âgées, accent régional). Une combinaison (voix âgée ×
   texte) sort du domaine exploitable pour les modèles « audio +
   transcript » (WER > 60 %) — cas isolé, écarté des moyennes. Manque une
   voix d'enfant, une qualité téléphone. Cf. `RESUME.md` § sensibilité voix.
5. **Artefacts ASR connus** : Whisper écrit « seconde » → « 2nde » (p33),
   « quatre-vingt-onze… » → « 91,3 % » (p15) — gonfle le WER de ces items.
6. Kokoro non comparable voix-à-voix (voix fixe).
7. **Long-form v2 non encore joué** — `corpus/longform.yaml` est prêt et
   validé (narration + podcast + journalisme), mais la génération et le
   scoring dédié (dérive de durée vs `duree_cible_s`, tenue du timbre,
   prosodie de registre) restent à lancer.
8. **Naturalité : aucune métrique automatique retenue.** Trois essayées,
   trois échecs sur le français (corrélations mesurées contre les premières
   notes MOS « Naturel » du test d'écoute, n=60) :
   - **UTMOS** (`tarepan/SpeechMOS`, `utmos22_strong` ; MOS SSL entraîné
     VoiceMOS EN) — non calibré FR : les voix de référence *humaines* y
     scoraient **1,5–2,9** (la voix propre = 2,89 ; une voix féminine = 1,56),
     *sous* les sorties TTS. Corr. MOS humain ≈ **−0,12**.
   - **TTSDS2** (Text-to-Speech Distribution Score ; distance
     distributionnelle multi-features gén. vs vraie parole FR, réf.
     MLS-French) — **anti-corrélé** : Spearman ≈ **−0,77** avec le MOS
     humain. Il récompense les modèles plats et propres (Kokoro, XTTS,
     CosyVoice3) qui collent statistiquement au corpus de réf (audiobook
     amateur, prosodie mesurée), et pénalise FireRed / MOSS que l'oreille
     juge plus naturels. Speaker exclu (bench `wespeaker` cassé) ; ce n'est
     pas ce qui explique l'inversion.
   - **NISQA-TTS** (`gabrielmittag/NISQA` ; *Naturalness* prédite par
     énoncé, modèle 2020 EN) — corr. MOS humain ≈ **−0,03** (nulle).

   **Cause commune** : ces métriques sont calibrées sur du MOS anglophone
   et/ou sur « proximité à la vraie parole », notion qui ne discrimine pas
   du TTS FR moderne tous à quasi-parité (bande étroite) — ce que l'oreille
   entend (expressivité, chaleur, micro-prosodie) n'est pas la proximité
   distributionnelle. **UTMOSv2** (successeur 2024, toujours EN/VoiceMOS)
   n'a pas été testé : même biais de fond attendu.

   → **La naturalité et l'expressivité se classent au test d'écoute**
   (MOS + A/B en aveugle), qui est l'élément décisif du classement — repris
   tel quel sur la page d'accueil du site. WER (intelligibilité) et SIM
   (identité) restent les seules métriques auto ; leur corrélation avec le
   MOS reste faible (r ≈ 0,1–0,2 sur n=120), attendu entre modèles tous
   corrects. Le code TTSDS2 / NISQA a été retiré.
