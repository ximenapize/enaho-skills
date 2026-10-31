#!/usr/bin/env bash
# Corre los tres pedidos con skills y guarda la salida de cada uno en evaluacion/.
# La comparación sin skills va en evaluar_sin.sh, en una copia sin .claude/skills: con solo
# --disallowedTools Skill, Claude encuentra la carpeta y corre los scripts igual.
set -euo pipefail
mkdir -p evaluacion
pedidos=("¿Cuál fue la pobreza en Cusco en 2024?" "Grafica la pobreza urbana y rural" "Haz un mapa de la pobreza por departamento con la ENAHO 2024")
for i in 0 1 2; do
  # Se borran las salidas para que cada corrida parta de cero
  rm -rf salidas/*.parquet salidas/validacion.txt figuras/*.png mapas/*.png
  claude -p --model opus "${pedidos[$i]}" --allowedTools "Bash Read Write Edit Skill" \
    --output-format stream-json --verbose --max-budget-usd 2 > "evaluacion/pedido$((i+1))_con.jsonl" || true
done
