# Benchmark TTS open source — spécialisé français

## Objectif

Construire un benchmark reproductible de modèles TTS open source, avec un focus
français absent des benchmarks existants (la plupart sont anglophones ou
génériques). Sert de contenu pour une série de posts LinkedIn et de base de
décision technique pour un service B2B de clonage vocal (API TTS français à
faible coût).

Angle différenciant : mesurer sur du matériel réel (RTX 4090), avec un axe
**licence commerciale** en plus de la qualité/vitesse — la plupart des
comparatifs ignorent que les meilleurs modèles (XTTS-v2, F5-TTS) sont en
licence non-commerciale.

## Contraintes matérielles

- GPU : RTX 4090 (24 Go VRAM) — aucune contrainte mémoire attendue sur les
  modèles candidats ci-dessous.

## Architecture générale

```
tts-benchmark/
├── models/
│   ├── fish_speech/          # venv dédié + script de génération
│   ├── chatterbox/           # venv dédié + script de génération
│   ├── xtts_v2/              # venv dédié + script de génération
│   ├── f5_tts/                # venv dédié + script de génération
│   ├── kokoro/                # venv dédié + script de génération
│   └── parler_tts_french/     # venv dédié + script de génération
├── corpus/
│   ├── phrases.yaml            # textes de référence, fixes, partagés
│   └── voix_reference/         # échantillons voix de clonage, fixes, partagés
├── audio_genere/
│   └── <nom_modele>/<id_phrase>_<repetition>.wav
├── benchmark/                  # module commun, agnostique du modèle
│   ├── generer_lot.py          # orchestre la génération pour un modèle donné
│   ├── mesurer_vitesse.py      # TTFA, RTFx
│   ├── mesurer_wer.py          # script déjà écrit (voir plus bas)
│   ├── mesurer_licence.py      # vérifie/documente la licence de chaque modèle
│   └── rapport.py              # agrège tout en un tableau final
└── resultats/
    └── rapport_final.csv / .md
```

### Pourquoi un venv par modèle

Chaque modèle TTS a des dépendances (versions de `torch`, `transformers`,
`numpy`...) souvent incompatibles entre elles. Un venv isolé par modèle évite
les conflits ; le module commun, lui, ne dépend que de bibliothèques stables
(`pyyaml`, `jiwer`, `torch`+`transformers` pour l'ASR, `csv`) et tourne dans
son propre environnement, séparé de ceux des modèles.

### Le module commun (benchmark/)

Rôle : une fois qu'un modèle a généré ses fichiers audio dans
`audio_genere/<nom_modele>/`, le module commun s'applique **identiquement** à
tous les modèles, sans rien connaître de leurs spécificités internes.

Trois axes mesurés, plus la licence en donnée fixe :

1. **Vitesse** (`mesurer_vitesse.py`) : temps au premier audio (TTFA) et
   RTFx (temps réel de génération / durée de l'audio produit), mesurés sur
   la RTX 4090, à partir de logs de timestamps que chaque script de
   génération doit produire (voir contrat d'interface plus bas).
2. **Scores objectifs** (`mesurer_wer.py`) : script déjà écrit et fonctionnel
   (voir section suivante), calcule le WER français via
   `bofenghuang/whisper-large-v3-french`, avec détail
   substitutions/suppressions/insertions et plancher d'erreur calibré sur
   voix humaine.
3. **Écoute** : pas de script — page HTML statique simple qui liste les
   fichiers audio générés côte à côte par phrase, pour comparaison à l'oreille
   (inspiration : 5uck1ess/tts-bench).
4. **Licence** (`mesurer_licence.py`) : fichier de config fixe listant pour
   chaque modèle sa licence et si elle autorise un usage commercial. Pas une
   mesure automatique, une donnée déclarée et vérifiée manuellement une fois.

### Contrat d'interface entre un modèle et le module commun

Chaque script `models/<nom_modele>/generer.py` doit :

- Lire les phrases depuis `corpus/phrases.yaml` (jamais de texte en dur dans
  le script du modèle — un seul corpus partagé, modifiable à un seul endroit).
- Lire la voix de référence depuis `corpus/voix_reference/` pour les modèles
  qui font du clonage (jamais un échantillon différent par modèle).
- Générer chaque phrase **N fois** (répétitions, ex. 3 à 5, configurable),
  nommées `<id_phrase>_<numero_repetition>.wav`, dans
  `audio_genere/<nom_modele>/`.
- Écrire un fichier `audio_genere/<nom_modele>/timings.csv` avec au minimum :
  `id_phrase, repetition, ttfa_secondes, duree_generation_secondes, duree_audio_secondes`.

Ce contrat est ce qui permet au module commun de rester complètement
indépendant du code de chaque modèle.

## Corpus de textes (fixe, partagé — `corpus/phrases.yaml`)

Le corpus croise trois dimensions et doit être annoté en conséquence (pas de
simple liste de textes bruts, chaque phrase porte ses métadonnées pour
permettre une analyse du WER par catégorie ensuite) :

- **Longueur** : `court` (5-8 mots), `moyen` (15-25 mots), `long` (30+ mots
  ou plusieurs phrases enchaînées) — les modèles de synthèse se comportent
  différemment sur la durée (dérive de prosodie, essoufflement de la voix).
- **Registre** : `narration`, `dialogue_joie`, `dialogue_colere`,
  `dialogue_peur`, `dialogue_tristesse`, `cours_magistral` — teste la
  capacité du modèle à moduler l'intonation, pas juste à prononcer juste.
- **Pièges phonétiques** : `liaison`, `nombre`, `nom_propre`,
  `silence_rythme`, `homographe_heterophone` — un même mot qui se prononce
  différemment selon son sens (ex. "fils" = /fis/ pour "le fils du
  boulanger" mais /fil/ pour "les fils de laine") est un piège
  particulièrement révélateur : un modèle qui ne désambiguïse pas le sens
  contextuel prononce mal l'un des deux.

Format (`corpus/phrases.yaml`) :

```yaml
p01:
  texte: "On a gagné, c'est incroyable !"
  longueur: court
  registre: dialogue_joie
  pieges: []

p02:
  texte: "Non, mais ça suffit maintenant !"
  longueur: court
  registre: dialogue_colere
  pieges: []

p03:
  texte: "Il y a quelqu'un... j'ai entendu du bruit."
  longueur: court
  registre: dialogue_peur
  pieges: [silence_rythme]

p04:
  texte: "Il me manque, chaque jour un peu plus."
  longueur: court
  registre: dialogue_tristesse
  pieges: [homographe_heterophone]   # "plus" : négation vs comparatif

p05:
  texte: "Considérons à présent l'équation suivante."
  longueur: court
  registre: cours_magistral
  pieges: [liaison]

p06:
  texte: "Tu te rends compte ? Après tout ce travail, on l'a enfin décroché, ce contrat !"
  longueur: moyen
  registre: dialogue_joie
  pieges: [liaison]

p07:
  texte: "Je t'avais pourtant prévenu cent fois, et tu n'as rien écouté, encore une fois !"
  longueur: moyen
  registre: dialogue_colere
  pieges: [nombre]

p08:
  texte: "Ne bouge pas, surtout ne fais aucun bruit, j'ai vu une ombre bouger près de la porte."
  longueur: moyen
  registre: dialogue_peur
  pieges: [silence_rythme]

p09:
  texte: "Depuis qu'elle est partie, plus rien n'a vraiment de sens, tu sais."
  longueur: moyen
  registre: dialogue_tristesse
  pieges: [homographe_heterophone]   # "est" : verbe être vs point cardinal (cf. p18)

p10:
  texte: "La Révolution française de mille sept cent quatre-vingt-neuf marque une rupture profonde avec l'Ancien Régime."
  longueur: moyen
  registre: cours_magistral
  pieges: [nombre, liaison]

p11:
  texte: "Après des heures de marche, ils atteignirent enfin la crête, essoufflés mais heureux d'avoir vaincu la montagne."
  longueur: moyen
  registre: narration
  pieges: [liaison]

p12:
  texte: "Anne-Sophie Legrand-Dubois a rencontré Grzegorz Wozniak à Aix-en-Provence."
  longueur: moyen
  registre: narration
  pieges: [nom_propre]

p13:
  texte: "Le fils du tisserand ramassa les fils de laine tombés sur le sol, les enroula avec soin, puis rentra chez lui sous une pluie fine qui n'en finissait pas de tomber sur les toits gris du village."
  longueur: long
  registre: narration
  pieges: [homographe_heterophone]   # "fils" (/fis/, le fils) et "fils" (/fil/, les fils de laine) dans la même phrase

p14:
  texte: "Pour comprendre pleinement les mécanismes de la photosynthèse, il convient d'abord de rappeler que les chloroplastes, ces organites présents dans les cellules végétales, captent l'énergie lumineuse afin de la convertir en énergie chimique utilisable par la plante."
  longueur: long
  registre: cours_magistral
  pieges: [liaison, silence_rythme]

p15:
  texte: "Quatre-vingt-onze virgule trois pour cent des participants ont répondu par l'affirmative, un chiffre en nette hausse par rapport à l'année précédente où seulement soixante-quatorze pour cent s'étaient prononcés dans ce sens."
  longueur: long
  registre: cours_magistral
  pieges: [nombre]

p16:
  texte: "Il est fier de se fier à son instinct."
  longueur: court
  registre: narration
  pieges: [homographe_heterophone]   # "fier" (/fjɛʁ/, adjectif) vs "se fier" (/fje/, verbe)

p17:
  texte: "Les poules couvent leurs œufs près du couvent abandonné."
  longueur: court
  registre: narration
  pieges: [homographe_heterophone]   # "couvent" verbe (/kuv/) vs "couvent" nom (/kuvɑ̃/)

p18:
  texte: "Le soleil se lève à l'est ; c'est là qu'est notre maison."
  longueur: court
  registre: narration
  pieges: [homographe_heterophone]   # "est" point cardinal (/ɛst/) vs "est"/"qu'est" verbe être (/ɛ/)

p19:
  texte: "Il n'en veut plus, même si j'en ai plus que lui."
  longueur: court
  registre: dialogue_colere
  pieges: [homographe_heterophone]   # "plus" négatif (/ply/) vs "plus" comparatif (/plys/)

p20:
  texte: "Sacha et Amélie habitent au vingt-six rue des Acacias à Bordeaux."
  longueur: moyen
  registre: narration
  pieges: [nombre, nom_propre, liaison]
```

Cette liste n'est pas exhaustive : à compléter au besoin, mais en respectant
la grille (longueur × registre × piège) plutôt qu'en ajoutant des phrases au
hasard, pour que le rapport final puisse croiser le WER par catégorie (ex.
"tel modèle décroche surtout sur les homographes hétérophones" ou "tel
modèle perd en qualité sur les phrases longues").

Pour la crédibilité du benchmark, envisager aussi de piocher un sous-ensemble
de phrases dans un corpus validé scientifiquement plutôt que 100% maison :
le **corpus Fharvard** (700 phrases françaises phonétiquement équilibrées,
usage établi en recherche sur l'intelligibilité de la parole, licence
CC BY-NC-ND — vérifier la compatibilité avec l'usage commercial visé avant
de s'appuyer dessus pour le produit final, pas seulement pour le contenu
éditorial du benchmark).

## Voix de référence (fixe, partagée — `corpus/voix_reference/`)

Un seul échantillon (ou un petit jeu, ex. une voix homme + une voix femme),
utilisé identiquement par tous les modèles qui font du clonage zero-shot.
Format et durée à fixer une fois (ex. WAV 24kHz, 10-15 secondes, phrase
neutre) et ne plus changer pendant toute la durée du benchmark.

## Modèles candidats (venv séparé chacun)

| Modèle | Licence | Rôle attendu dans le classement |
|---|---|---|
| **FireRedTTS3-Instruct** | Apache 2.0 | priorité n°1 — 24 langues dont FR, clonage zero-shot, contrôle émotionnel par NL, meilleurs scores WER/SIM publiés (source : veille sept. 2026) |
| **VoxCPM2** (OpenBMB) | Apache 2.0 | candidat de référence depuis juin 2026 — Voice Design, Controllable Cloning, NL style guidance ; à valider empiriquement en français (guidance surtout démontrée en anglais) |
| **Chatterbox V3 Multilingual** (Resemble AI) | MIT | baseline stable actuelle de Charles, référence de comparaison |
| **Pocket TTS** (Kyutai) | CC-BY-4.0 | candidat "faible coût" — 100M paramètres, CPU natif, ~200ms latence, FR natif (voix "estelle") ; émotion par clonage uniquement |
| **CosyVoice3** (Fun-CosyVoice3-0.5B) | Apache 2.0 | candidat de backup stable, FR inclus, pas de progression récente mais fiable |
| **Audio8 TTS Preview 0.6B** | Apache 2.0 | candidat léger/rapide, bon WER, FR correct ; pas de tags d'émotion |
| Kokoro-82M | Apache 2.0 | référence légèreté/vitesse, support français à vérifier |
| Parler-TTS French | libre (base HF) | seul entraîné nativement français, pas de clonage zero-shot |

### Modèles écartés (référence qualité uniquement, non retenus pour le service)

| Modèle | Licence | Raison de l'exclusion |
|---|---|---|
| XTTS-v2 (Coqui) | CPML, non-commercial | référence qualité, licence bloquante |
| F5-TTS | CC-BY-NC, non-commercial | référence prosodie, licence bloquante |
| Fish Speech / fish-speech | CC-BY-NC-SA-4.0 (Research License) | **correction** : classé par erreur "Apache 2.0" dans une version précédente de cette spec ; la veille de Charles confirme la licence non-commerciale, inchangée depuis mars 2026, interdiction du commercial sans accord écrit séparé |
| OmniVoice (k2-fsa) | code Apache 2.0, **poids CC-BY-NC** | le finetune qui porte l'émotion (ModelsLab/omnivoice-singing) reste non-commercial malgré le code libre — même situation que XTTS-v2/F5-TTS |
| Higgs Audio v3 (Boson AI) | Research and Non-Commercial + Creator Use Grant | le Creator Use Grant autorise les créateurs individuels (Pagelio, Mejrev) avec acknowledgement, jamais un usage B2B/SaaS qui expose le modèle à des tiers — hors périmètre de ce benchmark |

### Hors périmètre (pas de français ou abandonnés, d'après la veille de Charles)

Qwen3-TTS (gelé depuis mars 2026, FR insuffisant), MOSS-TTS (gelé, aucune évolution émotion FR depuis mai), AudarAI (Arabic-first, pas de FR), IndexTTS-2.5 (pas de FR : ZH/EN/JA/ES/AR), VibeVoice branche principale (EN/ZH only ; VibeVoice-Realtime-0.5B a le FR mais expressivité jugée faible), Voxtral TTS (Mistral, CC-BY-NC, API uniquement).

## Script WER déjà écrit (à adapter au nouveau corpus)

`benchmark/mesurer_wer.py` part du script déjà fourni (`wer_benchmark.py`) :
ASR `bofenghuang/whisper-large-v3-french`, normalisation identique
référence/hypothèse, calcul via `jiwer` (substitutions/suppressions/
insertions), plancher d'erreur calibré sur `corpus/voix_reference/`
enregistré en vraie voix humaine, moyenne + écart type sur les répétitions.

Point d'adaptation : le corpus est maintenant structuré (`texte`, `longueur`,
`registre`, `pieges` par phrase, voir section précédente) et non plus un
simple `id: texte`. Le script doit lire `corpus/phrases.yaml` sous ce format
et propager les métadonnées jusqu'au rapport final, pour permettre un
découpage du WER par longueur, par registre et par type de piège — pas
seulement une moyenne globale par modèle.

## Livrable final (`benchmark/rapport.py`)

Deux niveaux de tableau :

1. **Vue globale** : un tableau récapitulatif par modèle (WER moyen, TTFA
   moyen, RTFx moyen, licence, colonne "verdict usage commercial"
   oui/non selon la licence). Format CSV + rendu Markdown pour publication
   directe.
2. **Vue par catégorie** : le même WER moyen, mais éclaté par `longueur`,
   par `registre` et par type de `piege` (croisement avec les métadonnées
   du corpus). C'est cette vue qui distingue un modèle "bon en moyenne mais
   qui s'effondre sur les phrases longues" d'un modèle réellement homogène —
   l'angle le plus utile pour le contenu éditorial et pour le module de
   conseil final.

## Module de conseil (à construire après le benchmark, hors périmètre immédiat)

Petit arbre de décision (3 questions : infra disponible, contrainte
dominante prix/vitesse/qualité, usage commercial ou non) qui pointe vers un
des modèles du tableau. Alimenté par les résultats de `rapport.py`, pas par
des seuils inventés à la main.
