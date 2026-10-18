r"""PDF — compila el `.tex` a PDF con `latexmk` (biber orquestado solo).

Implementación real (el legacy tenía un stub y el monolito corría `pdflatex ×2` sin biber) —
feature 001, Tarea 5. Claves:
  - `latexmk -pdf` orquesta las pasadas de pdflatex Y `biber` automáticamente → las publicaciones
    resuelven sin lógica manual (criterio CA4).
  - `cwd=output_dir` en subprocess, NUNCA `os.chdir` (el legacy usaba estado global del proceso).
  - Se copian los assets de la plantilla (`.cls`, `.cfg`) junto al `.tex` antes de compilar, porque
    latexmk corre dentro de `output/` y necesita `\input{pubs-*.cfg}` y la clase a mano.
"""

import shutil
import subprocess
from pathlib import Path

# Archivos de la plantilla que deben acompañar al .tex en output/ para compilar.
_ASSET_FILES = ["altacv.cls", "pubs-num.cfg", "pubs-authoryear.cfg"]


class PdfError(Exception):
    """Error al compilar el PDF."""


class PdfCompiler:
    """Compila un `.tex` a PDF con el motor declarado en config (por defecto latexmk)."""

    def __init__(self, config):
        self.config = config
        self.output_dir = config.get_output_dir()
        self.template_dir = config.get_template_dir()
        self.engine = config.get_latex_engine()  # "latexmk"
        self.options = config.get_latex_options()  # ["-pdf", "-interaction=nonstopmode", "-halt-on-error"]

    def _stage_assets(self) -> None:
        """Copia los archivos de la plantilla necesarios junto al .tex en output/."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for name in _ASSET_FILES:
            src = self.template_dir / name
            if src.exists():
                shutil.copy2(src, self.output_dir / name)

    def compile(self, tex_path: Path, clean_aux: bool = True) -> Path:
        """Compila `tex_path` a PDF. Devuelve la ruta del PDF o lanza PdfError con el log."""
        self._stage_assets()

        cmd = [self.engine, *self.options, tex_path.name]
        # errors="replace": latexmk/pdflatex a veces emite bytes Latin-1 en su log
        # (p. ej. al eco de contenido acentuado); sin esto, decodificar la salida
        # crashea y oculta el resultado real de la compilación.
        result = subprocess.run(cmd, cwd=self.output_dir, capture_output=True, text=True, errors="replace")
        if result.returncode != 0:
            tail = "\n".join((result.stdout or "").splitlines()[-40:])
            raise PdfError(f"Falló la compilación ({' '.join(cmd)}). Últimas líneas del log:\n{tail}")

        pdf_path = self.output_dir / f"{tex_path.stem}.pdf"
        if not pdf_path.exists():
            raise PdfError(f"El motor terminó sin error pero no se generó el PDF: {pdf_path}")

        if clean_aux:
            self._clean_aux(tex_path)
        return pdf_path

    def _clean_aux(self, tex_path: Path) -> None:
        """Deja output/ solo con el entregable: quita auxiliares LaTeX, restos de biber y assets stageados."""
        if self.engine == "latexmk":
            subprocess.run(
                [self.engine, "-c", tex_path.name],
                cwd=self.output_dir,
                capture_output=True,
                text=True,
                errors="replace",
            )
        stem = tex_path.stem
        # latexmk -c no borra estos: restos de biber/biblatex y copias de la plantilla.
        leftovers = [
            self.output_dir / f"{stem}.bbl",
            self.output_dir / f"{stem}.blg",
            self.output_dir / f"{stem}.bcf",
            self.output_dir / f"{stem}.run.xml",
            self.output_dir / "pdfa.xmpi",
            *(self.output_dir / name for name in _ASSET_FILES),
        ]
        for path in leftovers:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    from src.autocv.config import load_config

    cfg = load_config()
    tex = cfg.get_output_dir() / "cv_final.tex"
    print(f"✅ PDF: {PdfCompiler(cfg).compile(tex)}")
