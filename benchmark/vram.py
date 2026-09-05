#!/usr/bin/env python3
"""Pic de VRAM pendant un bloc de génération, via NVML.

Utilisé DANS les `models/<nom>/generer.py` (contrat : colonne
`vram_pic_mo` de `timings.csv`). Dégradation silencieuse : sans GPU ni
`nvidia-ml-py`, `pic_mo` vaut None et le context manager ne fait rien —
ne lève jamais.
"""
from __future__ import annotations

import threading
import time


class PicVRAM:
    """Échantillonne la VRAM utilisée dans un thread léger et retient le pic.

        with PicVRAM() as p:
            wav = model.generate(...)
        print(p.pic_mo)   # int (Mo) ou None si NVML indisponible
    """

    def __init__(self, intervalle_s: float = 0.05, index_gpu: int = 0) -> None:
        self.intervalle_s = intervalle_s
        self.index_gpu = index_gpu
        self.pic_mo: int | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._handle = None
        self._pynvml = None

    # -- cycle de vie -------------------------------------------------
    def __enter__(self) -> "PicVRAM":
        try:
            import pynvml

            pynvml.nvmlInit()
            self._pynvml = pynvml
            self._handle = pynvml.nvmlDeviceGetHandleByIndex(self.index_gpu)
        except Exception:
            return self  # pas de GPU / lib absente : no-op

        self.pic_mo = self._lire_mo()
        self._thread = threading.Thread(target=self._boucle, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._pynvml is not None:
            try:
                self._pynvml.nvmlShutdown()
            except Exception:
                pass

    # -- interne --------------------------------------------------
    def _lire_mo(self) -> int | None:
        try:
            used = self._pynvml.nvmlDeviceGetMemoryInfo(self._handle).used
            return int(used / (1024 * 1024))
        except Exception:
            return None

    def _boucle(self) -> None:
        while not self._stop.wait(self.intervalle_s):
            mo = self._lire_mo()
            if mo is not None and (self.pic_mo is None or mo > self.pic_mo):
                self.pic_mo = mo
