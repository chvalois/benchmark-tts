"""Tests de l'agrégation de vitesse (benchmark/mesurer_vitesse.py)."""
from __future__ import annotations

import textwrap

from benchmark.mesurer_vitesse import agreger_vitesse, charger_timings

CSV = textwrap.dedent("""\
    id_phrase,repetition,seed,ttfa_s,gen_s,audio_s,vram_pic_mo,categorie_chunk,statut
    p01,1,42,0.30,1.00,2.00,4100,replique_courte,ok
    p01,2,43,0.34,1.20,2.10,4100,replique_courte,ok
    p26,1,42,0.50,30.0,60.0,8200,narration,ok
    p26,2,43,0.55,90.0,60.0,8200,narration,echec:boucle
""")


def _fichier(tmp_path):
    f = tmp_path / "timings.csv"
    f.write_text(CSV, encoding="utf-8")
    return f


def test_charger_timings_ignore_les_echecs_et_caste(tmp_path):
    lignes = charger_timings(_fichier(tmp_path))
    assert len(lignes) == 3                       # la ligne echec:boucle est écartée
    assert lignes[0]["gen_s"] == 1.0
    assert isinstance(lignes[0]["vram_pic_mo"], int)


def test_agreger_vitesse_rtf_et_categories(tmp_path):
    agg = agreger_vitesse(charger_timings(_fichier(tmp_path)))
    # global : 3 runs, RTF = gen/audio -> 0.5, 0.571..., 0.5
    assert agg["global"]["n_runs"] == 3
    assert agg["global"]["rtf"]["moyenne"] < 1.0
    assert agg["global"]["rtfx"]["moyenne"] > 1.0
    assert set(agg["par_categorie"]) == {"replique_courte", "narration"}
    assert agg["par_categorie"]["narration"]["n_runs"] == 1


def test_agreger_vitesse_liste_vide():
    agg = agreger_vitesse([])
    assert agg["global"]["n_runs"] == 0
    assert agg["global"]["rtf"]["n"] == 0
