"""Fixtures compartidas: un proyecto AutoCV mínimo y autocontenido en tmp_path.

No toca la red ni LaTeX; cada test trabaja sobre config/data/plantilla de juguete.
"""

import pytest
import yaml

from src.autocv.config import Config

_CONFIG = {
    "project": {"name": "AutoCV", "author": "Tester", "repo_url": "https://github.com/x/Auto_CV"},
    "languages": {"source": "es", "target": "en"},
    "paths": {"data_dir": "data", "templates_dir": "templates", "output_dir": "output"},
    "latex": {"engine": "latexmk", "options": ["-pdf"], "template": "cv_ds", "main_template": "cv.tex"},
    "output": {"lang_suffix": {"es": "", "en": "_eng"}, "filename_base": ""},
    "labels": {
        "es": {"resumen": "Resumen Profesional", "experiencia": "Experiencia"},
        "en": {"resumen": "Professional Summary", "experiencia": "Experience"},
    },
}

_DEEPL = {
    "deepl": {"api_url": "https://api-free.deepl.com"},
    "translation": {
        "preserve_formatting": True,
        "split_sentences": "1",
        "formality": "default",
        "no_translate_keys": ["empresa", "enlace"],
        "glossary": {"Actualidad": "Present"},
    },
}

_DATA_ES = {
    "personales": {"nombre": "MSc. Juan Pérez", "titulo": "Economista", "correo": "j@x.com"},
    "experiencia": {
        "experiencia": [
            {
                "puesto": "Analista",
                "empresa": "ACME S.A.",
                "fecha_fin": "Actualidad",
                "descripcion": ["Subí ventas 100%."],
            }
        ]
    },
}

# Plantilla de juguete con los delimitadores propios del proyecto.
_TEMPLATE = (
    "\\documentclass{article}\n\\begin{document}\n"
    "Nombre: ((( personales.nombre )))\n"
    "((* for e in experiencia.experiencia *))"
    "Puesto: ((( e.puesto ))) en ((( e.empresa )))\n"
    "((* for d in e.descripcion *))- ((( d )))\n((* endfor *))"
    "((* endfor *))"
    "\\end{document}\n"
)


@pytest.fixture
def project(tmp_path, monkeypatch):
    """Monta un proyecto AutoCV mínimo en tmp_path y hace chdir ahí. Devuelve la ruta raíz."""
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "config.yaml").write_text(yaml.dump(_CONFIG, allow_unicode=True))
    (tmp_path / "config" / "deepl_config.yaml").write_text(yaml.dump(_DEEPL, allow_unicode=True))
    es = tmp_path / "data" / "es"
    es.mkdir(parents=True)
    for name, content in _DATA_ES.items():
        (es / f"{name}.yaml").write_text(yaml.dump(content, allow_unicode=True))
    tpl = tmp_path / "templates" / "cv_ds"
    tpl.mkdir(parents=True)
    (tpl / "cv.tex").write_text(_TEMPLATE)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DEEPL_API_KEY", "test-key-xx")
    # Aislar del .env real: load_dotenv lo busca vía la ubicación de config.py (no el cwd),
    # así que sin esto repoblaría variables desde el .env del proyecto.
    monkeypatch.setattr("src.autocv.config.load_dotenv", lambda *a, **k: None)
    return tmp_path


@pytest.fixture
def cfg(project):
    """Config cargada contra el proyecto de juguete."""
    return Config(config_dir="config")
