"""Renderer — datos → LaTeX (`.tex`) con Jinja2 y delimitadores propios.

Extraído del monolito legacy (`docs/AutoCV-legacy/src/modules/template_renderer.py`) — feature 001,
Tarea 4. SOLO la parte de render: nada de cargar YAML (eso es `data_loader`) ni de compilar (eso es `pdf`).
Conserva los delimitadores que no chocan con LaTeX: `((* *))` (bloque) y `((( )))` (variable).
"""

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

# Caracteres especiales de LaTeX → su forma escapada. Sin esto, un '%' en los datos
# comenta el resto de la línea ("+100% en…" se corta), un '&' rompe la compilación, etc.
_LATEX_MAP = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
_LATEX_RE = re.compile("|".join(re.escape(k) for k in _LATEX_MAP))

# Claves cuyos valores son URLs/identificadores: NO se escapan (romperían el enlace).
_NO_ESCAPE_KEYS = {"enlace", "linkedin", "github", "correo", "web", "repo_url"}


def _escape_latex(data: Any, skip: bool = False) -> Any:
    """Escapa recursivamente los especiales de LaTeX en los strings, salvo URLs/identificadores.

    En UN solo paso (regex) para no re-escapar los '\' que introduce el propio escape.
    """
    if isinstance(data, dict):
        return {k: _escape_latex(v, skip or k in _NO_ESCAPE_KEYS) for k, v in data.items()}
    if isinstance(data, list):
        return [_escape_latex(item, skip) for item in data]
    if isinstance(data, str) and not skip:
        return _LATEX_RE.sub(lambda m: _LATEX_MAP[m.group()], data)
    return data


class RendererError(Exception):
    """Error al renderizar la plantilla LaTeX."""


class Renderer:
    """Renderiza los datos del CV a un `.tex` usando la plantilla elegida en config."""

    def __init__(self, config):
        self.config = config
        self.template_dir = config.get_template_dir()  # p. ej. templates/cv_ds
        self.main_template = config.get_main_template()  # p. ej. cv_template.tex
        self.output_dir = config.get_output_dir()

    def _environment(self) -> Environment:
        return Environment(
            block_start_string="((*",
            block_end_string="*))",
            variable_start_string="(((",
            variable_end_string=")))",
            comment_start_string="((#",
            comment_end_string="#))",
            trim_blocks=True,
            autoescape=False,  # es LaTeX, no HTML
            # Undefined por defecto (lenient): la plantilla usa `((* if opcional *))` para campos
            # que pueden faltar (linkedin, github, resumen, pub.enlace…). StrictUndefined los rompería.
            loader=FileSystemLoader(str(self.template_dir)),
        )

    @staticmethod
    def _preprocess(data: dict[str, Any]) -> dict[str, Any]:
        """Ajustes de PRESENTACIÓN propios de la plantilla (no tocan la fuente en disco).

        Muestra el handle de LinkedIn/GitHub en vez de la URL completa. Se copia el dict para no
        mutar los datos cargados.
        """
        data = dict(data)
        personales = dict(data.get("personales") or {})
        if personales.get("linkedin"):
            personales["linkedin"] = (
                personales["linkedin"].replace("https://www.linkedin.com/in/", "").strip("/")
            )
        if personales.get("github"):
            personales["github"] = personales["github"].replace("https://github.com/", "").strip("/")
        data["personales"] = personales
        return data

    def render(self, data: dict[str, Any], template_name: str | None = None) -> str:
        """Renderiza `data` con la plantilla y devuelve el contenido LaTeX como string."""
        env = self._environment()
        name = template_name or self.main_template
        try:
            template = env.get_template(name)
        except Exception as e:
            raise RendererError(f"No se pudo cargar la plantilla '{name}' en {self.template_dir}: {e}")
        try:
            # Escapar especiales de LaTeX DESPUÉS del preprocess (sobre el handle ya recortado).
            return template.render(**_escape_latex(self._preprocess(data)))
        except Exception as e:
            raise RendererError(f"Error renderizando '{name}': {e}")

    def render_to_file(
        self, data: dict[str, Any], output_name: str = "cv_final", template_name: str | None = None
    ) -> Path:
        """Renderiza y escribe `<output_dir>/<output_name>.tex`. Devuelve la ruta."""
        content = self.render(data, template_name)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.output_dir / f"{output_name}.tex"
        out_path.write_text(content, encoding="utf-8")
        return out_path


if __name__ == "__main__":
    from src.autocv.config import load_config
    from src.autocv.data_loader import DataLoader

    cfg = load_config()
    data = DataLoader(cfg).load_all_data("es")
    path = Renderer(cfg).render_to_file(data)
    print(f"✅ .tex generado: {path}")
