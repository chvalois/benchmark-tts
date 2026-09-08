"""Tests du convertisseur Markdown -> HTML de build_pages (fonction pure)."""
from __future__ import annotations

from benchmark.build_pages import md_vers_html


def test_titres_et_paragraphe():
    h = md_vers_html("# Grand\n\n## Moyen\n\ntexte simple.")
    assert "<h1>Grand</h1>" in h and "<h2>Moyen</h2>" in h
    assert "<p>texte simple.</p>" in h


def test_table():
    md = "| modèle | WER |\n|---|---|\n| firered | 3.6% |\n| voxcpm | 4.2% |"
    h = md_vers_html(md)
    assert h.count("<tr>") == 3               # entête + 2 lignes
    assert "<th>modèle</th>" in h and "<td>firered</td>" in h


def test_liste_et_citation():
    h = md_vers_html("- un\n- deux\n\n> une remarque")
    assert "<ul>" in h and h.count("<li>") == 2
    assert "<blockquote>une remarque</blockquote>" in h


def test_inline_gras_code_italique():
    h = md_vers_html("un **mot** et `code` et *ital*.")
    assert "<strong>mot</strong>" in h and "<code>code</code>" in h and "<em>ital</em>" in h


def test_echappe_le_html_source():
    h = md_vers_html("texte <script>alert(1)</script> & suite")
    assert "<script>" not in h
    assert "&lt;script&gt;" in h and "&amp; suite" in h


def test_rapports_reels_se_rendent():
    """Les .md du dépôt passent sans erreur et produisent des tables."""
    from pathlib import Path

    for nom in ("comparatif.md", "EMOTIONS.md", "RESUME.md"):
        f = Path(__file__).resolve().parents[2] / "resultats" / nom
        if not f.is_file():
            continue
        h = md_vers_html(f.read_text(encoding="utf-8"))
        assert "<table>" in h and "<script" not in h.lower()
