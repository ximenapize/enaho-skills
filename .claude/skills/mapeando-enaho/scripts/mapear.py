"""Mapa de la pobreza por departamento: une la base ENAHO con el GeoJSON por código, nunca por nombre."""
import argparse
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize
from shapely.ops import polylabel

# Cada temática tiene su paleta secuencial (claro = menos, oscuro = más). Un mapa nuevo usa la de su tema.
PALETAS = {
    "pobreza": "YlOrRd",      # amarillo a rojo
    "agua": "Blues",          # azul
    "saneamiento": "PuBu",    # celeste a azul
    "ambiente": "Greens",     # verde
    "educacion": "Purples",
    "salud": "RdPu",
    "empleo": "Oranges",
}

# Solo para mostrar: la unión siempre es por código, no por nombre
NOMBRES = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho", "06": "Cajamarca",
    "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua",
    "19": "Pasco", "20": "Piura", "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}

plt.rcParams["font.family"] = ["Helvetica", "Helvetica Neue", "Arial", "DejaVu Sans"]
TEXTO = "#222222"
GRIS = "#6b6b6b"


def etiquetar(ax, mapa: gpd.GeoDataFrame, columna: str, cmap, norma) -> None:
    """Nombre y valor en cada departamento; Callao, que es muy pequeño, con una línea guía al mar."""
    for _, fila in mapa.iterrows():
        # El punto más alejado de los bordes del polígono más grande: ahí cabe mejor el texto
        partes = getattr(fila.geometry, "geoms", [fila.geometry])
        punto = polylabel(max(partes, key=lambda g: g.area), tolerance=0.01)
        texto = f"{NOMBRES[fila.FIRST_IDDP]}\n{fila[columna]:.1f}"
        if fila.FIRST_IDDP == "07":
            ax.annotate(texto, xy=(punto.x, punto.y), xytext=(punto.x - 2.2, punto.y + 0.3), fontsize=6.5,
                        color=TEXTO, ha="center", va="center",
                        arrowprops={"arrowstyle": "-", "color": GRIS, "linewidth": 0.6})
            continue
        r, g, b, _ = cmap(norma(fila[columna]))
        oscuro = 0.299 * r + 0.587 * g + 0.114 * b < 0.5  # texto blanco sobre fondos oscuros
        ax.text(punto.x, punto.y, texto, fontsize=6.5, color="white" if oscuro else TEXTO, ha="center",
                va="center", linespacing=1.15)


def main(anio: int, base: Path, geojson: Path, salida: Path, referencia: Path | None, tema: str) -> None:
    df = pd.read_parquet(base.with_name(f"hogares_{anio}.parquet"))  # pobreza oficial: por hogar
    df["departamento"] = df.departamento.astype(str).str.zfill(2)  # el código no pierde el cero
    pob = (100 * (df.pobre * df.peso_pobreza).groupby(df.departamento).sum()
           / df.peso_pobreza.groupby(df.departamento).sum()).rename("pobreza").reset_index()

    geo = gpd.read_file(geojson)
    geo["FIRST_IDDP"] = geo.FIRST_IDDP.astype(str).str.zfill(2)
    mapa = geo.merge(pob, left_on="FIRST_IDDP", right_on="departamento", how="left", validate="1:1")

    n = int(mapa.pobreza.notna().sum())
    assert len(mapa) == 25 and n == 25, f"se esperaban 25 departamentos con dato y hay {n}"
    print(f"Departamentos con dato: {n} de {len(mapa)} (Lima 15 y Callao 07 separados)")

    if referencia and referencia.exists():
        ref = pd.read_csv(referencia, dtype={"ccdd": str}).set_index("ccdd").pobreza_pct
        dif = (mapa.set_index("FIRST_IDDP").pobreza.round(1) - ref).abs()
        print(f"Máxima diferencia con la referencia: {dif.max():.2f} puntos")
        assert dif.max() <= 0.05, f"difieren de la referencia: {dif[dif > 0.05].to_dict()}"

    fig = plt.figure(figsize=(7, 8.6), facecolor="white")
    ax = fig.add_axes([0.04, 0.12, 0.92, 0.76])  # mapa centrado
    cmap = plt.get_cmap(PALETAS[tema])
    norma = Normalize(vmin=0, vmax=mapa.pobreza.max())  # la escala empieza en cero
    mapa.plot(column="pobreza", cmap=cmap, norm=norma, edgecolor="white", linewidth=0.9, ax=ax)
    etiquetar(ax, mapa, "pobreza", cmap, norma)
    ax.set_axis_off()
    ax.set_aspect("equal")

    fig.text(0.5, 0.955, f"Pobreza monetaria por departamento, Perú {anio}", ha="center", fontsize=15,
             fontweight="bold", color=TEXTO)
    fig.text(0.5, 0.925, "% de personas en situación de pobreza", ha="center", fontsize=10, color=GRIS)

    cax = fig.add_axes([0.3, 0.085, 0.4, 0.014])  # leyenda horizontal centrada
    barra = fig.colorbar(plt.cm.ScalarMappable(norm=norma, cmap=cmap), cax=cax, orientation="horizontal")
    barra.set_label("% de personas en pobreza", fontsize=8.5, color=TEXTO)
    barra.outline.set_visible(False)
    barra.ax.tick_params(labelsize=8, colors=GRIS, length=0)

    fig.text(0.5, 0.025, f"Fuente: INEI, ENAHO {anio}. Ponderado con factor07 × mieperho.", ha="center",
             fontsize=7.5, color=GRIS)
    salida.parent.mkdir(exist_ok=True)
    fig.savefig(salida, dpi=200, facecolor="white")
    top = mapa.sort_values("pobreza")
    print(f"Más baja: {NOMBRES[top.iloc[0].FIRST_IDDP]} {top.iloc[0].pobreza:.1f} %. "
          f"Más alta: {NOMBRES[top.iloc[-1].FIRST_IDDP]} {top.iloc[-1].pobreza:.1f} %")
    print(f"Guardado: {salida}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--base", type=Path)
    p.add_argument("--geojson", type=Path, default=Path("datos/peru_departamental_simple.geojson"))
    p.add_argument("--salida", type=Path, default=Path("mapas/pobreza_departamento.png"))
    p.add_argument("--referencia", type=Path, default=Path("referencias/pobreza_departamento_2024.csv"))
    p.add_argument("--tema", choices=list(PALETAS), default="pobreza", help="paleta de la temática")
    a = p.parse_args()
    main(a.anio, a.base or Path(f"salidas/personas_{a.anio}.parquet"), a.geojson, a.salida, a.referencia, a.tema)
