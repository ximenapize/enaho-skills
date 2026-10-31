---
name: graficando-enaho
description: Hace gráficos de barras de la pobreza de la ENAHO del INEI por área urbano/rural, sexo o grupo de edad, con las reglas de visualización del proyecto. Úsala cuando pidan graficar, comparar o visualizar pobreza o cifras de la ENAHO en barras (no mapas).
argument-hint: [area|sexo|edad]
---
# Graficar la ENAHO

1. Si no existe `salidas/personas_2024.parquet`, usa primero la skill `limpiando-enaho`.
2. Corre: `uv run ${CLAUDE_SKILL_DIR}/scripts/graficar.py --por $0` con `area`, `sexo` o `edad` según la pregunta.
3. Abre el PNG de `figuras/` y comprueba que cumple las reglas de abajo. Informa la cifra de cada barra al usuario.

## Reglas (el script ya las cumple; mantenlas si modificas algo)
- Pondera siempre: por área con la base de hogares y `peso_pobreza`, por sexo y edad con `facpob07`. Nunca un promedio simple.
- Barras que empiezan en cero y ordenadas de mayor a menor.
- Un solo color, el de la temática (`COLORES` en `graficar.py`, se elige con `--tema`): pobreza en rojo, agua en azul, saneamiento en celeste, ambiente en verde, educación en morado, salud en rosado y empleo en naranja. Son los mismos tonos que usa `mapeando-enaho`, para que gráficos y mapas combinen.
- El valor escrito en negrita sobre cada barra.
- Tipografía sans serif (Helvetica, o Arial si no está). Título, subtítulo y nota al pie centrados.
- Estilo limpio: sin bordes arriba, a la derecha ni a la izquierda, y líneas guía horizontales muy suaves.
- El título dice qué y cuándo (por ejemplo, «Pobreza monetaria por área de residencia, Perú 2024»).
- Nota al pie: «Fuente: INEI, ENAHO 2024», más el peso usado.
- PNG a 200 dpi en `figuras/`.

Para un mapa por departamento usa `mapeando-enaho`, no esta skill.
