# Evaluación: tres pedidos con y sin skills

Corridas del 31 de octubre de 2026 con `claude -p --model opus` (Claude Opus 5.5).

- **Con skills:** en este repositorio, con `evaluar.sh`.
- **Sin skills:** con `evaluar_sin.sh`, en una copia que solo tiene `datos/`, `pyproject.toml` y `uv.lock`, sin `.claude/skills/` ni `referencias/`.

## Resultados

| Pedido | Skills activadas | Cifra con skills | Cifra sin skills | ¿Ponderó? | La figura |
|---|---|---|---|---|---|
| ¿Cuál fue la pobreza en Cusco en 2024? | `limpiando-enaho` | **18.5 %** ✓ | **No respondió.** Intentó buscar en la web, se lo bloquearon y dijo que no recordaba la cifra | Con: sí, `factor07 × mieperho`. Sin: no calculó | No aplica |
| Grafica la pobreza urbana y rural | `graficando-enaho` → `limpiando-enaho` | 24.8 % y 39.3 % ✓ | 24.8 % y 39.3 % ✓ | Las dos, `factor07 × mieperho` | Con: cumple las reglas. Sin: dos colores, barras sin ordenar y una barra «Nacional» que no se pidió |
| Haz un mapa de la pobreza por departamento con la ENAHO 2024 | `mapeando-enaho` → `limpiando-enaho` | 25 departamentos; Cajamarca 45.0 %, Ica 6.0 % ✓ | Mismas cifras ✓; une por código | Las dos, `factor07 × mieperho` | Con: escala desde 0 y archivo en `mapas/`. Sin: escala desde ~6, que exagera las diferencias, y archivo en `resultados/` |

Costo según `claude -p`: con skills $0.21, $0.23 y $0.24; sin skills $0.11, $0.20 y $0.33.

## Qué aportan las skills

1. **Usan los datos que hay.** Sin skills, Opus no se dio cuenta de que podía calcular la pobreza de Cusco con los zip de `datos/` y se rindió. Con `limpiando-enaho` la calculó y la validó.
2. **Dos skills seguidas.** En los pedidos 2 y 3, la skill de gráfico o de mapa vio que faltaba la base limpia y llamó primero a `limpiando-enaho`.
3. **Mismo resultado para cualquiera.** Con skills, los archivos tienen siempre el mismo nombre y van en la misma carpeta, con las mismas reglas visuales. Sin skills, cada corrida inventó sus nombres y su estilo.
4. **Validación escrita.** Con skills queda `salidas/validacion.txt` con las 108,664 personas y la pobreza de 27.6 %. Sin skills, Opus usó solo la sumaria y nunca armó ni revisó la base de personas.

## Qué hizo bien la versión sin skills

Cuando calculó, Opus sin skills acertó: ponderó con `factor07 × mieperho`, separó urbano y rural con `estrato <= 5` y unió el mapa por código. Su mapa además traía el valor en cada departamento e intervalos de confianza. Esa idea la llevamos a `mapeando-enaho`, que ahora etiqueta cada departamento con su nombre y su valor.

## Archivos

- `evaluacion/sin_skills/`: las figuras que hizo Opus sin skills.
- Para repetir la prueba: `./evaluar.sh` y `./evaluar_sin.sh <carpeta-temporal>`. Las salidas crudas (`evaluacion/*.jsonl`) no se suben al repositorio.
