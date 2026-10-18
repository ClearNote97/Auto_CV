# Roadmap

> Qué se construye, en qué orden y por qué. Cada hito aterriza en una feature (`spec/features/NNN_...`).
> Se lee contra el propósito (00) y el alcance (02).

## Ahora (en curso)

- [ ] **001 — Pipeline de CV reproducible en un comando** (`spec/features/001_cv-pipeline/`).
  El refactor central: reconstruir AutoCV sobre este ClearNote_Dev (sin DB) como módulos reales y
  **conectados** (`load → translate → render → compile`), matando las dos arquitecturas paralelas del
  legacy. Es el prerequisito de todo lo demás: hasta que exista un comando único, no hay dónde colgar
  validación ni glosarios.

## Siguiente

- [ ] **002 — Validación de esquema de datos.** Contrato validable por sección (`personales`, `experiencia`,
  …); falla claro y temprano si un YAML no tiene la forma esperada. (Hoy `validation.py` es un stub.)
- [ ] **003 — Traducción robusta.** Glosario DeepL opcional, `formality`/`timeout`/`retries` desde
  `deepl_config.yaml`, y cache movido a `.cache/` fuera de `data/`.

## Después (backlog priorizado)

- [ ] Segunda plantilla seleccionable por config (elegir entre `altacv` y una alternativa), sin activar dos a la vez.
- [ ] Idiomas adicionales además de EN (parametrizar `target`).
- [ ] `output/tex/` (intermedios) separado del PDF entregable.

## Fuera por ahora

> Ver `02_scope` → Fuera. No re-discutir.

- Base de datos / persistencia, API web, frontend, multi-tenant, editor visual del CV.
