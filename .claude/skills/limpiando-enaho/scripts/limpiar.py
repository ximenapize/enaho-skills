"""Limpia la ENAHO: une el módulo 02 (personas) con la sumaria (módulo 34) y valida la pobreza oficial."""
import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd

LLAVES_HOGAR = ["conglome", "vivienda", "hogar"]
OFICIAL = {2024: {"pobreza": 27.6, "personas": 108_664}}


def leer_dta(zip_path: Path, nombre: str) -> pd.DataFrame:
    """Lee un .dta dentro del zip sin extraerlo, con las llaves como texto y columnas en minúscula."""
    with zipfile.ZipFile(zip_path) as z:
        ruta = next(n for n in z.namelist() if n.endswith(nombre))
        df = pd.read_stata(io.BytesIO(z.read(ruta)), convert_categoricals=False)
    df.columns = [c.lower() for c in df.columns]  # 'aÑo' llega con Ñ mayúscula
    for c in LLAVES_HOGAR + ["codperso"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    return df


def main(anio: int, datos: Path, salidas: Path) -> None:
    pers = leer_dta(datos / f"966-Modulo02.zip", f"enaho01-{anio}-200.dta")
    hog = leer_dta(datos / f"966-Modulo34.zip", f"sumaria-{anio}.dta")
    n_modulo02 = len(pers)

    # 1. Residentes habituales
    pers = pers[((pers.p204 == 1) & (pers.p205 == 2)) | ((pers.p204 == 2) & (pers.p206 == 1))]

    # 2. Llaves únicas antes de unir
    assert not hog.duplicated(LLAVES_HOGAR).any(), "la sumaria tiene hogares duplicados"
    assert not pers.duplicated(LLAVES_HOGAR + ["codperso"]).any(), "personas duplicadas"

    # 3. Unir personas (m) con hogares (1); la sumaria solo aporta pobreza y gasto
    hogares = hog.copy()  # sumaria completa: la pobreza oficial se calcula por hogar
    hog = hog[LLAVES_HOGAR + ["pobreza", "mieperho", "factor07"]]
    n0 = len(pers)
    df = pers.merge(hog, on=LLAVES_HOGAR, how="left", validate="m:1")
    assert len(df) == n0, "la unión cambió el número de filas"
    sin_hogar = int(df.pobreza.isna().sum())

    # 4. Variables derivadas (ubigeo y departamento como texto de 2 dígitos)
    df["ubigeo"] = df.ubigeo.astype(str).str.zfill(6)
    df["departamento"] = df.ubigeo.str[:2]
    df["urbano"] = df.estrato <= 5
    df["pobre"] = (df.pobreza <= 2).where(df.pobreza.notna())

    # 5. Base de hogares con el peso oficial de pobreza (factor07 x mieperho)
    hogares["ubigeo"] = hogares.ubigeo.astype(str).str.zfill(6)
    hogares["departamento"] = hogares.ubigeo.str[:2]
    hogares["urbano"] = hogares.estrato <= 5
    hogares["pobre"] = hogares.pobreza <= 2
    hogares["peso_pobreza"] = hogares.factor07 * hogares.mieperho

    # 6. Validación contra la cifra oficial
    w = df.dropna(subset=["pobre"])
    pobreza_personas = 100 * (w.pobre * w.facpob07).sum() / w.facpob07.sum()
    pobreza = 100 * (hogares.pobre * hogares.peso_pobreza).sum() / hogares.peso_pobreza.sum()
    ref = OFICIAL.get(anio)
    lineas = [
        f"ENAHO {anio}",
        f"Filas del módulo 02: {n_modulo02:,}",
        f"Residentes habituales: {len(df):,}",
        f"Hogares en la sumaria: {len(hog):,}",
        f"Personas sin hogar en la sumaria: {sin_hogar}",
        f"Pobreza monetaria (hogares, factor07 x mieperho): {pobreza:.2f} %",
        f"Pobreza monetaria (personas, facpob07): {pobreza_personas:.2f} %",
    ]
    if ref:
        ok_n = len(df) == ref["personas"]
        ok_p = abs(pobreza - ref["pobreza"]) <= 0.1 and abs(pobreza_personas - ref["pobreza"]) <= 0.1
        lineas += [
            f"Oficial INEI: {ref['pobreza']} % y {ref['personas']:,} personas",
            f"Personas: {'OK' if ok_n else 'FALLA'}",
            f"Pobreza dentro de 0.1 puntos: {'OK' if ok_p else 'FALLA'}",
        ]
    salidas.mkdir(exist_ok=True)
    (salidas / "validacion.txt").write_text("\n".join(lineas) + "\n")
    print("\n".join(lineas))
    assert not ref or (ok_n and ok_p), "la validación falló: revisa factor y filtro de residentes"

    df.to_parquet(salidas / f"personas_{anio}.parquet", index=False)
    hogares.to_parquet(salidas / f"hogares_{anio}.parquet", index=False)
    print(f"Guardado: personas_{anio}.parquet y hogares_{anio}.parquet en {salidas}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--datos", type=Path, default=Path("datos"))
    p.add_argument("--salidas", type=Path, default=Path("salidas"))
    a = p.parse_args()
    main(a.anio, a.datos, a.salidas)
