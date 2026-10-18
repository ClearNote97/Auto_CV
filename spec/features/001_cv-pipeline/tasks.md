# Tareas — Feature 001 (pipeline de CV)

> Pasos ejecutables en orden. Marca `[x]` al completar. Cada tarea es verificable.
> Traducción de la checklist de migración (README docs/AutoCV §6) a pasos SDD.

- [x] **1. Preparar el terreno (destructivo).** ✔ Hecho.
  Paquete `src/autocv/` + CLI `autocv` (confirmado). Legacy movido a `docs/AutoCV-legacy/`.
  Scaffold full-stack (`src/backend`, `src/frontend`, `src/analytics`, `src/database`) **conservado
  intacto** (uso probable a futuro). Esqueleto creado: `src/autocv/{__init__,config,data_loader,
  translator,renderer,pdf,cli}.py` + README.
  _Verificado:_ `python3 -c "import src.autocv; from src.autocv import config, data_loader, translator,
  renderer, pdf, cli"` → OK. (Convención de import de este repo: `src.autocv`, no `autocv` suelto.)

- [x] **2. Portar `config.py` y `data_loader.py`.** ✔ Hecho.
  Portados a `src/autocv/` (un solo docstring; API key **lazy** para desacoplar render/compile de DeepL).
  Insumos traídos al root: `config/config.yaml` (corregido: sin `style_file`, `template: cv_ds`,
  `engine: latexmk`), `config/deepl_config.yaml`, `data/es/*.yaml`. `DEEPL_API_KEY` migrada al `.env` real. → **CA5**.
  _Verificado:_ `load_config()` carga la config única (engine=latexmk, template=templates/cv_ds) y
  `DataLoader.load_all_data("es")` lee las 7 secciones; key lazy no rompe la carga; `__str__` la enmascara.
  _(Plantilla elegida: **cv_ds** — es la que tiene el `cv_template.tex` Jinja, no `altacv` pristino.)_

- [x] **3. Reescribir `translator.py`.** ✔ Hecho.
  Lib oficial `deepl` (import **lazy**), traducción **en lote** (una llamada por documento), cache SHA256
  en `.cache/translations/` fuera de `data/`. `preserve_formatting`/`split_sentences`/`formality` desde
  `deepl_config.yaml`. Red aislada en `_translate_batch()` (mockeable). → **CA2, CA3**.
  _Verificado (mock, sin red):_ 1 llamada por documento; no-traducibles (int/teléfono/vacío) intactos;
  claves y forma preservadas; cache **hit** sin cambios (0 llamadas) y re-traduce al editar la fuente.
  _Higiene (Tarea 8):_ `.cache/` en `.gitignore` ✓; `deepl` activo en `pyproject.toml` (gestión con uv) ✓.
  Skip por campo + glosario implementados (ver `deepl_config.yaml`).

- [x] **4. Extraer `renderer.py`.** ✔ Hecho.
  Solo Jinja2→`.tex` con los delimitadores LaTeX (`((* *))`/`((( )))`/`((# #))`), `autoescape=False`,
  `Undefined` lenient (la plantilla usa `((* if opcional *))`). Incluye el preprocesado de presentación
  linkedin/github (handle en vez de URL). Copiado al root el set **mínimo** de la plantilla `cv_ds`
  (`cv_template.tex`, `altacv.cls`, `pubs-num.cfg`, `pubs-authoryear.cfg`) — sin sample/imágenes/.git
  (adelanta parte de la higiene de la Tarea 8).
  _Verificado (datos ES reales):_ `.tex` generado (`output/cv_final.tex`), delimitadores consumidos,
  nombre en `\name{}`, 4 `\cvevent`, URLs preprocesadas, sección Publicaciones presente.

- [x] **5. Implementar `pdf.py`.** ✔ Hecho.
  `latexmk` + `cwd=output_dir` (nunca `os.chdir`), staging de assets (`.cls`/`.cfg`) en `output/`,
  biber orquestado por latexmk, `latexmk -c` para limpiar auxiliares conservando el PDF. → **CA4**.
  _Verificado EN el contenedor `Auto_CV_dev`:_ compiló `output/cv_final.pdf` (140 KB, 1 página, 4
  `\cvevent`), `.bcf` de biber generado, **cero referencias/citas sin resolver**. Docstring pasado a
  raw string (sin `SyntaxWarning`, listo para el gate CA7).
  _Nota de infra:_ el Dockerfile **raíz** ganó el toolchain LaTeX (texlive mínimo + biber + latexmk) —
  antes no lo tenía. Se instaló temporalmente en el contenedor vivo para verificar; queda permanente
  al hacer *Rebuild Container*.

- [x] **6. Crear el CLI orquestador `cli.py`.** ✔ Hecho.
  `build --lang es|en|both` encadena `load → (translate si aplica) → render → compile` (argparse, sin
  sumar deps; `click` es pulido opcional del roadmap). Nombra la salida por idioma (`cv_final_es.pdf`).
  `pdf.py._clean_aux` mejorado: `output/` queda solo con `.pdf` + `.tex`. → **CA1**.
  _Verificado en contenedor:_ `python -m src.autocv.cli build --lang es` genera `output/cv_final_es.pdf`
  en un comando. (La ruta `both`/`en` usa DeepL en vivo → se ejercita en el smoke de aceptación / al correrlo.)

- [x] **7. Tests reales + gate.** ✔ Hecho.
  23 tests (`tests/`): config (key lazy, labels), data_loader (faltante/vacío), translator con DeepL
  **mockeado** (lote, cache hit/miss, skip-keys, glosario), renderer (escape LaTeX, delimitadores),
  cli (slug del nombre) y smoke de aceptación (pipeline ES con compile mockeado → CA1/CA5). Gate verde:
  **ruff (format + lint) + mypy + pytest** configurado en `.pre-commit-config.yaml`. → **CA7** ✓.

- [x] **8. Higiene.** ✔ Hecho.
  `.gitignore` real (output/, .cache/, aux LaTeX, data/en/, __pycache__, .env); **una** plantilla (`cv_ds`,
  sin el sample upstream); deps con **uv** (`pyproject.toml` + `uv.lock`, requirements.txt = Estado 0);
  scaffold full-stack de ClearNote podado. → **CA6** ✓.

- [x] **9. Documentar.** ✔ Hecho.
  README showcase (comando único, pipeline, metodología) + **6 ADRs** en `docs/decisions/` (CV como datos,
  sin DB, Jinja2+escape LaTeX, traducción lote/cache/glosario, presentación/layout/i18n, uv/Estado 0).
