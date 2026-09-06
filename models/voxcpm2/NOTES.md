# VoxCPM2 — notes d'intégration

- **Paquet** : `voxcpm==2.0.3` (PyPI), torch 2.8 cu128 (comme FireRed).
- **API** : `VoxCPM.from_pretrained(<dir>, load_denoiser=False)` puis
  `model.generate(text, prompt_wav_path, prompt_text, reference_wav_path,
  cfg_value=2.0, inference_timesteps=10, seed=<int>)` → np.ndarray **48 kHz**
  (`model.tts_model.sample_rate`). Clonage « Ultimate » = wav + transcription.
- **Pas de tag de langue** (auto-détection depuis le texte).
- `seed` propre au modèle → threadé via `executer_corpus` (sinon 3 reps identiques).

## ⚠️ Bloqueur : RAM de la VM WSL2

Le chargement de VoxCPM2 (funasr + AudioVAE + backbone MiniCPM-4 2B) dépasse
les **8 Go** alloués à la VM WSL2 → `oom-killer`, SIGKILL (exit 137) avant
même le 1er `generate`. Chatterbox / Kokoro / FireRed passent sous 8 Go.

**Correctif (côté Windows)** : éditer `C:\Users\<user>\.wslconfig`
```
[wsl2]
memory=24GB      # au lieu de 8GB (le PC a une 4090 -> largement assez de RAM)
processors=4     # optionnel, accélère les installs / le chargement
```
puis, dans un terminal Windows : `wsl --shutdown` et relancer WSL.

Une fois fait :
```
source env.sh
uv run --python "$TTSB_VENVS/voxcpm2/bin/python" \
    models/voxcpm2/generer.py --reps 3 --voix papa_narration,johnny
```
