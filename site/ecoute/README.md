# Test d'écoute local (`site/ecoute/`)

Page statique **sans serveur** (`file://`), vanilla JS, aveugle. Les
métriques auto (WER, SIM) couvrent l'intelligibilité et l'identité ; **la
naturalité n'a aucune métrique auto fiable en français** (UTMOS, TTSDS2,
NISQA tous écartés — `docs/METHODOLOGIE.md` §10). Ce test produit le
verdict de naturalité / préférence.

## Générer / régénérer

```bash
source env.sh
python3 benchmark/build_ecoute.py
```

Produit (tous trois **git-ignorés** — voix perso + artefacts régénérables) :

| fichier | contenu |
|---|---|
| `audio/cXXXX.wav` | clips **anonymisés** (aucun nom de modèle dans le nom) |
| `manifest.js` | données de la page — **jamais** de nom de modèle |
| `solution.js` | mapping id → modèle(s), chargé **uniquement** par le bouton « 👁 modèles » (déblinde le test — vérification locale) |
| `_solution.json` | mapping complet (clips + build), pour le dépouillement |

Le bouton **« 👁 modèles »** (barre du bas) affiche, pour l'item courant,
quels modèles sont derrière A / B (ou le modèle noté en MOS). Désactivé si
`solution.js` absent. À n'utiliser que pour vérifier — il casse l'aveugle.

## Plusieurs voix de référence

A/B et MOS couvrent **6 voix** (`VOIX_ECOUTE`) : `papa_narration`,
`aurore2_narration` (femme), `tonton_marc_narration` (accent Sud-Ouest),
`papy_narration` (voix âgée), `johnny` (réf brute), `manou_narration`
(femme âgée, conte). Chaque item affiche sa voix ; en MOS le bouton
« voix de référence » joue la bonne `ref_<voix>.wav`. Les combos
(modèle, voix) au WER > `WER_MAX_ECOUTE` (30 % — clips cassés, ex.
FireRed/VoxCPM sur `papy`) sont **exclus** du pool. En **MOS**, les
phrases de registre émotionnel sont notées sur la voix `papa_<émotion>`
uniquement (pas de rendu neutre). Le mode ÉMOTION reste sur les voix
`papa_*`.

## Sessions courtes, phrases tournantes

`build_ecoute.py` construit des **pools** larges — **toutes** les 34 phrases
du corpus (hors `multi_voix`) × 6 voix (~430 paires A/B, ~280 clips MOS,
~36 paires émotion). À chaque session la page tire **au hasard ≤ 20 items**
(`limite_session`), graine `pseudo + mode + nonce` → **sous-ensemble
différent (phrases ET voix) à chaque nouvelle session**. Refais-en
plusieurs pour couvrir le corpus.

En **MOS**, les phrases de registre émotionnel (joie / colère / peur /
tristesse) ne sont notées que sur des clips clonés depuis la **voix de réf
émotionnelle** correspondante (`papa_<émotion>`), jamais depuis une voix de
narration neutre.

Les `id` des items sont des **hachages du contenu** (voix + phrase +
modèles) : stables d'un `build_ecoute.py` à l'autre → un ajustement du pool
n'invalide **pas** les exports déjà collectés pour les items conservés.

Reprise : même mode → *OK* reprend la session en cours, *Annuler* en
relance une neuve (autres phrases). L'export ne contient **que les items
vus**. Rien n'est envoyé.

## Les trois modes

| mode | question | contenu |
|---|---|---|
| **A/B préférence** | « lequel est le meilleur globalement » (naturel + intelligibilité + ressemblance) | 2 têtes (`voxcpm2`, `firered_tts3`) plus exposées, tous les couples visés + paires aléatoires ; défauts cochables **par côté** (A et B séparément) |
| **MOS 1–5** | note sur 4 axes (naturel, intelligibilité, similarité, expressivité) | 2 modèles tournants par phrase ; curseurs à **3 par défaut** (note retenue, ajustable) ; bouton « voix de référence » pour l'axe similarité |
| **A/B émotion** | « lequel rend le mieux l'émotion \<X\> ? » (A / équivalent / B) | **modèle A vs modèle B**, tous deux clonés depuis la **même** voix de réf émotionnelle (`papa_joie/colere/peur/tristesse`) → compare les modèles sur leur rendu émotionnel |

**Kokoro est exclu du test** (A/B, MOS, émotion) : voix interne fixe, non
comparable voix-à-voix — sa qualité reste couverte par WER + SIM et le
comparatif automatique.

## Dépouiller

Dépose les exports dans `exports/` puis :

```bash
python3 benchmark/agreger_ecoute.py            # lit tout exports/*.json
```

Régénère `resultats/ecoute.md` **à chaque appel**, sur l'ensemble des
fichiers fournis (plusieurs auditeurs / sessions s'additionnent). Ce n'est
pas temps réel : c'est une commande à relancer.

- **A/B** : win-rate par modèle (victoires + ½ nuls), matrice des duels,
  défauts attribués au bon modèle.
- **MOS** : moyenne ± IC 95 % par axe + corrélations MOS ↔ métrique auto
  (intelligibilité↔(1−WER), similarité↔SIM ; le **naturel** n'a pas de
  contrepartie auto).
- **Émotion** : taux de transfert par (modèle, émotion) et global.

Puis `python3 benchmark/build_pages.py` → **`site/resultats/ecoute.html`**
(rendu lisible). Voir aussi `exports/README.md` et `site/resultats/README.md`.
