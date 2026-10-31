"""Gráfico de barras de la pobreza ENAHO por área, sexo o grupo de edad, ponderado con facpob07."""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

GRUPOS = {
    "area": ("urbano", "Pobreza monetaria por área de residencia", {True: "Urbano", False: "Rural"}),
    "sexo": ("p207", "Pobreza monetaria por sexo", {1: "Hombre", 2: "Mujer"}),
    "edad": ("grupo_edad", "Pobreza monetaria por grupo de edad", None),
}
# Un solo color por temática, el tono medio-oscuro de la paleta que usa mapeando-enaho para ese tema
COLORES = {
    "pobreza": "#d7301f",      # rojo (YlOrRd)
    "agua": "#2171b5",         # azul (Blues)
    "saneamiento": "#3690c0",  # celeste-azul (PuBu)
    "ambiente": "#238b45",     # verde (Greens)
    "educacion": "#6a51a3",    # morado (Purples)
    "salud": "#ce1256",        # rosado (RdPu)
    "empleo": "#d94801",       # naranja (Oranges)
}

plt.rcParams["font.family"] = ["Helvetica", "Helvetica Neue", "Arial", "DejaVu Sans"]
TEXTO = "#222222"
GRIS = "#6b6b6b"


def pobreza_por(df: pd.DataFrame, col: str, peso: str) -> pd.Series:
    """% de personas pobres por grupo, siempre ponderado."""
    d = df.dropna(subset=["pobre", col])
    num = (d.pobre * d[peso]).groupby(d[col]).sum()
    den = d[peso].groupby(d[col]).sum()
    return 100 * num / den


def main(por: str, base: Path, salida: Path, anio: int, tema: str) -> None:
    # área: pobreza oficial por hogar (factor07 x mieperho); sexo y edad: personas con facpob07
    if por == "area":
        df, peso = pd.read_parquet(base.with_name(f"hogares_{anio}.parquet")), "peso_pobreza"
    else:
        df, peso = pd.read_parquet(base), "facpob07"
    col, titulo, etiquetas = GRUPOS[por]
    if por == "edad":
        df["grupo_edad"] = pd.cut(df.p208a, [-1, 17, 29, 59, 200], labels=["0-17", "18-29", "30-59", "60 y más"])
    serie = pobreza_por(df, col, peso)
    if etiquetas:
        serie.index = [etiquetas[i] for i in serie.index]
    serie = serie.sort_values(ascending=False)  # barras ordenadas

    fig = plt.figure(figsize=(7, 5), facecolor="white")
    ax = fig.add_axes([0.1, 0.14, 0.8, 0.66])  # gráfico centrado
    barras = ax.bar(serie.index.astype(str), serie.values, color=COLORES[tema], width=0.6)  # un solo color
    ax.set_ylim(0, serie.max() * 1.15)  # barras desde cero
    ax.bar_label(barras, labels=[f"{v:.1f} %" for v in serie.values], padding=4, fontsize=10,
                 fontweight="bold", color=TEXTO)  # valor en cada barra
    ax.set_ylabel("% de personas en pobreza", fontsize=9, color=GRIS)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(axis="x", length=0, labelsize=10, colors=TEXTO, pad=6)
    ax.tick_params(axis="y", length=0, labelsize=8, colors=GRIS)
    ax.yaxis.grid(True, color="#eeeeee", linewidth=0.8)
    ax.set_axisbelow(True)

    fig.text(0.5, 0.93, f"{titulo}, Perú {anio}", ha="center", fontsize=14, fontweight="bold", color=TEXTO)
    fig.text(0.5, 0.875, "% de personas en situación de pobreza", ha="center", fontsize=10, color=GRIS)
    ponderado = "factor07 × mieperho" if peso == "peso_pobreza" else peso
    fig.text(0.5, 0.03, f"Fuente: INEI, ENAHO {anio}. Ponderado con {ponderado}.", ha="center", fontsize=7.5,
             color=GRIS)
    salida.parent.mkdir(exist_ok=True)
    fig.savefig(salida, dpi=200, facecolor="white")
    print(serie.round(1).to_string())
    print(f"Guardado: {salida}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--por", choices=list(GRUPOS), required=True)
    p.add_argument("--anio", type=int, default=2024)
    p.add_argument("--base", type=Path)
    p.add_argument("--salida", type=Path)
    p.add_argument("--tema", choices=list(COLORES), default="pobreza", help="color de la temática")
    a = p.parse_args()
    main(a.por, a.base or Path(f"salidas/personas_{a.anio}.parquet"), a.salida or Path(f"figuras/pobreza_{a.por}_{a.anio}.png"), a.anio, a.tema)
