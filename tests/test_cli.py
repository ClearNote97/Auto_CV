"""Tests del CLI: derivación del nombre de archivo desde el nombre (sin títulos)."""

from src.autocv.cli import _slug_name


def test_slug_name_strips_titles():
    assert _slug_name("MSc. Nicolás Enrique Valencia Santiago") == "Nicolás_Enrique_Valencia_Santiago"
    assert _slug_name("Dr. Ana María Gómez") == "Ana_María_Gómez"


def test_slug_name_plain():
    assert _slug_name("Juan Pérez") == "Juan_Pérez"


def test_slug_name_empty_fallback():
    assert _slug_name("") == "CV"
