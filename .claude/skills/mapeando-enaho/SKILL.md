---
name: mapeando-enaho
description: Hace el mapa de la pobreza por departamento del Perú con la ENAHO del INEI, uniendo la base limpia con los límites departamentales. Úsala cuando pidan un mapa, coropleta o distribución geográfica de la pobreza u otra cifra de la ENAHO por departamento.
argument-hint: [año]
---
# Mapear la ENAHO

1. Si no existe `salidas/hogares_2024.parquet`, usa primero la skill `limpiando-enaho`.
2. Si falta `datos/peru_departamental_simple.geojson`, bájalo de `https://raw.githubusercontent.com/d2cml-ai/Data-Science-Python/main/sessions/06-geoespacial/lab/Data/peru_departamental_simple.geojson`.
3. Corre: `uv run ${CLAUDE_SKILL_DIR}/scripts/mapear.py --anio ${1:-2024}`
4. Si el script falla porque no hay 25 departamentos con dato, no dibujes el mapa a medias: revisa la unión. Abre `mapas/pobreza_departamento.png` y resume los extremos.

## Reglas
- Une por código, nunca por nombre: `ubigeo[:2]` de la ENAHO con `FIRST_IDDP` del GeoJSON, ambos como texto de dos dígitos. «APURIMAC» no es «Apurímac» y un entero pierde el cero de «01».
- Exige 25 departamentos y ninguno sin dato.
- Lima (15) y Callao (07) van separados.
- Escala secuencial de claro a oscuro, desde 0, nunca arcoíris. Cada temática tiene su paleta (`PALETAS` en `mapear.py`, se elige con `--tema`): pobreza de amarillo a rojo (`YlOrRd`), agua en azul (`Blues`), saneamiento de celeste a azul (`PuBu`), ambiente en verde (`Greens`), educación en morado, salud en rosado y empleo en naranja. Un mapa de otra temática usa la paleta de su tema, no la de pobreza.
- Bordes blancos entre departamentos.
- Cada departamento lleva su nombre con tildes y su valor; el texto va blanco sobre los colores oscuros. Callao se etiqueta fuera, con una línea guía.
- Tipografía sans serif (Helvetica, o Arial si no está), con el título, la leyenda y la nota al pie centrados.
- Leyenda horizontal con la unidad: «% de personas en pobreza».
- Nota al pie con fuente y año; PNG a 200 dpi en `mapas/`.
- Valida contra `referencias/pobreza_departamento_2024.csv` (Cajamarca 45.0 %, Ica 6.0 %).
