import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from components.ui import STRETCH, callout, details, html, page_header, plot, section, sources
from utils.data import csv, fmt_dec, gwas, kpis as load_kpis
from utils.theme import BLUE_GRAY, BURGUNDY, GOLD, GRAY, PETROL

page_header("Asociación", "Sensibilidad por PCs y comparación de modelos A vs B",
            "¿Cambian las conclusiones si se ajustan 3 o 10 PCs, o si se quitan sexo y educación? Mismas 334 filas y GRM LOCO.",
            icon="scale", deco="network")

k=load_kpis()
g = gwas()
sens = csv("m_comparacion_sensibilidad.csv")
ab = csv("m_comparacion_AB_muestra_comun.csv")
METRICS = [("lambda_GC", "λ GC", "%.4f"), ("solapamiento_top", "Top-20 compartido", "%d"),
           ("r_beta", "r(β)", "%.4f"), ("r_se", "r(SE)", "%.5f"), ("rho_rango_p", "ρ ranking p", "%.4f"),
           ("mediana_dif_abs_SE", "mediana |ΔSE|", "%.4f")]


def metric_panel(df, labels, colors, title):
    fig = make_subplots(rows=2, cols=3, subplot_titles=[m[1] for m in METRICS], vertical_spacing=0.2, horizontal_spacing=0.08)
    for i, (col, name, fmt) in enumerate(METRICS):
        r, c = divmod(i, 3)
        vals = df[col].to_numpy()
        fig.add_trace(go.Bar(x=labels, y=vals, marker_color=colors, text=[fmt % v for v in vals], textposition="outside",
                             cliponaxis=False, hovertemplate="%{x}: %{y}<extra>" + name + "</extra>", showlegend=False), r + 1, c + 1)
        lo = 0 if col in ("solapamiento_top", "mediana_dif_abs_SE") else min(0.9, vals.min() - 0.02)
        hi = 22 if col == "solapamiento_top" else (vals.max() * 1.35 if col == "mediana_dif_abs_SE" else max(1.02, vals.max() + 0.01))
        fig.update_yaxes(range=[lo, hi], row=r + 1, col=c + 1)
    fig.update_layout(title=title, height=520)
    return fig


def scatter_beta(x, y, xl, yl, top):
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=x, y=y, mode="markers", marker=dict(color=BLUE_GRAY, size=3, opacity=.35), hoverinfo="skip", name="SNPs"))
    fig.add_trace(go.Scatter(x=x[top], y=y[top], mode="markers", marker=dict(color=GOLD, size=10, line=dict(color=BURGUNDY, width=1.5)),
                             name="Top 20 del modelo B (5 PCs)", text=g.variante[top], hovertemplate="%{text}<br>x=%{x:.3f} · y=%{y:.3f}<extra></extra>"))
    lim = [np.nanmin([x.min(), y.min()]), np.nanmax([x.max(), y.max()])]
    fig.add_trace(go.Scatter(x=lim, y=lim, mode="lines", line=dict(color=GRAY, dash="dash"), name="y = x"))
    fig.update_layout(xaxis_title=xl, yaxis_title=yl, legend=dict(orientation="h", y=-0.2), height=430)
    return fig


top_mask = g.p.rank(method="first") <= 20
t1, t2 = st.tabs(["Sensibilidad 3 / 5 / 10 PCs", "Modelo A vs Modelo B"])

with t1:
    callout(f"<b>Referencia: cinco PCs.</b> El mínimo r(β) entre especificaciones es {sens.r_beta.min():.4f}; el solapamiento mínimo del top-20 es {int(sens.solapamiento_top.min())}/20. Son diagnósticos de sensibilidad; no se elige el modelo con menor p.","key")
    s = sens.copy()
    s["lab"] = s.modelo.astype(str) + " PCs"
    plot(metric_panel(s, s.lab.tolist(), [PETROL, BURGUNDY, PETROL], "Métricas de concordancia frente a la especificación principal (5 PCs)"))
    alt = st.segmented_control("Comparar 5 PCs con", ["3 PCs", "10 PCs"], default="3 PCs")
    sfx = "B3" if alt == "3 PCs" else "B10"
    c1, c2 = st.columns(2)
    with c1:
        f = scatter_beta(g.beta.to_numpy(), g[f"beta_{sfx}"].to_numpy(), "β con 5 PCs", f"β con {alt}", top_mask.to_numpy())
        f.update_layout(title=f"β por SNP: 5 PCs vs {alt}")
        plot(f, key="sens_beta")
    with c2:
        f = scatter_beta(g.logp.to_numpy(), -np.log10(g[f"p_{sfx}"].to_numpy()), "−log10 p (5 PCs)", f"−log10 p ({alt})", top_mask.to_numpy())
        f.update_layout(title=f"−log10(p): 5 PCs vs {alt}")
        plot(f, key="sens_p")
    st.dataframe(sens, hide_index=True, **STRETCH)

with t2:
    c1, c2 = st.columns(2)
    with c1:
        html("""<div class="card"><span class="badge gray">A · genético estructural</span>
        <div style="margin-top:6px">SNP + PC1–PC5 + GRM LOCO (A comparable, n = 334)</div></div>""")
    with c2:
        html("""<div class="card"><span class="badge solid">B · clínico-genético principal</span>
        <div style="margin-top:6px">SNP + sexo + educación + PC1–PC5 + GRM LOCO (n = 334)</div></div>""")
    a = ab[ab.modelo == "A"].iloc[0]
    plot(metric_panel(ab.assign(lab=["A", "B (ref.)"]), ["A", "B (ref.)"], [BLUE_GRAY, BURGUNDY],
                      "A comparable frente a B (mismas filas, SNPs del panel nuevo)"))
    callout(f"Sexo y educación <b>modifican parcialmente</b> las estimaciones —r(β) = {fmt_dec(a.r_beta,3)}, ρ del ranking "
            f"de p = {fmt_dec(a.rho_rango_p,3)}, {int(a.solapamiento_top)} de 20 variantes compartidas en el top— pero "
            f"<b>mantienen ampliamente la estructura global</b> de los resultados: los SE apenas cambian (r = {fmt_dec(a.r_se,4)}), "
            f"λGC pasa de {fmt_dec(a.lambda_GC,4)} (A) a {fmt_dec(ab[ab.modelo=='B'].lambda_GC.iloc[0],4)} (B) y en ninguno hay "
            "variantes significativas tras corrección.", "info")
    c1, c2 = st.columns(2)
    with c1:
        f = scatter_beta(g.beta_A.to_numpy(), g.beta.to_numpy(), "β modelo A", "β modelo B", top_mask.to_numpy())
        f.update_layout(title="β por SNP: A vs B")
        plot(f, key="ab_beta")
    with c2:
        ta = set(g.nsmallest(20, "p_A").variante)
        tb = g.nsmallest(20, "p")
        tb = tb.assign(**{"En top-20 de A": tb.variante.isin(ta)})
        st.markdown("**Top 20 del modelo B y su presencia en el top 20 de A**")
        st.dataframe(tb[["variante", "beta", "p", "beta_A", "p_A", "En top-20 de A"]], hide_index=True, **STRETCH, height=400,
                     column_config={"p": st.column_config.NumberColumn(format="%.2e"), "p_A": st.column_config.NumberColumn("p (A)", format="%.2e"),
                                    "beta": st.column_config.NumberColumn("β (B)", format="%.3f"),
                                    "beta_A": st.column_config.NumberColumn("β (A)", format="%.3f")})
    st.dataframe(ab, hide_index=True, **STRETCH)

details("""
- **Métricas** (calculadas en el notebook 05 y exportadas; aquí verificadas al reproducir el solapamiento del top-20 y r(β)):
  λGC por especificación; *top-20 compartido* = SNPs comunes entre las 20 menores p; *r(β)*, *r(SE)* = correlación de Pearson
  entre especificaciones; *ρ ranking p* = Spearman de los p; *mediana |ΔSE|* = mediana de la diferencia absoluta de SE.
- **Misma muestra:** todas las especificaciones usan las 334 filas del modelo B y la misma GRM LOCO por cromosoma; cada una
  reestima sus nulos REML.
- **Regla de inferencia:** la conclusión principal es la de 5 PCs, no la del diseño que produzca más señales.
- **Sensibilidad futura:** educación con los seis niveles originales como factores separados.
""")
sources("salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/comparacion_sensibilidad.csv", "…/comparacion_AB_muestra_comun.csv",
        "…/gwas_sensibilidad_3pcs.csv, gwas_sensibilidad_10pcs.csv, gwas_referencia_A_comparable.csv")

section("Sensibilidad genética a AOO imputada", "MICE–PMM M1b")
mi=csv("gwas_MI_resumen.csv")
st.dataframe(mi,hide_index=True,**STRETCH)
plot(go.Figure(go.Scatter(x=mi.imputacion,y=mi.lambda_GC,mode="lines+markers",name="λGC por imputación")))
callout(f"Se incorporaron {int(mi.n.iloc[0])-k['n_modelo_B']} casos elegibles: {int(mi.n.iloc[0])} pacientes en cada una de {len(mi)} corridas. Todas tuvieron cero asociaciones corregidas. M1b no incluyó genotipos ni PCs: esta ruta es sensibilidad al modelo clínico de imputación, con nulos por imputación/cromosoma y sin combinar p ni q.","warn")
sel=st.selectbox("SNP para comparar con MI",g.nsmallest(50,"p").variante.tolist()+[v for v in ["19:45411941-T-C","19:45412079-C-T"] if v not in set(g.nsmallest(50,"p").variante)])
smi=csv("gwas_MI_estabilidad.csv");r=smi.loc[smi.variante.eq(sel)].iloc[0]
st.dataframe(smi.loc[smi.variante.eq(sel)],hide_index=True,**STRETCH)
f=go.Figure(go.Scatter(x=[r.beta,r.beta_media],y=["Observado","Media empírica MI"],mode="markers",error_x=dict(type="data",symmetric=False,array=[0,r.beta_max-r.beta_media],arrayminus=[0,r.beta_media-r.beta_min])))
f.update_layout(title="β observado y rango entre imputaciones (no IC combinado)",xaxis_title="Años de AOO por copia ALT");plot(f)
