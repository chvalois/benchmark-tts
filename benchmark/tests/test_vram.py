"""Tests du suivi de pic VRAM (benchmark/vram.py).

Sans dépendre d'un GPU : le context manager doit fonctionner (et
`pic_mo` valoir None) quand NVML est indisponible, et retourner un entier
quand il l'est.
"""
from __future__ import annotations

from benchmark.vram import PicVRAM


def test_pic_vram_ne_leve_jamais_et_type_coherent():
    with PicVRAM(intervalle_s=0.01) as p:
        _ = [i * i for i in range(10_000)]
    assert p.pic_mo is None or (isinstance(p.pic_mo, int) and p.pic_mo > 0)


def test_pic_vram_reutilisable():
    p1 = PicVRAM()
    with p1:
        pass
    assert p1.pic_mo is None or isinstance(p1.pic_mo, int)
