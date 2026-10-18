# =============================================================================
# AutoCV — Dev Container
# Imagen mínima: Python + LaTeX (TeXLive) para generar el CV. Nada de ciencia
# de datos: este proyecto es una HERRAMIENTA, no un notebook (ver README §7).
# =============================================================================
# La etiqueta de la imagen y el comentario ahora COINCIDEN (antes decía 3.13.5
# pero el FROM era 3.13.2 — huella de crecer sin limpiar, README §4.13).
FROM python:3.13.2-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

# -----------------------------------------------------------------------------
# LaTeX + utilidades. OJO: cada `\` debe ser el ÚLTIMO carácter de la línea.
# Un espacio después del `\` rompe la continuación (bug real del Dockerfile
# anterior, README §4.13) — aquí ya no hay ninguno.
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    # --- LaTeX: solo lo que la plantilla altacv necesita ---
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-lang-spanish \
    texlive-lang-english \
    texlive-bibtex-extra \
    biber \
    latexmk \
    # --- Control de versiones (útil dentro del contenedor) ---
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# -----------------------------------------------------------------------------
# QUÉ SE QUITÓ y POR QUÉ (servicios/paquetes que AutoCV no necesita):
#   - ipykernel        → Jupyter. Drift del scaffold de datos; AutoCV no usa notebooks.
#   - texlive-science  → paquetes de matemáticas/ciencia; altacv no los usa.
#   - build-essential  → no se compila nada en C. requests/pyyaml/jinja2 traen wheels.
#   - vim / curl       → editor y descargas ad-hoc; innecesarios para construir el CV.
#
# QUÉ SE AGREGÓ:
#   - biber            → la plantilla usa biblatex (pubs-authoryear.cfg). Sin biber
#                        las PUBLICACIONES no resuelven (README §4.7). `latexmk -pdf`
#                        lo invoca solo — usa ese motor, no `pdflatex` a secas.
# -----------------------------------------------------------------------------

# pip actualizado (sin caché para no engordar la imagen).
RUN pip install --no-cache-dir --upgrade pip

# Las dependencias Python se instalan vía postCreateCommand del devcontainer
# (`pip install -r requirements.txt`), no aquí, para no reconstruir la imagen
# cada vez que cambian.

# WORKDIR /workspaces/${localWorkspaceFolderBasename}
