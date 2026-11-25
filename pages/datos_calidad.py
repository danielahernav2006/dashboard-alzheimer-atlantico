import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.ui import STRETCH, callout, details, download, kpis, page_header, plot, section, sources
from utils.data import csv
from utils.theme import BLUE_GRAY, BURGUNDY, GRAY, PETROL, SEQ_BURGUNDY

page_header("Datos", "Calidad de datos e integración",
            "Cobertura por fuente, identificadores, consistencia de la AOO, faltantes y trazabilidad de la limpieza.",
            icon="check", deco="chromosome")

fu = csv("q_resumen_fuentes.csv")
cov = csv("q_cobertura_fuentes.csv")
mod = csv("q_modificaciones.csv")
hal = csv("q_hallazgos_limpieza.csv")
kpis([
    {"label": "Fuentes integradas", "value": "4", "sub": "HXGEN · NEURO · MoCA · AOO revisada", "icon": "layers"},
    {"label": "En las 4 fuentes", "value": str(int(cov.loc[cov[["match_hxgen", "match_neuro", "match_moca", "match_aoo_revisada"]].all(axis=1), "n"].sum())),
     "sub": "de 391 pacientes", "icon": "users"},
    {"label": "Celdas auditadas", "value": f"{int(hal.n.sum()):,}".replace(",", "."), "sub": "hallazgos registrados", "icon": "search"},
    {"label": "Modificaciones efectivas", "value": f"{int(mod.n.sum()):,}".replace(",", "."), "sub": "cambios trazados", "icon": "filter", "kind": "accent"},
    {"label": "Duplicados de ID", "value": "1", "sub": "corrección documentada en fuentes", "icon": "alert", "kind": "accent"},
])

t1, t2, t3, t4 = st.tabs(["Fuentes e IDs", "Consistencia de AOO", "Faltantes", "Limpieza y codificaciones"])

with t1:
    c1, c2 = st.columns([1.3, 1])
    with c1:
        fig = go.Figure()
        fig.add_bar(y=fu.fuente, x=fu.filas, orientation="h", name="Filas en la fuente", marker_color=BLUE_GRAY,
                    hovertemplate="%{y}: %{x} filas<extra></extra>")
        fig.add_bar(y=fu.fuente, x=fu.coinciden_hxgen, orientation="h", name="Coinciden con HXGEN",
                    marker_color=BURGUNDY, hovertemplate="%{y}: %{x} coinciden<extra></extra>")
        fig.update_layout(barmode="group", title="Filas por fuente vs. coincidencias con la cohorte maestra",
                          legend=dict(orientation="h", y=-0.2), xaxis_title="Registros")
        plot(fig, height=340)
    with c2:
        st.markdown("**Discrepancias de identificadores**")
        st.dataframe(csv("q_auditoria_ids.csv"), hide_index=True, **STRETCH)
        st.markdown("**Patrones de cobertura**")
        st.dataframe(cov, hide_index=True, **STRETCH)
    callout("HXGEN define la población: los 11 IDs presentes en NEURO y en la AOO revisada pero ausentes de HXGEN se "
            "excluyen por definición. Un ID duplicado correspondía a dos pacientes distintos y se corrigió el identificador "
            "en NEURO, MoCA y AOO revisada tras confirmarlo con el responsable de los datos.", "info")

with t2:
    c1, c2 = st.columns(2)
    est = csv("q_estado_aoo.csv")
    with c1:
        fig = px.bar(est.sort_values("n"), x="n", y="estado", orientation="h", text="n",
                     color_discrete_sequence=[BURGUNDY], title="Estado de la AOO revisada")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(yaxis_title="", xaxis_title="Pacientes")
        plot(fig, height=320)
    con = csv("q_consistencia_aoo.csv")
    with c2:
        fig = px.bar(con.sort_values("n_pacientes"), x="n_pacientes", y="estado_consistencia_aoo", orientation="h",
                     text="n_pacientes", color_discrete_sequence=[PETROL], title="Coherencia AOO vs. edad de evaluación")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(yaxis_title="", xaxis_title="Pacientes")
        plot(fig, height=320)
    callout("Las inconsistencias (AOO mayor que la edad de evaluación en alguna fuente) se <b>señalan</b> pero no se "
            "corrigen ni se excluyen automáticamente: la AOO revisada es la fuente analítica.", "warn")

with t3:
    miss = csv("q_missing_variables.csv")
    fams = sorted(miss.familia.dropna().unique())
    c1, c2, c3 = st.columns([2, 1, 1])
    fsel = c1.multiselect("Familias", fams, default=[], placeholder="Todas las familias")
    topn = c2.slider("Variables a mostrar", 10, 80, 30, 5)
    orden = c3.radio("Orden", ["Más faltantes", "Menos faltantes"], horizontal=True)
    d = miss if not fsel else miss[miss.familia.isin(fsel)]
    d = d.sort_values("pct_faltante", ascending=(orden == "Menos faltantes")).head(topn)
    fig = px.bar(d.iloc[::-1], x="pct_faltante", y="etiqueta", orientation="h", color="pct_faltante",
                 color_continuous_scale=SEQ_BURGUNDY, range_color=[0, 100],
                 hover_data={"familia": True, "fuente": True, "n_valido": True, "n_faltante": True, "pct_faltante": ":.1f"},
                 title="Porcentaje de faltantes por variable (denominador: 391)")
    fig.update_layout(yaxis_title="", xaxis_title="% faltante", coloraxis_showscale=False)
    fig.update_yaxes(tickfont=dict(size=10))
    plot(fig, height=max(360, 18 * len(d) + 80))
    fam = miss.groupby("familia").pct_faltante.agg(["mean", "max", "size"]).reset_index().sort_values("mean")
    fig = px.bar(fam, x="mean", y="familia", orientation="h", color_discrete_sequence=[BLUE_GRAY],
                 hover_data={"max": ":.1f", "size": True}, title="Faltante medio por familia de variables")
    fig.update_layout(xaxis_title="% faltante medio", yaxis_title="")
    plot(fig, height=520)
    download(miss, "faltantes_por_variable.csv")
    st.caption("En preguntas condicionales (p. ej., detalle de un antecedente) un faltante puede reflejar que la pregunta no correspondía.")

with t4:
    fuentes = sorted(mod.fuente.unique())
    fsel = st.segmented_control("Fuente", ["Todas"] + fuentes, default="Todas")
    m = mod if fsel in (None, "Todas") else mod[mod.fuente == fsel]
    g = m.groupby("tipo_hallazgo").n.sum().sort_values().reset_index()
    fig = px.bar(g, x="n", y="tipo_hallazgo", orientation="h", text="n", log_x=True,
                 color_discrete_sequence=[BURGUNDY], title="Modificaciones efectivas por tipo (escala log)")
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(yaxis_title="", xaxis_title="Celdas modificadas")
    plot(fig, height=460)
    c1, c2 = st.columns(2)
    with c1:
        ce = csv("q_codigos_especiales.csv")
        fig = px.bar(ce.sort_values("n"), x="n", y="decision", orientation="h", text="n",
                     color_discrete_sequence=[PETROL], title="Decisiones sobre códigos especiales")
        fig.update_traces(textposition="outside", cliponaxis=False)
        fig.update_layout(yaxis_title="", xaxis_title="Códigos")
        plot(fig, height=340)
    with c2:
        st.markdown("**Reducción neuropsicológica por redundancia (|ρ| ≥ 0,80)**")
        st.dataframe(csv("q_reduccion_neuro.csv"), hide_index=True, **STRETCH)
    st.markdown("**Revisiones pendientes agrupadas** (no se modificaron automáticamente)")
    st.dataframe(csv("q_revision_pendiente.csv"), hide_index=True, **STRETCH, height=280)

details("""
- **Orden de uniones:** HXGEN > neuropsicología > MoCA > AOO revisada (left join, validación uno a uno, 391 filas antes y después).
- **Normalización:** se reconocen marcadores semánticos de ausencia, caracteres invisibles y edades con unidad; no hay
  recodificación global de 0/9/99 (se preservan binarias, diabetes, MoCA y familiar afectado).
- **Etiquetas:** las del Excel tienen prioridad sobre reglas manuales confirmadas.
- **Faltantes:** se cuantifican con `isna()` después de la limpieza; la fuente clínica mantiene sus faltantes. La ruta ampliada MI completa solo AOO en objetos separados.
- **Reducción neuropsicológica:** de cada grupo redundante (|ρ| ≥ 0,80) se conserva un representante; las demás
  se excluyen solo del conjunto analítico, no de la base.
""")
sources("salidas/objetos_preprocesamiento.pkl", "salidas/auditoria_fuentes_paciente.csv", "salidas/inventario.pkl",
        "01_preprocesamiento_definitivo.ipynb §8–13")

st.dataframe(csv("u_resumen_missingness_aoo.csv"),hide_index=True,**STRETCH)
callout("La fuente original mantiene 21 AOO desconocidas. La completitud analítica de cada base M1b no modifica ese missingness original.", "info")
