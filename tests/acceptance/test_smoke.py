"""Smoke de aceptación: el pipeline completo (load → render → compile) en un comando.

La compilación LaTeX se MOCKEA (no requiere TeXLive en el test); se verifica que el
pipeline encadena y produce el `.tex` esperado para el idioma pedido. → CA1, CA5.
"""

from src.autocv import pdf as P
from src.autocv.cli import build


def test_smoke_build_es(cfg, monkeypatch):
    # Stub de la compilación: devuelve la ruta del PDF sin invocar latexmk.
    monkeypatch.setattr(P.PdfCompiler, "compile", lambda self, tex, clean_aux=True: tex.with_suffix(".pdf"))

    pdfs = build(lang="es")  # CA1: un comando

    assert len(pdfs) == 1
    tex = cfg.get_output_dir() / "CV_Juan_Pérez.tex"  # nombre derivado del nombre, sin título
    assert tex.exists()
    content = tex.read_text()
    assert "Juan Pérez" in content  # contenido real renderizado
    assert "Analista" in content  # sección experiencia
