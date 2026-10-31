---
name: limpiando-enaho
description: Limpia los módulos 34 (sumaria) y 02 (miembros) de la ENAHO del INEI y arma una base de personas y otra de hogares con pobreza y factores de expansión. Úsala cuando pidan limpiar, unir o analizar la ENAHO, calcular pobreza por departamento, área, sexo o edad, o cuando falte salidas/personas_2024.parquet.
argument-hint: [año]
---
# Limpiar la ENAHO

1. Si faltan `datos/966-Modulo34.zip` y `datos/966-Modulo02.zip`, pide al usuario bajarlos del INEI (`966` = ENAHO 2024) o descárgalos de `https://proyectos.inei.gob.pe/iinei/srienaho/descarga/STATA/966-Modulo34.zip` y `966-Modulo02.zip`.
2. Corre exactamente: `uv run ${CLAUDE_SKILL_DIR}/scripts/limpiar.py --anio ${1:-2024}`
3. Lee `salidas/validacion.txt`. Si la pobreza difiere del INEI en más de 0.1 puntos, o las personas no son 108,664, detente y avisa. No sigas con una base que no valida.
4. Responde con `salidas/personas_$0.parquet` (personas) o `salidas/hogares_$0.parquet` (hogares). Toda cifra va ponderada: ver `reference.md` para saber con qué peso.
5. Antes de usar una variable que no está en la base, lee `reference.md`.

No reescribas la lógica de limpieza a mano: el script ya fija las llaves, el filtro de residentes habituales y las uniones.
