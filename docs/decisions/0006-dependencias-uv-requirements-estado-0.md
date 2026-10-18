# ADR-0006: Dependencias con uv (requirements.txt = Estado 0)

- **Estado:** aceptada

## Contexto

AutoCV hereda de ClearNote_Dev la convención de **Estado 0 → Estado N**: un proyecto nace declarando sus
dependencias en `requirements.txt` (Estado 0, trazabilidad de lo que se pidió), y el Dev Container las
**materializa** con uv en `pyproject.toml` + `uv.lock` (Estado N). El runtime real es siempre uv, nunca pip.

## Decisión

- **Gestión con `uv`**: `pyproject.toml` declara las deps de runtime (pyyaml, jinja2, deepl, python-dotenv) y el
  grupo `dev` (pytest, ruff, mypy, pre-commit); `uv.lock` las fija para builds reproducibles. Se corre todo con
  `uv run`.
- **`requirements.txt` se conserva** como declaración de Estado 0 (trazabilidad), aunque la gestión real sea uv.
- **No se usa pip.**
- **Gate de calidad:** **ruff** (formateador + linter, reemplaza black + flake8) + **mypy** + **pytest**,
  orquestado con `pre-commit` (`.pre-commit-config.yaml`).

## Consecuencias

- **+** Builds reproducibles (`uv.lock`), entorno rápido de levantar, un solo comando (`uv sync`) instala todo.
- **+** El gate corre antes de cada commit; el código queda formateado y modernizado a Python 3.13 por ruff.
- **+** `requirements.txt` da trazabilidad del Estado 0 sin que pip intervenga.
- **−** Dualidad `requirements.txt` ↔ `pyproject.toml`: hay que mantenerlas coherentes (mismas deps).
- **−** Depende de uv en el entorno (viene en el Dev Container; fuera de él hay que instalarlo).
