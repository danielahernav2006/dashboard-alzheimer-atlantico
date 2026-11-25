import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.ui import STRETCH, callout, details, download, html, page_header, plot, section, sources
from utils.data import csv, eda, kpis as load_kpis
from utils.theme import BLUE_GRAY, BURGUNDY, GOLD, GOLD_DARK, GRAY, PETROL

page_header("Asociación", "Selección de covariables clínicas",
            "La significancia en el EDA no basta: una covariable del modelo debe ser anterior al inicio, no reflejar el "
            "curso de la enfermedad, estar completa y no ser redundante.", icon="filter", deco="network")

e = eda()
k=load_kpis()
sexo_e=e.loc[e.variable.eq("neuro__genero")].iloc[0]
edu_e=e.loc[e.variable.eq("neuro__nivel_educativo")].iloc[0]

section("Criterios de decisión", "Más allá del p-valor")
crit = [("Evidencia estadística", "EDA con FDR", "sigma"), ("Temporalidad", "¿precede a la AOO?", "clock"),
        ("Leakage / downstream", "¿es consecuencia del curso?", "alert"), ("Completitud", "pérdida muestral", "users"),
        ("Redundancia", "|ρ| alto o proxy", "layers"), ("Plausibilidad metodológica", "rol en el estimando", "scale"),
        ("Literatura", "respaldo externo", "book")]
from components import svg  # noqa: E402

html('<div class="kpis">' + "".join(
    f'<div class="kpi genetic"><div class="top"><div class="lbl">{n}</div>{svg.icon(i, 20, "#3E6870")}</div>'
    f'<div class="sub" style="margin-top:8px">{d}</div></div>' for n, d, i in crit) + "</div>")

c1, c2 = st.columns([1.2, 1])
with c1:
    dec = e.decision.value_counts().reset_index()
    dec.columns = ["decision", "n"]
    colors = {"Principal": BURGUNDY, "Fenotipo secundario": PETROL}
    fig = go.Figure(go.Bar(y=dec.decision, x=dec.n, orientation="h", text=dec.n, textposition="outside", cliponaxis=False,
                           marker_color=[colors.get(d, GRAY if d != "Excluida por leakage/downstream" else GOLD) for d in dec.decision]))
    fig.update_layout(title=f"Destino de las {len(e)} variables consideradas", xaxis_title="Variables",
                      yaxis=dict(autorange="reversed"), height=360)
    plot(fig)
with c2:
    ct = e.groupby(["evidencia_estadistica_EDA", "decision"]).size().reset_index(name="n")
    piv = ct.pivot(index="decision", columns="evidencia_estadistica_EDA", values="n").fillna(0).astype(int)
    st.markdown("**Asociación estadística frente a elegibilidad**")
    st.dataframe(piv, **STRETCH)
    st.caption("De las 25 variables con evidencia tras FDR, solo **educación** llegó al modelo: el resto era medida "
               "al registro, fenotipo secundario o de temporalidad no identificable.")

section("Covariables seleccionadas", "Modelo B")
c1, c2 = st.columns(2)
with c1:
    html(f"""<div class="card" style="border-top:4px solid #721C3B"><span class="badge solid">SEXO</span>
    <h4 style="margin-top:8px">Covariable basal preespecificada</h4>
    <span class="badge petrol">basal / anterior al AOO</span><span class="badge petrol">completo (0 % faltante)</span>
    <span class="badge petrol">sin leakage</span><span class="badge gray">EDA: p = {sexo_e.p_EDA:.3g}; FDR = {sexo_e.FDR_EDA:.3g}</span>
    <p style="margin-top:8px">Se incluye <b>aunque no sea estadísticamente significativa</b>: es una característica basal que
    precede a la AOO y capta heterogeneidad fenotípica. La preespecificación no depende de la significancia univariada.</p></div>""")
with c2:
    html(f"""<div class="card" style="border-top:4px solid #3E6870"><span class="badge solid" style="background:#3E6870">EDUCACIÓN</span>
    <h4 style="margin-top:8px">Nivel educativo agrupado (factor)</h4>
    <span class="badge burg">EDA: ρ = {edu_e.efecto_EDA:.3f}; p = {edu_e.p_EDA:.3g}; FDR = {edu_e.FDR_EDA:.3g}</span>
    <span class="badge petrol">probablemente anterior</span><span class="badge petrol">{edu_e.missing_pct:.1f} % faltante</span><span class="badge petrol">leakage bajo</span>
    <p style="margin-top:8px">Escolaridad alcanzada plausiblemente previa al inicio clínico y relacionada con la reserva cognitiva.
    Respaldo bibliográfico (PSEN1 E280A) con transferibilidad limitada. La asociación del EDA es <i>una</i> de varias razones.</p></div>""")

c1, c2, c3 = st.columns([1.1, 1, 1])
with c1:
    ag = csv("cov_educacion_agrupada.csv").fillna("Faltante")
    st.markdown("**Agrupación de educación** (referencia: No escolarizada)")
    st.dataframe(ag, hide_index=True, **STRETCH)
with c2:
    cod = csv("cov_educacion_codigos.csv")
    fig = px.bar(cod[cod.n_observado > 0], x="etiqueta documentada", y="n_observado", text="n_observado",
                 color_discrete_sequence=[PETROL])
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(title="Códigos originales (n = 345)", xaxis_title="", yaxis_title="Pacientes", xaxis_tickangle=-30)
    plot(fig, height=340)
with c3:
    sx = csv("cov_educacion_por_sexo.csv")
    sx = sx[sx.neuro__genero.notna() & (sx.neuro__genero != "educacion_modelo7")].rename(
        columns={"neuro__genero": "Educación", "0.0": "Masculino", "1.0": "Femenino"})
    st.markdown("**Educación agrupada × sexo** (n = 334)")
    st.dataframe(sx, hide_index=True, **STRETCH)
callout("Maestría y Doctorado son demasiado pequeños para estimar coeficientes propios: se agrupan con "
        "Licenciatura en <b>Educación superior</b> antes del GWAS. Educación entra como <b>factor</b>, no como número, porque "
        "los códigos (0, 5, 12, 16…) ordenan niveles sin intervalos equivalentes.", "info")

section("Diagnóstico del diseño", "Colinealidad")
v = csv("m_vif_modelo_B.csv")
fig = go.Figure(go.Bar(x=v.VIF, y=v.Término, orientation="h", marker_color=[GOLD if x > 5 else BLUE_GRAY for x in v.VIF],
                       text=[f"{x:.2f}" for x in v.VIF], textposition="outside", cliponaxis=False))
fig.add_vline(x=5, line=dict(color=GOLD_DARK, dash="dash"), annotation_text="VIF = 5")
fig.update_layout(title=f"VIF del Modelo B · máximo {v.VIF.max():.2f}", xaxis_title="VIF", height=360,
                  yaxis=dict(autorange="reversed"))
plot(fig)

section("Tabla de decisiones", "Todas las variables")
f = st.multiselect("Filtrar decisión", sorted(e.decision.unique()), placeholder="Todas")
t = e if not f else e[e.decision.isin(f)]
cols = ["descripcion", "familia", "evidencia_estadistica_EDA", "temporalidad", "downstream", "missing_pct",
        "calidad_codificacion", "redundancia", "decision", "justificacion"]
st.dataframe(t[cols], hide_index=True, **STRETCH, height=380,
             column_config={"missing_pct": st.column_config.NumberColumn("% faltante", format="%.1f")})
download(t[cols], "decisiones_covariables.csv")

details("""
- **Fenotipos secundarios:** memoria, función ejecutiva, cognición, funcionalidad y severidad. Condicionar por ellas podría
  bloquear parte de la señal genética (si la variante actúa sobre el proceso de enfermedad y este sobre la evaluación) o introducir sesgo.
- **Temporalidad no identificable:** comorbilidades, antecedentes y exposiciones registradas en pacientes que ya tenían
  Alzheimer, sin fecha de inicio de la condición.
- **Leakage/downstream:** edades de evaluación y medidas al registro; la edad actual está ligada matemáticamente a la AOO.
- **Solapamiento conceptual:** historia familiar (recuerdo retrospectivo, proxy de carga genética compartida con la GRM).
- **APOE:** el modelo se ajusta sin APOE; condicionar por APOE cambiaría el estimando, ambos marcadores se probaron individualmente; algunas combinaciones no faseadas son ambiguas.
- **Modelo C** (otras covariables basales) queda como sensibilidad futura si existiera evidencia temporal externa.
""")
sources("salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/evaluacion_covariables.csv", "salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/vif_modelo_B.csv",
        "04_preparacion_genetica_definitivo.ipynb §7.3 (tablas recuperadas)")
