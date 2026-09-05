# Banque de voix de référence — FIXE et PARTAGÉE

Utilisée **identiquement** par tous les modèles qui font du clonage zero-shot.
Ne **jamais** changer un fichier en cours de release : rejouer tout le
benchmark sinon (protocole §4.5). Référence : APIAVISOL §3.4 et §4.2.

## Format imposé (une fois pour toutes)

| Paramètre | Valeur |
|---|---|
| Conteneur | WAV PCM |
| Échantillonnage | 24 000 Hz |
| Canaux | mono |
| Profondeur | 16 bits |
| Loudness cible | ~ -23 LUFS, pas de clipping |
| Silence tête / queue | < 200 ms |
| Nettoyage | **aucun** pour la v1 (voix brutes, reproductible, pas de dépendance ClearerVoice). Le nettoyage cascade SNR-adaptative est étudié en variante, pas en défaut. |

## Composition cible (6–8 voix)

| id | genre | durée | registre(s) | ce que ça teste |
|---|---|---|---|---|
| `vf_court`      | F | ~6 s  | neutre | sensibilité aux références courtes (§3.4 : perte d'identité, durée bâclée) |
| `vf_moyen`      | F | ~12 s | neutre | référence principale F |
| `vf_long`       | F | ~25 s | narration posée | tenue de l'identité + de la durée sur réf. longue |
| `vh_moyen`      | H | ~12 s | neutre | référence principale H |
| `vh_long`       | H | ~25 s | narration posée | idem, voix masculine |
| `vf_chuchote`   | F | ~12 s | « chuchotement de scène » (soufflé mais **voisé**) | registre chuchoté clonable ou non (§3.4) |
| `vf_multi`      | F | ~12 s × 4 | normal / joie / colère / peur | multi-voix (p27) + expressivité par registre (§3.5) |

> `vf_multi` = 4 fichiers `vf_multi_normal.wav`, `vf_multi_joie.wav`, etc.,
> **même locutrice**, enregistrés dans la foulée.

## Sidecar par voix (`<id>.json`)

```json
{
  "texte_prononce": "…",
  "duree_s": 12.3,
  "debit_cps_hors_silence": 17.4,
  "genre": "F",
  "registre": "neutre",
  "source": "voix perso de Charles / comédien sous contrat / dataset X",
  "consentement": "explicite, écrit, usage benchmark + produit",
  "licence": "…"
}
```

- `debit_cps_hors_silence` = caractères prononcés / (durée − silences).
  Sert de `chars_per_second` de **départ**, calibré ensuite par voix
  (§3.2). Mesuré une fois, stocké ici, jamais deviné.
- **Droits** : n'utiliser que des voix dont l'usage est couvert (voix
  perso, comédien sous contrat, ou dataset à licence compatible avec
  l'usage commercial visé). Le documenter dans `source` + `licence`.

## À produire (hors périmètre Phase 1)

Les fichiers audio eux-mêmes. Cette Phase 1 ne fixe que la **spécification**.
