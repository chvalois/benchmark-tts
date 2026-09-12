# exports/ — retours du test d'écoute

Dépose ici les fichiers `ecoute_<prénom>_<mode>.json` exportés par la page
`site/ecoute/` (bouton « Exporter mes résultats »).

- **Un seul fichier par (auditeur × mode)** : l'export contient *tout*
  l'historique cumulé de cet auditeur pour ce mode (toutes ses séries).
  Un nouvel export du même auditeur **remplace** l'ancien — garde le plus
  récent.
- Les séries sont **cumulatives et sans répétition** : chaque série de 20
  porte sur des items pas encore notés. L'auditeur enchaîne des séries
  courtes ; sa couverture monte.
- Les `id` d'items sont des hachages de contenu, et `build_ecoute.py`
  archive chaque solution (`site/ecoute/_solutions/`) : `agreger_ecoute.py`
  les fusionne → un export reste exploitable même après un changement de
  pool.
- Les `.json` sont **git-ignorés** (données d'auditeurs) ; ce README reste versionné.

## Dépouiller

```bash
source env.sh
python3 benchmark/agreger_ecoute.py           # lit tout exports/*.json
python3 benchmark/build_pages.py              # -> site/resultats/ecoute.html
# ou un sous-ensemble :
python3 benchmark/agreger_ecoute.py exports/ecoute_charles_ab.json exports/ecoute_marie_ab.json
```

Régénère **`resultats/ecoute.md`** à chaque exécution, en agrégeant **tous**
les fichiers fournis :

| mode | ce qui sort |
|---|---|
| A/B | win-rate par modèle (victoires + ½ nuls), **matrice des duels**, défauts attribués au bon modèle |
| MOS | moyenne ± IC 95 % par axe + corrélation avec les métriques auto (UTMOS, 1−WER, SIM) |
| Émotion | taux de transfert par (modèle, émotion) et global |

Ce n'est pas temps réel : c'est une commande à relancer quand tu ajoutes
des exports. La matrice n'est pas « incrémentale » au sens où elle se
mettrait à jour toute seule — elle est **recalculée** sur l'ensemble du
dossier à chaque appel.
