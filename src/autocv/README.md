# src/autocv — paquete de dominio de AutoCV

Pipeline del CV: `load → translate → render → compile`. Es una **herramienta CLI**, no una app
full-stack, así que vive como paquete de dominio propio y **no usa** las capas
`backend/frontend/database/analytics` del scaffold (ver `spec/constitution/03_stack.md`).

| Módulo | Rol | Estado |
|---|---|---|
| `config.py` | Única fuente de rutas/idiomas/engine | esqueleto → Tarea 2 |
| `data_loader.py` | Carga YAML por sección/idioma | esqueleto → Tarea 2 |
| `translator.py` | ES→EN (lib `deepl`, lote, cache hash) | esqueleto → Tarea 3 |
| `renderer.py` | Jinja2 → `.tex` | esqueleto → Tarea 4 |
| `pdf.py` | `latexmk` → PDF (biber) | esqueleto → Tarea 5 |
| `cli.py` | Orquestador `autocv build` | esqueleto → Tarea 6 |

Contrato completo: `spec/features/001_cv-pipeline/`. Código de referencia (legacy): `docs/AutoCV-legacy/`.
Convención de import de este repo: `from src.autocv.<módulo> import ...`.
