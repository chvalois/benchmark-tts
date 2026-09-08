#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# rescore_naturalite.sh — passe TTSDS2 + NISQA sur tout l'audio généré,
# puis régénère les rapports.
#
#   source env.sh
#   bash benchmark/rescore_naturalite.sh              # reprend là où ça s'est arrêté
#   bash benchmark/rescore_naturalite.sh --force      # recalcule tout
#   bash benchmark/rescore_naturalite.sh --only firered_tts3,voxcpm2
#
# Pour chaque $TTSB_AUDIO_OUT/<modèle>/<voix>/ contenant des <id>_<rep>.wav :
#   - NISQA  (venv _nisqa)  -> <voix>/nisqa.csv        [tous les dossiers]
#   - TTSDS2 (venv _ttsds2) -> <voix>/ttsds2.json      [>= MIN_WAV_TTSDS2 wav]
# puis rapport.py par modèle, comparatif.py, rapport_emotions.py.
#
# Idempotent : un dossier déjà scoré est sauté (sauf --force). Continue sur
# erreur (chaque échec est loggué et compté).
# ---------------------------------------------------------------------------
set -uo pipefail

MIN_WAV_TTSDS2=30          # en dessous, la distance distributionnelle n'a pas de sens

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RACINE"

: "${TTSB_VENVS:?sourcer env.sh en premier}"
: "${TTSB_AUDIO_OUT:?sourcer env.sh en premier}"
: "${TTSB_ROOT:?sourcer env.sh en premier}"

FORCE=0
ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --force) FORCE=1 ;;
    --only)  ONLY="$2"; shift ;;
    *) echo "argument inconnu : $1" >&2; exit 2 ;;
  esac
  shift
done

PY_NISQA="$TTSB_VENVS/_nisqa/bin/python"
PY_TTSDS2="$TTSB_VENVS/_ttsds2/bin/python"
PY_COMMUN="$TTSB_VENVS/_commun/bin/python"
for p in "$PY_NISQA" "$PY_TTSDS2" "$PY_COMMUN"; do
  [ -x "$p" ] || { echo "venv manquant : $p" >&2; exit 1; }
done

TS="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="$TTSB_ROOT/logs/rescore_naturalite_$TS"
mkdir -p "$LOG_DIR"
export TTSDS_CACHE_DIR="${TTSDS_CACHE_DIR:-$TTSB_ROOT/ttsds-cache}"
export PYTHONPATH="$RACINE"

echo "[rescore] logs -> $LOG_DIR"
echo "[rescore] force=$FORCE  only='${ONLY:-tous}'  min_wav_ttsds2=$MIN_WAV_TTSDS2"

# -- inventaire ------------------------------------------------------------
mapfile -t VOIX_DIRS < <(
  for md in "$TTSB_AUDIO_OUT"/*/; do
    mn="$(basename "$md")"
    if [ -n "$ONLY" ] && [[ ",$ONLY," != *",$mn,"* ]]; then continue; fi
    for vd in "$md"*/; do
      [ -d "$vd" ] || continue
      n=$(find "$vd" -maxdepth 1 -name '*_*.wav' | grep -cE '_[0-9]+\.wav$' || true)
      [ "${n:-0}" -ge 1 ] && echo "$n|$vd"
    done
  done
)
N=${#VOIX_DIRS[@]}
echo "[rescore] $N dossiers voix à traiter"
[ "$N" -gt 0 ] || { echo "[rescore] rien à faire"; exit 0; }

fails=0
t0=$(date +%s)
i=0
for entry in "${VOIX_DIRS[@]}"; do
  i=$((i + 1))
  n_wav="${entry%%|*}"
  vd="${entry#*|}"
  vd="${vd%/}"
  tag="$(basename "$(dirname "$vd")")/$(basename "$vd")"
  slug="${tag//\//__}"
  el=$(( $(date +%s) - t0 ))
  printf '[rescore] [%d/%d] %s (%s wav)  +%dm%02ds\n' "$i" "$N" "$tag" "$n_wav" $((el/60)) $((el%60))

  # --- NISQA ---
  if [ "$FORCE" -eq 1 ] || [ ! -f "$vd/nisqa.csv" ]; then
    if ! "$PY_NISQA" benchmark/mesurer_nisqa.py --audio-dir "$vd" \
         > "$LOG_DIR/${slug}.nisqa.log" 2>&1; then
      echo "  ! NISQA échec ($tag) — cf. $LOG_DIR/${slug}.nisqa.log"
      fails=$((fails + 1))
    fi
  else
    echo "  = NISQA déjà fait"
  fi

  # --- TTSDS2 (seulement si assez de wav) ---
  if [ "$n_wav" -ge "$MIN_WAV_TTSDS2" ]; then
    if [ "$FORCE" -eq 1 ] || [ ! -f "$vd/ttsds2.json" ]; then
      if ! "$PY_TTSDS2" benchmark/mesurer_ttsds2.py --audio-dir "$vd" --device cuda \
           > "$LOG_DIR/${slug}.ttsds2.log" 2>&1; then
        echo "  ! TTSDS2 échec ($tag) — cf. $LOG_DIR/${slug}.ttsds2.log"
        fails=$((fails + 1))
      fi
    else
      echo "  = TTSDS2 déjà fait"
    fi
  else
    echo "  - TTSDS2 sauté ($n_wav < $MIN_WAV_TTSDS2 wav)"
  fi
done

# -- rapports ------------------------------------------------------------
echo "[rescore] rapports par modèle…"
for md in "$TTSB_AUDIO_OUT"/*/; do
  mn="$(basename "$md")"
  if [ -n "$ONLY" ] && [[ ",$ONLY," != *",$mn,"* ]]; then continue; fi
  find "$md" -maxdepth 2 -name transcriptions.csv | grep -q . || continue
  if ! "$PY_COMMUN" benchmark/rapport.py --modele-dir "$md" --out "resultats/$mn" \
       > "$LOG_DIR/rapport.$mn.log" 2>&1; then
    echo "  ! rapport.py échec ($mn) — cf. $LOG_DIR/rapport.$mn.log"
    fails=$((fails + 1))
  fi
done

echo "[rescore] comparatif.py + rapport_emotions.py…"
"$PY_COMMUN" benchmark/comparatif.py resultats/*.json --out resultats/comparatif.md \
  > "$LOG_DIR/comparatif.log" 2>&1 || { echo "  ! comparatif.py échec"; fails=$((fails + 1)); }
"$PY_COMMUN" benchmark/rapport_emotions.py \
  > "$LOG_DIR/rapport_emotions.log" 2>&1 || { echo "  ! rapport_emotions.py échec"; fails=$((fails + 1)); }

el=$(( $(date +%s) - t0 ))
echo "[rescore] terminé en ${el}s ($((el/60))m) — $fails échec(s). Logs : $LOG_DIR"
exit $(( fails > 0 ? 1 : 0 ))
