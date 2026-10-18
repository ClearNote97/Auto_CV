"""Tests de data_loader: carga por sección/idioma y casos borde (faltante/vacío)."""

import pytest

from src.autocv.data_loader import DataLoader, DataLoaderError


def test_load_section_ok(cfg):
    data = DataLoader(cfg).load_section("personales", "es")
    assert data["nombre"] == "MSc. Juan Pérez"


def test_load_section_missing_file(cfg):
    with pytest.raises(DataLoaderError):
        DataLoader(cfg).load_section("inexistente", "es")


def test_load_section_empty_file(cfg, project):
    (project / "data" / "es" / "vacio.yaml").write_text("")
    with pytest.raises(DataLoaderError):
        DataLoader(cfg).load_section("vacio", "es")


def test_load_all_data(cfg):
    data = DataLoader(cfg).load_all_data("es")
    assert set(data.keys()) == {"personales", "experiencia"}


def test_load_all_data_missing_dir(cfg):
    with pytest.raises(DataLoaderError):
        DataLoader(cfg).load_all_data("fr")
