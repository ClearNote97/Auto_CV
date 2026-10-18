# AGENTS.md — AutoCV

> **Entrada estándar que los agentes de IA auto-leen.** El **contrato de trabajo** (cómo colaboramos,
> agnóstico de herramienta) vive en **[`README_AGENTS.md`](./README_AGENTS.md)** — léelo **primero**.
> Este archivo suma solo lo **específico de este proyecto**.

## Qué es este proyecto

**AutoCV**: generador de CV bilingüe (ES→EN) a PDF desde datos YAML, bajo **Spec-Driven Development (SDD)**.
Es una **herramienta CLI, sin base de datos**. Ver [`README.md`](./README.md) (qué es / cómo correr) y
[`spec/`](./spec/) (el contrato: constitución + features).

Construido sobre la plantilla [ClearNote_Dev](https://github.com/ClearNote97/ClearNote_Dev) — de ahí vienen
la estructura SDD, el Dev Container y el roster de agentes — pero **sin** su capa full-stack (DB, web).

## Roster de agentes (materialízalo)

Este proyecto declara los agentes que necesita, de forma agnóstica, en **[`spec_agents/`](./spec_agents/)**.
Si vas a trabajar con subagentes, **materialízalos a tu formato nativo** siguiendo el protocolo de
`spec_agents/README.md`: por cada `<id>.yaml`, si ya existe un agente para ese rol en tu harness **pregunta**
(reusar / reemplazar / complementar) antes de crearlo. Nunca pises en silencio.

## Reglas específicas al trabajar aquí

- **SDD manda:** nada se construye sin spec. El flujo es **Constitución → Spec → Plan → Tareas → Implementación**.
  `spec/` es **prescriptivo** (lo que DEBE ser verdad); `docs/` es **descriptivo** (cómo y por qué quedó así).
- **ES es la única fuente de verdad.** `data/en` es **derivado** (DeepL); jamás se edita a mano.
- **Un solo comando reproduce todo:** `uv run python -m src.autocv.cli build`. Nada de pasos manuales sueltos.
- **Nada de secretos ni artefactos de build en git.** Solo fuentes.

## Cómo correr

- **Entorno:** *Reopen in Container* (VS Code + Dev Containers). El `postCreateCommand` (`./init.sh`) prepara
  el entorno con **`uv`** (`uv sync`).
- **Generar el CV:** `uv run python -m src.autocv.cli build --lang es|en|both`.
- La versión en inglés necesita `DEEPL_API_KEY` en `.env` (ver `.env.example`).

## Stack

Python 3.13 + **`uv`** · **Jinja2** (render) · **DeepL** (traducción) · **LaTeX / [AltaCV](https://github.com/liantze/AltaCV)**
+ `latexmk` + `biber` (PDF). Entorno: Docker + Dev Containers.
