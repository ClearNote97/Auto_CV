"""Tests de config: accesores, API key lazy, labels i18n, enmascarado."""

import pytest

from src.autocv.config import Config, ConfigError


def test_loads_and_accessors(cfg):
    assert cfg.get("project.name") == "AutoCV"
    assert cfg.get_source_language() == "es"
    assert cfg.get_target_language() == "en"
    assert cfg.get_latex_engine() == "latexmk"
    assert cfg.get_template_name() == "cv_ds"
    assert str(cfg.get_template_dir()).endswith("templates/cv_ds")


def test_lazy_api_key_present(cfg):
    assert cfg.get_deepl_api_key() == "test-key-xx"


def test_lazy_api_key_missing_does_not_break_load(project, monkeypatch):
    monkeypatch.delenv("DEEPL_API_KEY", raising=False)
    cfg = Config(config_dir="config")  # cargar NO debe fallar sin key
    with pytest.raises(ConfigError):
        cfg.get_deepl_api_key()  # solo falla al pedirla


def test_get_labels(cfg):
    assert cfg.get_labels("es")["resumen"] == "Resumen Profesional"
    assert cfg.get_labels("en")["resumen"] == "Professional Summary"
    # idioma desconocido → cae al idioma fuente
    assert cfg.get_labels("pt")["resumen"] == "Resumen Profesional"


def test_str_masks_key(cfg):
    text = str(cfg)
    assert "test-key-xx" not in text
    assert "OCULTA" in text


def test_missing_config_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ConfigError):
        Config(config_dir="config")
