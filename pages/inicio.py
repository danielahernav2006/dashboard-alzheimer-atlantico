import streamlit as st

from components import svg
from components.ui import callout, html, kpis, pipeline, section, sources
from utils.data import fmt_dec, fmt_int, kpis as load_kpis

k = load_kpis()

html(f"""
<div class="hero">
  <div class="deco">{svg.dna_helix(width=560, height=170, turns=2.6, opacity=0.38)}</div>
  <div class="deco2">{svg.brain(190, color="#E8C9D4", accent="#E9C996", opacity=0.30)}</div>
  <div class="eyebrow">Universidad del Norte · Seminario Investigativo</div>
  <h1>Identificación de variantes genéticas asociadas con la edad de inicio de la enfermedad de Alzheimer</h1>
  <div class="lead">Análisis de estructura poblacional y asociación genética en pacientes del Atlántico.
  Desenlace principal: <b style="color:#E9C996">AOO</b> (<i>Age of Onset</i>), la edad de inicio de la enfermedad, analizada como variable cuantitativa.</div>
  <div class="question">¿Existen variantes genéticas asociadas con una edad de inicio más temprana o más tardía
  del Alzheimer en esta cohorte?</div>
  <div class="meta">
    <span class="chip">Integrantes: <b>Daniela Hernández</b> · <b>Alejandra Meneses</b> · <b>Mariangel Yepes</b></span>
    <span class="chip">Modelo principal: <b>LMM con GRM LOCO</b></span>
    <span class="chip">Asociación ≠ <b>causalidad</b></span>
  </div>
  {svg.acgt_strip(120)}
</div>
""")

st.markdown(
    "**Objetivo.** Evaluar si la dosis del alelo alternativo (ALT) de SNPs autosómicos se asocia con la AOO, "
    "controlando estructura genética poblacional (PCs), similitud genética entre individuos (GRM con LOCO) "
    "y covariables basales (sexo y educación)."
)

section("Cifras clave", "Cohorte y genética")
kpis([
    {"label": "Cohorte clínica", "value": fmt_int(k["cohorte_clinica"]), "sub": "pacientes HXGEN", "icon": "users"},
    {"label": "Con AOO", "value": fmt_int(k["pacientes_aoo"]),
     "sub": f"{100*k['pacientes_aoo']/k['cohorte_clinica']:.1f} % · media {fmt_dec(k['aoo_media'],1)} años", "icon": "clock"},
    {"label": "Muestras genotipadas", "value": fmt_int(k["muestras_geneticas"]), "sub": "panel actual functional-variants",
     "icon": "dna", "kind": "genetic"},
    {"label": "Genotipo + AOO observada", "value": fmt_int(k["enlaces_con_aoo"]), "sub": "genotipo + AOO enlazados",
     "icon": "layers", "kind": "genetic"},
    {"label": "Modelo principal (B)", "value": fmt_int(k["n_modelo_B"]), "sub": "casos completos sexo + educación",
     "icon": "filter", "kind": "genetic"},
])
kpis([
    {"label": "SNPs evaluados", "value": fmt_int(k["snps_probados"]), "sub": "panel nuevo · AOO observada",
     "icon": "chart", "kind": "genetic"},
    {"label": "Cromosomas", "value": str(k["cromosomas"]), "sub": "autosomas 1–22", "icon": "chromosome", "kind": "genetic"},
    {"label": "λ GC", "value": fmt_dec(k["lambda_gc"], 3), "sub": "inflación genómica (modelo B)", "icon": "sigma",
     "kind": "accent"},
    {"label": "Significativas Bonferroni", "value": str(k["n_bonferroni"]),
     "sub": f"umbral p < {k['umbral_bonferroni']:.2e}", "icon": "target", "kind": "accent"},
    {"label": "Significativas FDR", "value": str(k["n_fdr"]), "sub": f"q mínimo = {k['fdr_min']:.3f}",
     "icon": "check", "kind": "accent"},
])

callout(
    f"<b>Resultado principal.</b> Ninguna variante alcanzó significancia tras corrección Bonferroni o FDR en el "
    f"análisis principal. La señal de menor p fue <code>{k['snp_menor_p']}</code> "
    f"(p = {k['p_min']:.2e}; β = {fmt_dec(k['beta_menor_p'],2)} años por copia ALT), que se interpreta como "
    "señal sugestiva exploratoria, no como hallazgo confirmado.", "key")

section("Pipeline analítico", "De la clínica a la interpretación")
pipeline(["Datos clínicos", "EDA", "Genotipos", "QC", "PCA", "GRM", "LOCO", "GWAS", "Sensibilidad", "Interpretación"],
         genetic_from=2, final=9)

section("Explorar", "Rutas sugeridas")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.page_link("pages/contexto_problema.py", label="Riesgo vs. edad de inicio", icon=":material/psychology:")
    st.page_link("pages/contexto_literatura.py", label="Línea de tiempo", icon=":material/history_edu:")
with c2:
    st.page_link("pages/datos_cohorte.py", label="Flujo de pacientes", icon=":material/groups:")
    st.page_link("pages/datos_bivariado.py", label="Explorador bivariado", icon=":material/scatter_plot:")
with c3:
    st.page_link("pages/gen_pca.py", label="Estructura poblacional", icon=":material/bubble_chart:")
    st.page_link("pages/gen_loco.py", label="LOCO y cromosoma 8", icon=":material/call_split:")
with c4:
    st.page_link("pages/asoc_gwas.py", label="Manhattan y QQ", icon=":material/insights:")
    st.page_link("pages/asoc_variantes.py", label="Variantes priorizadas", icon=":material/biotech:")

sources("data/kpis.json ← salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/resumen_gwas.csv",
        "salidas/genetica_panel_nuevo_MI_integrado/denominadores_integrados.csv", "salidas/base_full.pkl")

section("Ruta ampliada", "Sensibilidad M1b")
callout(f"La fuente clínica conserva {k['aoo_faltante']} AOO desconocidas. MICE–PMM M1b genera {k['n_imputaciones']} versiones de los mismos pacientes: imputa la brecha edad de evaluación − AOO y reconstruye el desenlace, preservando los observados. En genética se añaden {k['adicionales_MI']} casos elegibles: N={k['n_modelo_MI']} por corrida.", "info")
