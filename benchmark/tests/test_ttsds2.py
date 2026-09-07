"""Tests des helpers purs de mesurer_ttsds2 (I/O `ttsds2.json`,
extraction de scores). Le runner (`ttsds2_dossier`) charge TTSDS2 → non
testé ici.
"""
from __future__ import annotations

from benchmark.mesurer_ttsds2 import _extraire_scores, ecrire_ttsds2, lire_ttsds2


def test_ttsds2_roundtrip(tmp_path):
    f = tmp_path / "ttsds2.json"
    data = {
        "score_global": 76.3,
        "par_composante": {"speaker": 0.8, "intelligibility": 0.9,
                           "prosody": 0.7, "generic": 0.75},
        "ref": "fr", "n_gen": 99, "n_ref": 150,
    }
    ecrire_ttsds2(f, data)
    assert lire_ttsds2(f) == data


def test_lire_ttsds2_absent_ou_corrompu(tmp_path):
    assert lire_ttsds2(tmp_path / "pas_la.json") is None

    corrompu = tmp_path / "ttsds2.json"
    corrompu.write_text('{"score_global": 12.3, ', encoding="utf-8")  # tronqué
    assert lire_ttsds2(corrompu) is None

    liste = tmp_path / "liste.json"
    liste.write_text("[1, 2, 3]", encoding="utf-8")  # JSON valide mais pas un dict
    assert lire_ttsds2(liste) is None


def test_extraire_scores_forme_dataframe_records():
    """Forme réelle de get_aggregated_results() : une ligne par catégorie
    + une ligne OVERALL, colonnes `benchmark_category` / `score_mean`."""
    recs = [
        {"benchmark_category": "PROSODY", "dataset": "firered__papa_narration", "score_mean": 64.38},
        {"benchmark_category": "OVERALL", "dataset": "firered__papa_narration", "score_mean": 73.09},
        {"benchmark_category": "INTELLIGIBILITY", "dataset": "firered__papa_narration", "score_mean": 63.27},
        {"benchmark_category": "GENERIC", "dataset": "firered__papa_narration", "score_mean": 91.62},
    ]
    g, comp = _extraire_scores(recs, "firered__papa_narration")
    assert g == 73.09
    assert comp == {"intelligibility": 63.27, "prosody": 64.38, "generic": 91.62}
    assert "speaker" not in comp


def test_extraire_scores_sans_overall_fait_la_moyenne():
    recs = [
        {"benchmark_category": "PROSODY", "score_mean": 0.6},
        {"benchmark_category": "INTELLIGIBILITY", "score_mean": 0.4},
        {"benchmark_category": "GENERIC", "score_mean": 0.2},
    ]
    g, comp = _extraire_scores(recs, "")
    assert abs(g - 0.4) < 1e-9
    assert comp["generic"] == 0.2


def test_extraire_scores_filtre_le_bon_dataset():
    recs = [
        {"benchmark_category": "OVERALL", "dataset": "A", "score_mean": 10.0},
        {"benchmark_category": "OVERALL", "dataset": "B", "score_mean": 90.0},
        {"benchmark_category": "GENERIC", "dataset": "B", "score_mean": 88.0},
    ]
    g, comp = _extraire_scores(recs, "B")
    assert g == 90.0 and comp["generic"] == 88.0
