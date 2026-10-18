# 02 — Alcance

## Dentro (in-scope)

- **Modelar el CV como datos** YAML por sección e idioma (`personales`, `experiencia`, `educacion`,
  `certificaciones`, `publicaciones`, `aptitudes`, `otros`); **ES es la única fuente de verdad**.
- **Traducir ES→EN** vía la API de DeepL **en lote**, con **cache por hash fuera de `data/`** para no
  re-traducir lo que no cambió.
- **Renderizar** los datos a LaTeX con Jinja2 (delimitadores propios que no chocan con LaTeX) sobre **una**
  plantilla (`altacv`).
- **Compilar a PDF con `latexmk`** (que orquesta `biber` solo → publicaciones resueltas).
- **Validar la forma** de cada sección de datos antes de renderizar (contrato de datos).
- **Un CLI orquestador único**: `load → (translate si cambió) → render → compile`.

## Fuera (out-of-scope) — explícito

- **Base de datos y persistencia.** Sin Postgres, sin ORM (SQLModel/SQLAlchemy), sin Alembic, sin la
  gobernanza de datos de ClearNote_Dev. La fuente son los YAML versionados en git. _(Regla de oro del proyecto.)_
- **API web, frontend y multi-tenant.** No se expone servicio; no hay UI web ni estado por tenant.
- **Edición manual de `data/en/`.** El inglés es **derivado**; jamás se edita a mano.
- **Múltiples plantillas activas a la vez.** Se elige **UNA** (`altacv` o `cv_ds`), no ambas.
- **Idiomas distintos de EN** (por ahora; ver roadmap → Después).
- **Editor visual / GUI** del CV.

## Supuestos

- Existe una **API key de DeepL** (free o pro) disponible vía `.env` (`DEEPL_API_KEY`).
- El contenedor trae **TeXLive + `biber` + `latexmk`** (ya provisto en el Dockerfile).
- El volumen de datos es pequeño (un CV): no hay problema de escala ni de concurrencia.

## Restricciones

- **Cuota de DeepL:** minimizar llamadas (batch + cache por hash). Es un costo real, no cosmético.
- **Cero secretos y cero artefactos de build en git** (`.env`, `output/**`, `*.aux/.log/.bcf/.run.xml`, cache).
- **Determinismo:** sin rutas absolutas ni datos aleatorios; el render de un fixture debe ser reproducible.

## Fronteras del sistema

- **DeepL API** — servicio externo de traducción. Dueño externo; se consume con la lib oficial `deepl`.
- **TeXLive / `biber` / `latexmk`** — toolchain de compilación dentro del contenedor. No es código propio.
- **Plantilla `altacv`** (upstream LaTeX, MIT) — se **vendoriza una sola copia**, sin el sample upstream.
