# Plan — Feature 001 (pipeline de CV)

> El CÓMO. Enlaza a `spec.md`. Debe poder ejecutarse sin adivinar.

## Arquitectura

Paquete de dominio único `src/autocv/` (no se usan las capas `backend/frontend/database` del scaffold
full-stack — no aplican a una herramienta CLI; ver `03_stack` → decisiones). Flujo lineal, un módulo por
responsabilidad, acoplados **por contrato** (principio 8):

```
cli.py ──► config.py ──► data_loader.py ──► translator.py ──► renderer.py ──► pdf.py
 (orquesta)  (única       (lee data/es)     (ES→EN lote,       (Jinja2→.tex)   (latexmk
             config)                          cache hash)                        → PDF)
```

| Módulo | Responsabilidad | Origen |
|---|---|---|
| `config.py` | Única fuente de rutas/idiomas/engine. Carga `config/*.yaml` + `.env`. | **Portar** el `config.py` bueno del legacy (quitar el doble docstring). |
| `data_loader.py` | Cargar YAML por sección/idioma; error claro si vacío/faltante. | **Portar** el `data_loader.py` bueno del legacy. |
| `translator.py` | ES→EN con **lib oficial `deepl`**, **en lote**, cache por hash en `.cache/`. | **Reescribir** (el legacy usa `requests` string-por-string). |
| `renderer.py` | Solo Jinja2→`.tex` con los delimitadores LaTeX (`((* *))`, `((( )))`, `((# #))`). | **Extraer** del monolito `template_renderer.py`. |
| `pdf.py` | Compilar con **`latexmk -pdf`** usando `cwd=` (no `os.chdir`). biber lo orquesta latexmk. | **Implementar** (hoy es stub / pdflatex×2 sin biber). |
| `cli.py` | Orquestador `autocv build --lang es\|en\|both`. Reemplaza `run.py`/`main.py`/el `main()` del monolito. | **Nuevo** (destino `click`). |

## Modelo de datos

**No aplica base de datos** (ver `02_scope`). El "modelo" son los YAML por sección; su forma se validará
como contrato en la feature 002, no aquí. Sin tablas, sin migraciones Alembic, sin RLS/auditoría.

## Contratos

- **CLI:** `autocv build [--lang es|en|both] [--template altacv] [--output cv_final] [--no-clean]`.
- **Config:** `config/config.yaml` (paths, languages, latex.engine) + `config/deepl_config.yaml`
  (timeout, retries, formality). Corregir `style_file` inexistente y `templates_dir` para que apunte a la
  plantilla elegida (fin de las "dos realidades de configuración", CA5).
- **Traducción:** contrato de `translator` = recorrer el dict/list, juntar los strings de un documento y
  traducirlos en lote preservando estructura; cache = SHA256 del YAML fuente en `.cache/<seccion>.hash`.

## Estrategia de pruebas

- **Unit** (espejo de `src/autocv/`, en `tests/`):
  - `data_loader`: YAML vacío / faltante / malformado (edge + estado vacío).
  - `translator`: **mock de DeepL** (sin red), hash hit/miss, batch (una llamada por documento).
  - `renderer`: render **determinista** de un fixture → `.tex` esperado (sin red, sin LaTeX).
- **Acceptance** (`tests/acceptance/`, contra `spec.md`): smoke del pipeline completo con DeepL y compilación
  mockeados/marcados, verificando CA1–CA6.
- **Gate** (CA7): `black` + `flake8` + `mypy` + `pytest` en pre-commit.
