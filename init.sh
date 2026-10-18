#!/usr/bin/env bash
# =============================================================================
# init.sh — Prepara el entorno de AutoCV (idempotente).
# -----------------------------------------------------------------------------
# Lo dispara el postCreateCommand del Dev Container. AutoCV es una herramienta
# CLI sin base de datos: todo lo que hace falta es instalar las dependencias
# con uv (declaradas en requirements.txt / pyproject.toml).
# =============================================================================
set -euo pipefail
cd "$(dirname "$0")"

echo "▶ Instalando dependencias con uv…"
uv sync

echo ""
echo "✓ Entorno listo. Genera tu CV con:"
echo "    uv run python -m src.autocv.cli build --lang both"
