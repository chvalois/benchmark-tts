"""Module commun du benchmark — agnostique du modèle TTS.

Ne dépend que de bibliothèques stables (pyyaml, jiwer, num2words,
soundfile/librosa, huggingface_hub). Le code propre à chaque modèle vit
dans `models/<nom>/` avec son venv isolé.
"""
