# Feature 001 — Pipeline de CV reproducible en un comando

> QUÉ hace y qué debe ser verdad. El CÓMO vive en `plan.md`; los pasos en `tasks.md`.

## Objetivo

Que un solo comando reconstruya el CV de punta a punta —cargar datos ES, traducir a EN solo lo que
cambió, renderizar LaTeX y compilar el PDF— reemplazando los dos scripts sueltos del legacy por un
pipeline único y conectado.

## Alcance

- **Incluye:** orquestador CLI único; módulos reales y conectados (`config`, `data_loader`, `translator`,
  `renderer`, `pdf`); traducción en lote con cache por hash fuera de `data/`; compilación con `latexmk`
  (biber resuelto); una sola plantilla vendorizada; `.gitignore` real; mover el código viejo a
  `docs/AutoCV-legacy/`.
- **No incluye:** validación profunda de esquema de datos (→ feature 002), glosario DeepL y tuning de
  formality/retries (→ feature 003), base de datos, API, UI. Ver `02_scope`.

## Criterios de aceptación (lo que DEBE ser verdad)

- [ ] **CA1 — Un comando.** Dado `data/es/*.yaml` poblado y `DEEPL_API_KEY` en `.env`, cuando corro
  `autocv build --lang both`, entonces se generan el PDF ES y el PDF EN en la carpeta de salida, sin
  pasos manuales intermedios.
- [ ] **CA2 — Fuente única + derivación.** Dado que edito una sección en `data/es/`, cuando reconstruyo,
  entonces `data/en/` de **esa** sección se regenera y las demás **no** se vuelven a traducir (cache hit
  por hash). `data/en/` nunca se edita a mano.
- [ ] **CA3 — Traducción en lote.** Dado un YAML con N textos, cuando se traduce, entonces se hace en
  **una** llamada por documento/lote (no una petición HTTP por string), respetando la cuota.
- [ ] **CA4 — Publicaciones resueltas.** Dado que la plantilla usa biblatex, cuando se compila, entonces
  el PDF muestra las publicaciones resueltas (sin `[?]` ni vacíos) — `latexmk` invoca `biber`.
- [ ] **CA5 — Una sola realidad de configuración.** Dado `config/config.yaml`, cuando corre el pipeline,
  entonces rutas/idiomas/engine salen **solo** de ahí (nada hardcodeado en paralelo).
- [ ] **CA6 — Higiene.** Dado un repo limpio, cuando corro el pipeline, entonces `git status` no muestra
  artefactos de build, cache ni secretos como cambios (todo ignorado).
- [ ] **CA7 — Gate verde.** `black --check`, `flake8`, `mypy` y `pytest` pasan en pre-commit.

## Actores y datos

- **Actores/roles:** usuario único (autor del CV). Sin roles ni multi-tenant.
- **Datos tocados:** solo archivos YAML en `data/es` (fuente) y `data/en` (derivado). **Sin base de datos,
  sin PII de terceros, sin RLS.** La cache de hash vive fuera de `data/` (p. ej. `.cache/`).

## Riesgos / preguntas abiertas

- **DeepL en lote con estructura anidada:** hay que preservar claves/estructura del YAML y traducir solo
  los valores string. Decidir estrategia (recorrer y juntar strings por documento) en `plan.md`.
- **Elección de plantilla:** `altacv` vs `cv_ds` (casi idénticas). Elegir UNA — propuesta: `altacv`.
- **Nombre del paquete/CLI:** propuesta `src/autocv/` + entry point `autocv`. Confirmar en Tarea 1.
