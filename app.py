"""
Dashboard — Variantes genéticas y edad de inicio (AOO) del Alzheimer en el Atlántico.
Ejecutar:  python -m streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="AOO Alzheimer · Atlántico",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components import svg  # noqa: E402
from components.ui import html, inject_css  # noqa: E402
from utils.theme import register_template  # noqa: E402

register_template()
inject_css()

P = "pages/"
nav = {
    "Inicio": [st.Page(P + "inicio.py", title="Portada", icon=":material/home:", default=True)],
    "Contexto": [
        st.Page(P + "contexto_problema.py", title="Problema y objetivos", icon=":material/psychology:"),
        st.Page(P + "contexto_literatura.py", title="Literatura", icon=":material/history_edu:"),
    ],
    "Datos": [
        st.Page(P + "datos_cohorte.py", title="Cohorte y flujo", icon=":material/groups:"),
        st.Page(P + "datos_calidad.py", title="Calidad de datos", icon=":material/fact_check:"),
        st.Page(P + "datos_univariado.py", title="Análisis univariado", icon=":material/bar_chart:"),
        st.Page(P + "datos_bivariado.py", title="Análisis bivariado", icon=":material/scatter_plot:"),
    ],
    "Genética": [
        st.Page(P + "gen_preparacion.py", title="Preparación y codificación", icon=":material/genetics:"),
        st.Page(P + "gen_pca.py", title="PCA · estructura", icon=":material/bubble_chart:"),
        st.Page(P + "gen_grm.py", title="GRM · similitud", icon=":material/grid_on:"),
        st.Page(P + "gen_loco.py", title="LOCO", icon=":material/call_split:"),
    ],
    "Asociación": [
        st.Page(P + "asoc_covariables.py", title="Selección de covariables", icon=":material/tune:"),
        st.Page(P + "asoc_modelos.py", title="Modelos LMM", icon=":material/functions:"),
        st.Page(P + "asoc_gwas.py", title="Resultados GWAS", icon=":material/insights:"),
        st.Page(P + "asoc_sensibilidad.py", title="Sensibilidad y A vs B", icon=":material/compare_arrows:"),
        st.Page(P + "asoc_variantes.py", title="Variantes priorizadas", icon=":material/biotech:"),
    ],
    "Cierre": [
        st.Page(P + "cierre_conclusiones.py", title="Conclusiones", icon=":material/flag:"),
        st.Page(P + "cierre_metodologia.py", title="Metodología y trazabilidad", icon=":material/account_tree:"),
    ],
}

with st.sidebar:
    html(f"""
    <div class="side-brand">
      <div style="opacity:.85">{svg.dna_helix(width=260, height=46, turns=2.2, opacity=0.9)}</div>
      <div class="s">Seminario Investigativo</div>
      <div class="t">Edad de inicio del Alzheimer · Atlántico</div>
    </div>""")

pg = st.navigation(nav, position="sidebar", expanded=True)

with st.sidebar:
    st.divider()
    html("""<div class="side-foot">Universidad del Norte<br>
    Daniela Hernández · Alejandra Meneses · Mariangel Yepes<br><br>
    Asociación ≠ causalidad. Resultados exploratorios.</div>""")

pg.run()
