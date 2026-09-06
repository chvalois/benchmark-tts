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
  **v2** (à venir) = volet long-form / prosodie lourde.

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

- **Personnelles → jamais poussées** (`.gitignore` sur `*.wav`, `*.prompt.txt`).
- v1 : `papa_narration` (27 s, 24 kHz, nettoyée) et `johnny` (21 s, converti
  du 44 kHz stéréo, brut) — délibérément une propre + une « difficile »
  pour mesurer la sensibilité à la qualité de la référence.
- \+ 4 voix d'émotion (`papa_{joie,colere,peur,tristesse}`) pour le run
  émotions : chaque voix ne génère que les phrases de son registre
  (`--voix-phrases`).
- Transcription de chaque référence (`<voix>.prompt.txt`, via
  `whisper-large-v3-french`) — requise par FireRed / VoxCPM / MOSS (clonage
  « ultimate » = audio + transcript).

## 7. Modèles — ce qui est réellement benchmarké

| clé | modèle | checkpoint / code exact | licence |
|---|---|---|---|
| `chatterbox_v3` | Chatterbox Multilingual | poids `ResembleAI/chatterbox@5bb1f6ee` + **code GitHub `@5de7a54a`** (le wheel PyPI ne câble que le T3 v2 ; on force `t3_model="v3"` comme la prod avisol) ; `setuptools<80` (pkg_resources pour resemble-perth) | MIT |
| `kokoro_82m` | Kokoro-82M | `hexgrad/Kokoro-82M@f3ff3571` ; **pas de clonage** → voix interne `ff_siwis` (baseline, non comparable voix-à-voix) | Apache-2.0 |
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
| **UTMOS** | naturel prédit — `tarepan/SpeechMOS` (`utmos22_strong`, torch.hub) ; ~1–5, **entraîné sur MOS EN** → classement relatif | `mesurer_perceptuel.py` |
| **SIM** | similarité locuteur — cosinus embeddings `microsoft/wavlm-base-plus-sv` (généré vs voix de réf) ; proxy (pas le wavlm-large finetuné des papers) | `mesurer_perceptuel.py` |
| **Stabilité** | écart-type + **coefficient de variation** de la durée audio sur les 3 reps ; flag si CV > 15 % | `stabilite.py` |
| **VRAM** | pic pendant la génération (NVML) | `vram.py` |
| **Licence** | registre déclaré + vérifié à la main (`licences.yaml`), **croisé** avec `models.lock` (incohérence = bug) | `mesurer_licence.py` |

Agrégation : `rapport.py` (par modèle : global + WER par
longueur/registre/piège + phrases à écouter en priorité) →
`resultats/<modèle>.{md,json}` ; `comparatif.py` → `resultats/comparatif.md` ;
synthèse éditoriale → `resultats/RESUME.md`.

Le module `benchmark/` est **pur et testé** (~140 tests, ≥ 90 % de
couverture ; seuls les runners qui chargent un modèle sont hors mesure).

## 10. Limites assumées de la v1 (à lever)

1. **Aucune écoute** — MOS / A-B en aveugle (Phase 4) obligatoire avant un
   classement « officiel ». Les métriques **priorisent** l'écoute, elles ne
   tranchent pas.
2. **WER brut** — aucun plancher humain soustrait (une vraie voix dans le
   même Whisper fait déjà 2-4 %). → enregistrer les 34 phrases en voix
   humaine.
3. **Passe-1 seulement** — pas de `chars_per_second` par voix ; critique
   pour MOSS (défauts model card = instable, cf. RESUME).
4. **2 voix de référence**, toutes deux masculines.
5. **Artefacts ASR connus** : Whisper écrit « seconde » → « 2nde » (p33),
   « quatre-vingt-onze… » → « 91,3 % » (p15) — gonfle le WER de ces items.
6. Kokoro non comparable voix-à-voix (voix fixe).
