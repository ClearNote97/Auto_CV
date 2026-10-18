# -----------------------------------------------------------------------------
# DOCKERFILE - ClearNote_Dev (Entorno de Desarrollo)
# -----------------------------------------------------------------------------
# Usamos una imagen base de Python moderna (3.14 alpha/experimental o estable)
# La variante 'slim-bookworm' ofrece un balance perfecto entre peso y estabilidad (Debian 12).
FROM python:3.14.5-slim-bookworm

# Evita que Debian abra diálogos interactivos durante la instalación de paquetes.
ENV DEBIAN_FRONTEND=noninteractive

# Instalación de paquetes esenciales del sistema.
# NOTA AutoCV: este entorno NO usa base de datos, así que se desactivan los
# paquetes ligados a la capa Postgres/compilación de drivers (README docs/AutoCV §5):
# - build-essential   → DESACTIVADO: sin psycopg2/cryptography no se compila nada en C.
# - postgresql-client → DESACTIVADO: sin DB no hay `psql` ni run-admin.sh que correr.
# Se conservan:
# - git/openssh-client: control de versiones y repos privados.
# - ca-certificates: conexiones HTTPS seguras (la API de DeepL, p. ej.).
# - curl: red para healthchecks/descargas puntuales.
# Reactiva build-essential y postgresql-client si reactivas la capa Postgres.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # build-essential \
    ca-certificates \
    git \
    openssh-client \
    curl \
    # postgresql-client \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# TOOLCHAIN LaTeX (requerido por AutoCV para generar el PDF del CV)
# -----------------------------------------------------------------------------
# AutoCV es el proyecto de este repo (ver docs/AutoCV-legacy + spec/). Necesita
# TeXLive para compilar la plantilla altacv. Set MÍNIMO — solo lo que altacv usa:
#   - latex-base/recommended/extra : clases y paquetes (incluye paracol)
#   - fonts-recommended/extra       : fontawesome5, roboto, lato, academicons
#   - lang-spanish/english          : guiones y tipografía por idioma (CV bilingüe)
#   - bibtex-extra + biber          : biblatex; biber lo orquesta latexmk (CA4)
#   - latexmk                       : motor único que encadena pdflatex + biber
# NO se instala texlive-science, ipykernel ni build-essential (AutoCV no los usa).
# OJO: cada `\` debe ser el ÚLTIMO carácter de la línea (un espacio detrás rompe la continuación).
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalación de 'uv': el gestor de paquetes de alto rendimiento (Escrito en Rust).
# Copiamos los binarios directamente desde la imagen oficial de Astral Sh.
COPY --from=ghcr.io/astral-sh/uv:0.11.13 /uv /uvx /bin/

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DINÁMICA DEL WORKDIR
# -----------------------------------------------------------------------------
# Recibimos el nombre del proyecto desde docker-compose (viene del .env).
# Esto crea la carpeta física dentro del contenedor con el nombre correcto.
ARG APP_NAME=project_default
ENV PROJECT_NAME=${APP_NAME}

# Establecemos el directorio de trabajo dinámicamente.
# Ejemplo: si APP_NAME=ClearNote_Dev, el WORKDIR será /workspaces/ClearNote_Dev
WORKDIR /workspaces/${PROJECT_NAME}

# Comando por defecto para mantener el contenedor encendido mientras trabajas.
# Impide que el contenedor se apague inmediatamente después de iniciarse.
CMD ["sleep", "infinity"]