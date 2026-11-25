"""Paleta, plantilla Plotly y constantes visuales del dashboard."""
import plotly.graph_objects as go
import plotly.io as pio

BURGUNDY = "#721C3B"
BURGUNDY_DARK = "#4A1128"
BURGUNDY_2 = "#A43D62"
BLUE_GRAY = "#52697A"
PETROL = "#3E6870"
CHARCOAL = "#2D3136"
GRAY = "#7B8791"
LIGHT = "#F4F5F6"
WHITE = "#FCFBFB"
ROSE = "#D8B8C4"
GOLD = "#C89B62"
GOLD_DARK = "#8F6A38"  # para texto/líneas sobre blanco (contraste)
GRID = "#E3E6E9"

# Orden categórico fijo (nunca ciclado): entidad -> color
CAT = [BURGUNDY, PETROL, GOLD, GRAY, BURGUNDY_2, BLUE_GRAY]
# Escala secuencial de un solo tono (claro -> oscuro)
SEQ_BURGUNDY = ["#F7EEF1", "#E6C9D4", "#C98AA1", "#A43D62", "#721C3B", "#4A1128"]
SEQ_PETROL = ["#EEF4F5", "#C9DCDF", "#93B6BC", "#5F8E96", "#3E6870", "#26464C"]
# Divergente: petróleo <- gris neutro -> burgundy
DIVERGING = [[0, "#26464C"], [0.25, "#5F8E96"], [0.5, "#EDEDED"], [0.75, "#C98AA1"], [1, "#4A1128"]]

EVIDENCIA_COLORES = {
    "Evidencia estadística tras corrección FDR": BURGUNDY,
    "Exploratoria nominal": GOLD,
    "Sin evidencia estadística detectable": GRAY,
    "No evaluable": "#C5CBD0",
}
EVIDENCIA_CORTA = {
    "Evidencia estadística tras corrección FDR": "Tras FDR",
    "Exploratoria nominal": "Nominal",
    "Sin evidencia estadística detectable": "Sin evidencia",
    "No evaluable": "No evaluable",
}


def register_template() -> None:
    t = go.layout.Template()
    t.layout = go.Layout(
        font=dict(family="Inter, 'Segoe UI', Roboto, sans-serif", color=CHARCOAL, size=13),
        title=dict(font=dict(family="'Source Serif 4', Georgia, serif", size=17, color=BURGUNDY_DARK), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CAT,
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor="#C9CED3", ticks="outside",
                   tickcolor="#C9CED3", title_font=dict(size=12, color=GRAY)),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor="#C9CED3", ticks="outside",
                   tickcolor="#C9CED3", title_font=dict(size=12, color=GRAY)),
        hoverlabel=dict(bgcolor="white", bordercolor=ROSE, font=dict(color=CHARCOAL, size=12)),
        legend=dict(bgcolor="rgba(255,255,255,0)", font=dict(size=12)),
        margin=dict(l=10, r=10, t=50, b=10),
        bargap=0.12,
    )
    pio.templates["biomed"] = t
    pio.templates.default = "simple_white+biomed"


PLOT_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}
