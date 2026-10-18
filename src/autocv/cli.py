"""CLI — orquestador único de AutoCV: `load → translate → render → compile`.

Feature 001, Tarea 6. Reemplaza `run.py`, `src/main.py` y el `main()` del monolito legacy (CA1).
Un solo comando reconstruye el CV de punta a punta.

Uso (mientras no haya console-script `autocv`):
    python -m src.autocv.cli build --lang both
    python -m src.autocv.cli build --lang es --no-clean

Se usa `argparse` (stdlib) para no sumar dependencias a la corrida 0; migrar a `click` es
un pulido opcional (roadmap), no un requisito.
"""

import argparse
import logging
import sys
from typing import List, Optional

from src.autocv.config import load_config
from src.autocv.data_loader import DataLoader
from src.autocv.pdf import PdfCompiler
from src.autocv.renderer import Renderer
from src.autocv.translator import Translator

logger = logging.getLogger("autocv")


# Títulos académicos que se omiten al derivar el nombre del archivo.
_TITLES = {"msc", "dr", "dra", "ing", "phd", "lic", "mg", "esp", "mba", "md"}


def _slug_name(nombre: str) -> str:
    """Base de archivo a partir del nombre: quita títulos (MSc., Dr.…) y une con '_'."""
    tokens = nombre.replace(",", "").split()
    while tokens and tokens[0].rstrip(".").lower() in _TITLES:
        tokens.pop(0)
    return "_".join(t.replace(".", "") for t in tokens) or "CV"


def build(
    lang: str = "both",
    output: Optional[str] = None,
    template: Optional[str] = None,
    clean: bool = True,
    force: bool = False,
) -> List[str]:
    """Ejecuta el pipeline completo para el/los idioma(s) pedidos. Devuelve rutas de PDF generadas."""
    cfg = load_config()
    source = cfg.get_source_language()  # es
    target = cfg.get_target_language()  # en
    langs = [source, target] if lang == "both" else [lang]
    loader = DataLoader(cfg)

    # Nombre base del archivo: --output > config.output.filename_base > derivado del
    # nombre FUENTE (sin traducir). Es igual para todos los idiomas; el sufijo cambia.
    base = output or cfg.get("output.filename_base") or ""
    if not base:
        nombre = (loader.load_section("personales", source) or {}).get("nombre", "CV")
        base = f"CV_{_slug_name(nombre)}"
    suffixes = cfg.get("output.lang_suffix", {}) or {}

    # Traducir ES→EN solo si se pide un idioma derivado (respeta cache por hash).
    if target in langs and target != source:
        logger.info("Traduciendo %s → %s (solo lo que cambió)…", source, target)
        Translator(cfg).translate_all(force=force, log=logger.info)

    renderer = Renderer(cfg)
    compiler = PdfCompiler(cfg)

    pdfs: List[str] = []
    for lg in langs:
        logger.info("── Idioma '%s' ──", lg)
        data = loader.load_all_data(lg)
        data["labels"] = cfg.get_labels(lg)  # títulos de sección en el idioma del build
        data["repo_url"] = cfg.get("project.repo_url", "")  # link del footer
        suffix = suffixes.get(lg, f"_{lg}")
        tex = renderer.render_to_file(data, output_name=f"{base}{suffix}", template_name=template)
        logger.info("  .tex → %s", tex)
        pdf = compiler.compile(tex, clean_aux=clean)
        logger.info("  PDF → %s", pdf)
        pdfs.append(str(pdf))
    return pdfs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="autocv", description="Generador de CV bilingüe (ES→EN) a PDF.")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("build", help="Reconstruye el CV: load → translate → render → compile.")
    b.add_argument("--lang", "-l", choices=["es", "en", "both"], default="both",
                   help="Idioma(s) a generar (default: both).")
    b.add_argument("--output", "-o", default=None,
                   help="Nombre base de salida (default: CV_<nombre> de config/personales).")
    b.add_argument("--template", "-t", default=None, help="Plantilla .tex (default: la de config.yaml).")
    b.add_argument("--no-clean", action="store_true", help="No limpiar auxiliares de LaTeX.")
    b.add_argument("--force", action="store_true", help="Re-traducir todo, ignorando la cache por hash.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.command == "build":
        try:
            pdfs = build(
                lang=args.lang,
                output=args.output,
                template=args.template,
                clean=not args.no_clean,
                force=args.force,
            )
        except Exception as e:  # noqa: BLE001 — el CLI reporta el error, no lo propaga como traceback
            logger.error("❌ %s", e)
            return 1
        print("\n✅ CV generado:")
        for p in pdfs:
            print(f"   📑 {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
