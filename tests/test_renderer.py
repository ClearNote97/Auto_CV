"""Tests de renderer: escape de especiales LaTeX (exento de URLs) y render determinista."""

from src.autocv import renderer as R
from src.autocv.renderer import Renderer


def test_escape_latex_specials():
    assert R._escape_latex("100% & $5 #1") == r"100\% \& \$5 \#1"


def test_escape_latex_exempts_urls():
    data = {"enlace": "https://x/a_b%c", "desc": "50% _x_"}
    out = R._escape_latex(data)
    assert out["enlace"] == "https://x/a_b%c"  # URL intacta
    assert out["desc"] == r"50\% \_x\_"  # prosa escapada


def test_render_substitutes_and_escapes(cfg):
    data = {
        "personales": {"nombre": "Juan"},
        "experiencia": {"experiencia": [{"puesto": "Dev", "empresa": "X", "descripcion": ["hizo 100%"]}]},
    }
    tex = Renderer(cfg).render(data)
    assert "Nombre: Juan" in tex
    assert "Puesto: Dev en X" in tex
    assert r"hizo 100\%" in tex  # '%' escapado (si no, cortaría la línea)
    assert "(((" not in tex  # delimitadores consumidos


def test_render_to_file_writes_tex(cfg):
    data = {"personales": {"nombre": "Juan"}, "experiencia": {"experiencia": []}}
    path = Renderer(cfg).render_to_file(data, output_name="test")
    assert path.exists()
    assert path.name == "test.tex"
