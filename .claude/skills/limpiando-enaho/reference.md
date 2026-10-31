# Referencia: ENAHO 2024

| Módulo | Archivo | Una fila por | Llaves |
|---|---|---|---|
| 02 miembros | `enaho01-2024-200.dta` | persona | `conglome`, `vivienda`, `hogar`, `codperso` |
| 34 sumaria | `sumaria-2024.dta` | hogar | `conglome`, `vivienda`, `hogar` |

La columna del año llega como `aÑo`; el script pasa todo a minúscula (`año`).

## Pasos fijos del script
1. Lee los .dta dentro del zip con `convert_categoricals=False` y las llaves como texto.
2. Residentes habituales: `(p204 == 1 & p205 == 2) | (p204 == 2 & p206 == 1)` (108,664 de 117,721).
3. Une personas con hogares con `merge(..., validate="m:1")`; no puede cambiar el número de filas.
4. `departamento = ubigeo[:2]`, `urbano = estrato <= 5`, `pobre = pobreza <= 2` (`pobreza` 1 = extremo, 2 = no extremo, 3 = no pobre).

## Pesos
- **Pobreza oficial por área y por departamento**: base de hogares, `peso_pobreza = factor07 * mieperho`. Da 27.58 % nacional, 24.8 % urbano, 39.3 % rural y reproduce la tabla departamental del INEI.
- **Personas** (sexo, edad, cualquier variable individual): `facpob07`. Da 27.53 % nacional.
- No uses `facpob07 * mieperho` ni `factor07 * mieperho` sobre filas de personas: multiplica el tamaño del hogar por cada miembro y sube la pobreza a ~33 %.

## Cifras de control
Pobreza nacional 27.6 %, extrema 5.5 %, urbano 24.8 %, rural 39.3 %, Lima Metropolitana (`dominio == 8`) 28.2 %, Cusco 18.5 %, Cajamarca 45.0 %, Ica 6.0 %. Hogares en la sumaria: 33,691.
