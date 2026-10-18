# AutoCV — Diagnóstico y plan de reconstrucción

> **Estado:** proyecto *legacy* (construido sobre la vieja plantilla `ClearNote_Py_DA`).
> **Destino:** reconstruir sobre **`ClearNote_Dev`** (SDD), **sin** la capa de Postgres.
> Este documento es la **narración honesta** del proyecto: qué es, qué salió bien, qué salió mal
> y la intervención concreta para dejarlo bien hecho. Es el primer proyecto real con el que se
> prueba la efectividad de la familia de plantillas ClearNote.

---

## 1. Qué es AutoCV (la narración)

AutoCV genera un **CV bilingüe** a partir de datos estructurados:

```
data/es/*.yaml   ──DeepL──►   data/en/*.yaml
     │                              │
     └──────────► Jinja2 ◄──────────┘
                    │
              output/cv_final.tex ──pdflatex──► output/cv_final.pdf
```

- Los datos viven **modularizados por sección e idioma**: `personales`, `experiencia`, `educacion`,
  `certificaciones`, `publicaciones`, `aptitudes`, `otros` — un `.yaml` por sección, en `data/es` (fuente)
  y `data/en` (traducción).
- El **español es la fuente**; el inglés se deriva automáticamente vía la API de DeepL.
- El render usa **Jinja2 sobre LaTeX** (plantilla `altacv`) y compila a PDF con TeXLive.

### Su historia (por qué importa para entender los defectos)

AutoCV **nació sobre el scaffold de la plantilla de *análisis de datos*** (`ClearNote_Py_DA`). Las huellas siguen ahí:
el `README.md` original dice *"Plantilla Dev Container para Ciencia de Datos"*, el `devcontainer.json` se llama
`clearnote-py-da` y trae extensiones de Jupyter y **Django**. Es decir: **se construyó una herramienta de software
sobre un molde pensado para notebooks exploratorios.** Ese desajuste de origen explica casi todo lo que salió mal.

Después, `setup_autocv.py` generó un **blueprint modular limpio** (todos los archivos como *stubs* `# TODO`), y la
implementación ocurrió en **dos ráfagas que nunca se conectaron**. El resultado es un proyecto que *funciona a medias
si sabes exactamente qué dos scripts correr a mano*, pero que no tiene un flujo único ni la estructura que su propio
scaffold prometía.

---

## 2. Arquitectura, tal como quedó (mapa honesto)

```
                 BLUEPRINT PROMETIDO (setup_autocv.py)
   data_loader ─ translator ─ template_renderer ─ pdf_generator ─ config ─ utils ─ tests

                 LO QUE REALMENTE SE IMPLEMENTÓ
   ┌─ Mundo A (traducción) ─────────────┐   ┌─ Mundo B (generación) ──────────────┐
   │ translator.py  ──usa──►  config.py │   │ template_renderer.py = MONOLITO      │
   │ (SHA256 hash cache, DeepL vía       │   │ CVGenerator: load + render + compile │
   │  requests crudo)                    │   │ con su PROPIO main(), rutas hardcode │
   └─────────────────────────────────────┘   │ e IGNORA config.py y data_loader.py  │
                                              └──────────────────────────────────────┘
   STUBS VACÍOS (# TODO):  run.py · src/main.py · pdf_generator.py · validation.py ·
                           file_utils.py · tests/test_*.py
   HUÉRFANOS (bien hechos pero nadie los usa):  data_loader.py · config.py (parcial)
```

El archivo llamado `template_renderer.py` **no es un renderer**: es la aplicación entera metida en una clase
`CVGenerator` con su propio `main()`. Mientras tanto, el `pdf_generator.py`, `main.py` y `run.py` — donde *debería*
vivir esa lógica — están vacíos.

---

## 3. ✅ Lo que salió bien

1. **Modelo de datos limpio.** Un YAML por sección y por idioma (`data/es`, `data/en`). Fácil de editar, versionar y diff-ear.
2. **Fuente única + derivación.** ES como verdad, EN generado. La dirección del flujo es correcta.
3. **Cache por hash.** `translator.py` calcula SHA256 del YAML fuente y **evita re-traducir lo que no cambió** — buena
   intención de ingeniería (ahorra cuota de DeepL y tiempo).
4. **`config.py` es sólido.** Acceso por clave-punto (`config.get('latex.engine')`), validación de secciones requeridas,
   y **oculta la API key** en `__str__`. Es código de calidad.
5. **`data_loader.py` está bien hecho.** Carga por sección o idioma completo, maneja YAML vacío/faltante con errores claros.
6. **Jinja2 con delimitadores personalizados** (`((* *))`, `((( )))`, `((# #))`) para **no chocar con las llaves de LaTeX**.
   Es una decisión correcta y no obvia — mucha gente tropieza justo aquí.
7. **Seguridad correcta.** El `.env` **no** está rastreado en git, la API key de DeepL **no** se filtró, y `config.__str__`
   la enmascara. Este pilar está bien.
8. **Entorno reproducible.** El Dockerfile trae TeXLive completo (con `texlive-lang-spanish`/`-english` y `latexmk`),
   y el PDF efectivamente se genera.
9. **CLI usable** en el monolito (`--language`, `--template`, `--output`, `--no-clean` vía `argparse`).

---

## 4. ❌ Lo que salió mal

### Arquitectura y cableado
1. **Dos arquitecturas paralelas que no se hablan** (ver §2). El blueprint modular quedó a medias y la app real es un
   monolito que **reimplementa** la carga de datos e **ignora** `config.py`/`data_loader.py`.
2. **No hay orquestador.** `run.py`, `src/main.py` y `pdf_generator.py` son `# TODO`. **Nadie ejecuta el flujo completo**
   traducir → renderizar → compilar. Hay que correr `translator.py` a mano y luego `template_renderer.py` a mano.
3. **Módulos huérfanos = código muerto.** `data_loader.py` y `config.py` (buenos) no los usa el monolito;
   `config.yaml` define `paths`/`engine` que el monolito **hardcodea aparte** → **dos realidades de configuración**.

### Calidad
4. **Cero tests reales.** Los tres `tests/test_*.py` son `# TODO`. `mypy`/`black`/`flake8` están declarados pero **sin gate**.
5. **`validation.py` y `file_utils.py` vacíos** — el proyecto no valida la forma de los datos de entrada.
6. **Doble docstring en `config.py`** (el header `# TODO` quedó pegado sobre la implementación real): huella de crecer sin limpiar.

### LaTeX / PDF
7. **Falta `biber`.** La plantilla usa **biblatex** (`pubs-authoryear.cfg`, y quedaron `cv_final.bcf` + `.run.xml` en `output/`),
   pero `compile_pdf` corre **solo `pdflatex` ×2** y **nunca `biber`** → la lista de **publicaciones muy probablemente no resuelve**
   (aparecen vacías o con `[?]`). Este es un síntoma concreto del "salió mal".
8. **`compile_pdf` usa `os.chdir`** (estado global del proceso) en vez de `cwd=` — frágil, aunque restaura en `finally`.

### Higiene del repositorio
9. **`.gitignore` es un `# TODO`** que solo ignora `.env`. Quedaron **versionados** (92 archivos, muchos basura):
   - `__pycache__/*.pyc` (5)
   - artefactos de build: `output/cv_final.{pdf,tex,bcf,run.xml}`
   - la **cache** `data/en/*.hash` (7)
   - el **sample completo de altacv** duplicado en `templates/` (`sample.*`, `mmayer.*`, imágenes, `x.log`, `sample.log`…)
10. **Templates duplicados.** `templates/altacv` y `templates/cv_ds` son casi el mismo paquete upstream. Y `output/`
    mezcla **proceso** (`.tex`, `.bcf`) con **entregable** (`.pdf`) sin separarlos.

### Drift heredado del scaffold equivocado
11. `devcontainer.json` se llama `clearnote-py-da`, trae extensiones de **Django/Jupyter** irrelevantes, usa **`pip`** (no `uv`)
    y `remoteUser: root`.
12. `config.yaml` apunta a `style_file: estilos/cv_styles.sty` **que no existe** (altacv usa su `.cls`).
13. Dockerfile: el comentario dice "3.13.5" pero `FROM` es `3.13.2`, y hay **espacios tras el `\`** en varias líneas del
    `RUN` (riesgo de romper la continuación de línea — revisar).

### DeepL
14. **Reinventa el cliente.** `requirements.txt` trae la lib oficial **`deepl`**, pero `translator.py` usa **`requests` crudo**
    contra `api-free.deepl.com`, y **traduce string por string** (una petición HTTP por cada texto, recursivamente) → lento
    y **quema cuota**. Además **ignora** `timeout`/`max_retries`/`formality` que sí están definidos en `deepl_config.yaml`.

---

## 5. 🔧 La intervención — reconstruir sobre `ClearNote_Dev` (SDD)

> Regla de oro: **AutoCV no tiene base de datos.** Se usa `ClearNote_Dev` pero **sin activar** su capa de Postgres
> (`docker-compose` de DB, `alembic.ini`, `infra/db`, `secrets/db_password.txt`, gobernanza). Queda el Dev Container,
> el `src/` estructurado, `spec/` (SDD), `tests/` y `docs/`.

### 5.1 `spec/constitution/` — las reglas duras
- **ES es la única fuente de verdad.** `data/en` es **derivado**; jamás se edita a mano.
- **Un solo comando reproduce todo** (traducir → render → compilar). Nada de "corré estos dos scripts".
- **Proceso ≠ entregable.** Intermedios (`.tex`, `.bcf`, `.aux`) fuera del entregable; el PDF final aparte.
- **Nada de secretos ni artefactos en git.** Solo fuentes.

### 5.2 `spec/features/` — los contratos
- **Esquema de datos del CV**: forma esperada de cada sección (`personales`, `experiencia`, …) como contrato validable.
- **Pipeline**: `load → (translate si falta/cambió) → render → compile`.
- **Contrato de traducción**: batch (no string por string), `formality`/`timeout`/`retries` desde el YAML, glosario opcional.

### 5.3 `src/` — módulos reales **y conectados**
| Módulo | Qué hacer |
|---|---|
| `config` | Adaptar el `config.py` bueno (quitar el doble docstring). **Única** fuente de rutas/idiomas/engine. |
| `data_loader` | Adaptar el `data_loader.py` bueno. El pipeline lo usa (no se reimplementa). |
| `translator` | Migrar a la **lib oficial `deepl`**; **traducir en lote**; respetar `timeout`/`retries`/`formality`; mover el `.hash` a un **cache fuera de `data/`** (p. ej. `.cache/`). |
| `renderer` | Extraer **solo** el Jinja→`.tex` del monolito (conservar los delimitadores LaTeX). |
| `pdf` | Implementarlo **de verdad**: usar **`latexmk -pdf`** (ya está en el Dockerfile) que **orquesta `biber` solo** → mata el bug del bibliography. Usar `cwd=`, no `os.chdir`. |
| `cli` (reemplaza `run.py`/`main.py`) | Orquestador único: `autocv build --lang es|en|both` = `load → translate → render → compile`. |

### 5.4 `tests/` — reales, con gate
- `data_loader`: YAML vacío / faltante / malformado.
- `translator`: **mock de DeepL**, hash *hit/miss*, batch.
- `renderer`: render **determinista** de un fixture (sin tocar red ni LaTeX).
- **smoke** del pipeline completo.
- Gate `black` + `flake8` + `mypy` + `pytest` en **pre-commit**.

### 5.5 Higiene y assets
- **`.gitignore` real**: `__pycache__/`, `*.pyc`, `.env`, `output/**`, `*.aux`, `*.log`, `*.bcf`, `*.run.xml`, `.cache/`.
- **Un solo** paquete de plantilla (elegir `cv_ds` o `altacv`), **sin** el sample upstream (`sample.*`, `mmayer.*`, imágenes, `x.log`).
- Separar `output/tex/` (intermedios) del **PDF final**.
- `.devcontainer` de Dev: **`uv`** en vez de `pip`, nombre correcto, sin extensiones Django, con `latexmk`.

---

## 6. Checklist de migración

- [ ] Descargar `ClearNote_Dev` desde GitHub y copiar esta carpeta a `docs/AutoCV-legacy/` (referencia).
- [ ] Desactivar la capa Postgres (compose DB, alembic, infra/db, secret de DB).
- [ ] Escribir `spec/constitution` + `spec/features` (§5.1–5.2).
- [ ] Portar `config.py` y `data_loader.py` (los buenos) a `src/`.
- [ ] Reescribir `translator` (lib `deepl` + batch + cache fuera de `data/`).
- [ ] Extraer `renderer` del monolito; implementar `pdf` con `latexmk` (biber resuelto).
- [ ] Crear el **CLI orquestador** único.
- [ ] Escribir los tests reales + activar pre-commit.
- [ ] `.gitignore` real + limpiar templates y artefactos.
- [ ] Verificar que las **publicaciones** ahora sí aparecen en el PDF.

---

## 7. Lecciones (qué no repetir)

- **La plantilla correcta importa desde el minuto cero.** AutoCV es una *herramienta*, no un análisis: iba en `ClearNote_Dev`,
  no en la de datos. El molde equivocado arrastró todo el drift.
- **Un scaffold de stubs no es una arquitectura.** Prometer módulos y luego colapsarlos en un monolito deja huérfanos y `# TODO`
  por todas partes. SDD evita esto: primero el contrato, luego el código que lo cumple.
- **Si hay dos formas de correr el proyecto, no hay ninguna.** Un solo comando, un solo orquestador.
- **La higiene se define antes del primer commit.** `.gitignore` primero; los artefactos nunca entran al repo.
- **No reinventes clientes de API** cuando la lib oficial ya está en tus dependencias.
