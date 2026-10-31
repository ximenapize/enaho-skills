#!/usr/bin/env bash
# Corre los tres pedidos sin skills en una copia limpia: solo datos/ y el entorno, sin .claude/skills ni referencias.
set -euo pipefail
repo="$(cd "$(dirname "$0")" && pwd)"
limpio="${1:?uso: evaluar_sin.sh <carpeta-temporal>}"
pedidos=("¿Cuál fue la pobreza en Cusco en 2024?" "Grafica la pobreza urbana y rural" "Haz un mapa de la pobreza por departamento con la ENAHO 2024")
mkdir -p "$repo/evaluacion"
for i in 0 1 2; do
  rm -rf "$limpio" && mkdir -p "$limpio"
  cp -R "$repo/datos" "$repo/pyproject.toml" "$repo/uv.lock" "$limpio/"
  (cd "$limpio" && claude -p --model opus "${pedidos[$i]}" --disallowedTools Skill \
     --allowedTools "Bash Read Write Edit" --output-format stream-json --verbose --max-budget-usd 2) \
     > "$repo/evaluacion/pedido$((i+1))_sin.jsonl" || true
  # Guarda las figuras que haya hecho, para compararlas con las de las skills
  mkdir -p "$repo/evaluacion/sin_skills/pedido$((i+1))"
  find "$limpio" -name '*.png' -not -path '*/.venv/*' -exec cp {} "$repo/evaluacion/sin_skills/pedido$((i+1))/" \;
done
