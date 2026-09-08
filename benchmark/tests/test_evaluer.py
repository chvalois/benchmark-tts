"""Tests de l'évaluation croisée transcriptions x corpus (benchmark/evaluer.py)."""
from __future__ import annotations

from benchmark.corpus import Phrase
from benchmark.evaluer import evaluer_runs, synthese

CORPUS = [
    Phrase("p01", "le vieux moulin tournait lentement dans le vent du soir",
           "moyen", "narration", ("liaison",)),
    Phrase("p02", "elle poussa la lourde porte de chêne massif du grenier",
           "moyen", "narration", ()),
    Phrase("p03", "il compta 21 moutons avant de sombrer dans le sommeil",
           "moyen", "narration", ("nombre",)),
]


def test_run_parfait_zero_anomalie():
    tr = [{"id_phrase": "p01", "repetition": 1,
           "texte_transcrit": "le vieux moulin tournait lentement dans le vent du soir"}]
    (ligne,) = evaluer_runs(tr, CORPUS)
    assert ligne["wer"] == 0.0
    assert ligne["fidelite_verifiee"] is True
    assert not (ligne["hallucination"] or ligne["troncature"] or ligne["repetition_audio"])


def test_nombre_ecrit_ne_penalise_pas_le_wer():
    tr = [{"id_phrase": "p03", "repetition": 1,
           "texte_transcrit": "il compta vingt et un moutons avant de sombrer dans le sommeil"}]
    (ligne,) = evaluer_runs(tr, CORPUS)
    assert ligne["wer"] == 0.0


def test_troncature_detectee():
    tr = [{"id_phrase": "p02", "repetition": 1, "texte_transcrit": "elle poussa la lourde porte"}]
    (ligne,) = evaluer_runs(tr, CORPUS)
    assert ligne["troncature"] is True
    assert "troncature" in ligne["anomalie_kind"]


def test_transcription_inconnue_ignoree():
    tr = [{"id_phrase": "pZZ", "repetition": 1, "texte_transcrit": "hors corpus"}]
    assert evaluer_runs(tr, CORPUS) == []


def test_synthese_taux_et_listes():
    tr = [
        {"id_phrase": "p01", "repetition": 1,
         "texte_transcrit": "le vieux moulin tournait lentement dans le vent du soir"},
        {"id_phrase": "p02", "repetition": 1, "texte_transcrit": "elle poussa la lourde porte"},
        {"id_phrase": "p03", "repetition": 1,
         "texte_transcrit": "recette de cuisine totalement differente qui n a rien a voir ici"},
    ]
    lignes = evaluer_runs(tr, CORPUS)
    s = synthese(lignes, plancher_wer=0.05)
    assert s["n_runs"] == 3 and s["n_verifiees"] == 3
    assert s["taux_troncature"] > 0.0
    assert "p02" in s["phrases_troncature"]
    assert "p03" in s["phrases_hallucination"]
    assert 0.0 <= s["wer_net_plancher"] <= s["wer_moyen"]
    assert "narration" in s["wer_par_registre"]
    assert "nombre" in s["wer_par_piege"]


def test_synthese_vide():
    assert synthese([])["n_runs"] == 0


def test_perceptuel_joint_et_agrege():
    tr = [
        {"id_phrase": "p01", "repetition": 1,
         "texte_transcrit": "le vieux moulin tournait lentement dans le vent du soir"},
        {"id_phrase": "p02", "repetition": 1,
         "texte_transcrit": "elle poussa la lourde porte de chêne massif du grenier"},
    ]
    perc = [
        {"id_phrase": "p01", "repetition": 1, "sim": 0.90},
        {"id_phrase": "p02", "repetition": 1, "sim": 0.80},
    ]
    lignes = evaluer_runs(tr, CORPUS, perceptuel=perc)
    assert lignes[0]["sim"] == 0.90
    # aucune métrique de naturalité auto ne subsiste
    assert "utmos" not in lignes[0] and "nisqa" not in lignes[0]
    s = synthese(lignes)
    assert abs(s["sim_moyen"] - 0.85) < 1e-9
    assert "nisqa_moyen" not in s and "ttsds2" not in s


def test_synthese_sans_perceptuel_none():
    lignes = evaluer_runs(
        [{"id_phrase": "p01", "repetition": 1,
          "texte_transcrit": "le vieux moulin tournait lentement dans le vent du soir"}],
        CORPUS,
    )
    s = synthese(lignes)
    assert s["sim_moyen"] is None
