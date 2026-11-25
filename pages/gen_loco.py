import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from components.ui import STRETCH, callout, details, html, kpis, page_header, plot, section, sources
from utils.data import csv, fmt_dec, fmt_int, jsonf, kpis as load_kpis
from utils.theme import BLUE_GRAY, BURGUNDY, GOLD, GOLD_DARK, GRAY, PETROL

page_header("Genética", "LOCO: leave-one-chromosome-out",
            "Para probar un SNP del cromosoma c, el efecto aleatorio usa una GRM construida sin ese cromosoma.",
            icon="chromosome", deco="chromosome")

k=load_kpis()
loco = csv("m_resumen_grm_loco.csv")
aud = csv("m_auditoria_cromosomas.csv")
diag = csv("m_nulos_loco_diagnostico.csv")
nb = csv("m_modelo_nulo_lmm.csv")
glob = csv("m_nulos_globales_pcs.csv")
perfil = csv("m_perfil_reml.csv")
txt = jsonf("textos_notebook.json")

section("La idea", "Proximal contamination")
html("""<div class="eq" style="text-align:center;white-space:normal">
GRM<sub>LOCO(c)</sub> &nbsp;=&nbsp; GRM construida <b>excluyendo el cromosoma c</b>
&nbsp;=&nbsp; (S<sub>total</sub> − S<sub>c</sub>) / (M<sub>total</sub> − M<sub>c</sub>)</div>""")
c1, c2 = st.columns(2)
with c1:
    callout("<b>Problema.</b> Si el SNP probado (y sus vecinos en LD) también forman parte de la GRM, parte de su señal "
            "se absorbe en el efecto aleatorio y la prueba pierde potencia: <i>proximal contamination</i> "
            "(Yang et al., 2014).", "warn")
with c2:
    callout("<b>Solución LOCO.</b> Se construyen 22 GRMs, cada una sin un cromosoma. Los PCs globales no cambian; "
            "la GRM descriptiva original tampoco. Cada cromosoma tiene su propio modelo nulo REML.", "info")

section("Explorar por cromosoma", "Selector")
c = st.select_slider("Cromosoma excluido", options=list(range(1, 23)), value=8)
r = loco[loco.cromosoma_excluido == c].iloc[0]
a = aud[aud.cromosoma == c].iloc[0]
d = diag[diag.cromosoma_excluido == c].iloc[0]
b = nb[(nb.Modelo == 5) & (nb.cromosoma_excluido == c)].iloc[0]
kpis([
    {"label": "SNPs excluidos", "value": fmt_int(r.n_snps_excluidos), "sub": f"{fmt_dec(a.pct_snps,2)} % del panel", "icon": "filter", "kind": "genetic"},
    {"label": "SNPs en la GRM LOCO", "value": fmt_int(r.n_snps_usados), "sub": f"de {fmt_int(k['marcadores_estructura'])} marcadores de estructura", "icon": "dna", "kind": "genetic"},
    {"label": "Tamaño GRM", "value": "755 × 755", "sub": f"submatriz AOO {int(r.n_AOO)} × {int(r.n_AOO)}", "icon": "grid", "kind": "genetic"},
    {"label": "Cambio vs. GRM global", "value": f"{fmt_dec(a.cambio_relativo_grm_AOO_pct,2)} %", "sub": "norma de Frobenius relativa (AOO)", "icon": "scale", "kind": "accent"},
    {"label": "Media diagonal", "value": fmt_dec(r.media_diagonal, 4), "sub": "panel nuevo", "icon": "chart", "kind": "accent"},
])
c1, c2 = st.columns(2)
with c1:
    html(f"""<div class="card"><span class="badge gray">Nulo diagnóstico</span> <b>sexo + PC1–PC5 · n = 345</b>
    <div class="vc" style="box-shadow:none;border:none;padding:6px 0 0 0">
    <div class="row"><span>σ²g</span><b>{fmt_dec(d.sigma_g2,2)}</b></div>
    <div class="row"><span>σ²e</span><b>{fmt_dec(d.sigma_e2,2)}</b></div>
    <div class="row"><span>h² del componente GRM</span><b>{fmt_dec(d.h2,4)}</b></div>
    <div class="row"><span>Solución</span><b>{d.frontera}</b></div></div></div>""")
with c2:
    html(f"""<div class="card"><span class="badge solid">Modelo B (principal)</span> <b>sexo + educación + PC1–PC5 · n = 334</b>
    <div class="vc" style="box-shadow:none;border:none;padding:6px 0 0 0">
    <div class="row"><span>σ²g</span><b>{fmt_dec(b.sigma_g2,2)}</b></div>
    <div class="row"><span>σ²e</span><b>{fmt_dec(b.sigma_e2,2)}</b></div>
    <div class="row"><span>h² del componente GRM</span><b>{fmt_dec(b.h2,4)}</b></div>
    <div class="row"><span>Solución</span><b>{b.frontera}</b></div></div></div>""")

section("Componentes de varianza por cromosoma", "22 modelos nulos")
fig = make_subplots(rows=1, cols=2, subplot_titles=("Nulo diagnóstico (sexo + 5 PCs, n = 345)",
                                                    "Modelo B principal (n = 334)"), horizontal_spacing=0.08)
cols_d = [GOLD if x == 8 else GRAY for x in diag.cromosoma_excluido]
fig.add_trace(go.Bar(x=diag.cromosoma_excluido, y=diag.h2, marker_color=cols_d, name="h² diagnóstico",
                     hovertemplate="chr %{x}: h²=%{y:.3f}<extra></extra>"), 1, 1)
bb = nb[nb.Modelo == 5]
fig.add_trace(go.Bar(x=bb.cromosoma_excluido, y=bb.h2, marker_color=[BURGUNDY if x != c else GOLD for x in bb.cromosoma_excluido],
                     name="h² modelo B", hovertemplate="chr %{x}: h²=%{y:.3f}<extra></extra>"), 1, 2)
fig.update_yaxes(range=[0, 1.08], title_text="h² (componente GRM)", row=1, col=1)
fig.update_yaxes(range=[0, 1.08], row=1, col=2)
fig.update_xaxes(dtick=1, title_text="Cromosoma excluido")
fig.update_layout(showlegend=False, height=380)
plot(fig)

_global5=glob.loc[glob.n_pcs.eq(5)].iloc[0]
_chr8=diag.loc[diag.cromosoma_excluido.eq(8)].iloc[0]
callout(f"<b>Panel nuevo.</b> El nulo global con sexo y cinco PCs ya era interior (h²={_global5.h2:.3f}); al excluir chr8, h²={_chr8.h2:.3f}, también interior. {int(diag.sigma_e2.eq(0).sum())} de {len(diag)} nulos LOCO diagnósticos tuvieron varianza residual cero. Estos ajustes no son el Modelo B con educación. El paso de frontera a interior corresponde al panel histórico.","key")


c1, c2 = st.columns(2)
with c1:
    fig = go.Figure(go.Bar(x=aud.cromosoma, y=aud.cambio_relativo_grm_AOO_pct,
                           marker_color=[GOLD if x == 8 else PETROL for x in aud.cromosoma],
                           customdata=aud[["n_snps", "norma_frobenius_por_snp_AOO"]],
                           hovertemplate="chr %{x}: %{y:.2f} %<br>SNPs %{customdata[0]}<br>norma/SNP %{customdata[1]:.2f}<extra></extra>"))
    fig.update_layout(title="Cambio de la GRM al excluir cada cromosoma", xaxis=dict(dtick=1, title="Cromosoma"),
                      yaxis_title="% cambio (norma relativa, AOO)")
    plot(fig, height=340)
with c2:
    fig = go.Figure(go.Scatter(x=aud.n_snps, y=aud.cambio_relativo_grm_AOO_pct, mode="markers+text", text=aud.cromosoma,
                               textposition="middle right", marker=dict(size=11, color=[GOLD if x == 8 else BLUE_GRAY for x in aud.cromosoma],
                                                                         line=dict(color="white", width=1))))
    fig.update_layout(title="El cambio crece con el número de SNPs excluidos", xaxis_title="SNPs del cromosoma",
                      yaxis_title="% cambio GRM")
    plot(fig, height=340)
st.caption("Los aportes cromosómicos y sus cambios se calculan con el panel nuevo; su magnitud no demuestra un locus causal.")

section("Perfil REML del modelo global", "Diagnóstico de frontera")
c1, c2 = st.columns([1.5, 1])
with c1:
    fig = go.Figure(go.Scatter(x=perfil.h2, y=perfil.objetivo_REML, mode="lines", line=dict(color=BURGUNDY, width=2.5)))
    mn = perfil.loc[perfil.objetivo_REML.idxmin()]
    fig.add_trace(go.Scatter(x=[mn.h2], y=[mn.objetivo_REML], mode="markers", marker=dict(color=GOLD, size=13, line=dict(color=BURGUNDY, width=2)),
                             name="mínimo"))
    fig.update_layout(title="−2 log L restringida perfilada vs h² (GRM global, sexo + 5 PCs)", xaxis_title="h²",
                      yaxis_title="Objetivo REML (menor es mejor)", showlegend=False)
    plot(fig, height=340)
with c2:
    st.dataframe(glob, hide_index=True, **STRETCH)
    st.caption("Panel nuevo: los diagnósticos globales con sexo y 3, 5 y 10 PCs fueron interiores. h² describe este componente en esta muestra y especificación, no heredabilidad poblacional definitiva.")

with st.expander("Tabla completa de GRMs LOCO y auditoría por cromosoma"):
    st.dataframe(loco, hide_index=True, **STRETCH)
    st.dataframe(aud, hide_index=True, **STRETCH)

details("""
- **Construcción eficiente:** una sola pasada acumula S_c (producto estandarizado) y M_c por cromosoma; S_total = Σ S_c;
  GRM_LOCO(c) = (S_total − S_c)/(M_total − M_c). Mismas reglas de la GRM global (p observada, 2p para faltantes, escala √(2p(1−p))).
- **Validaciones:** simetría, autovalor mínimo no negativo dentro de tolerancia en la muestra genética y en la submuestra AOO, reconstrucción global cotejada.
- **Modelo nulo por cromosoma:** V = σ²g·K₋c + σ²e·I estimado por REML con los efectos fijos de cada especificación; sus componentes
  se reutilizan en las pruebas de Wald de todos los SNPs de ese cromosoma (esquema tipo EMMAX).
- **Auditoría del cromosoma 8:** porcentaje de SNPs, aporte por SNP (norma de Frobenius / M_c en la muestra AOO), cambio relativo de la
  GRM y percentiles fuera de la diagonal. Posibles explicaciones (no verificadas): similitud entre familiares, concentración de
  información en ciertos marcadores, LD residual tras la poda o propiedades muestrales y numéricas.
""")
sources("salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/{resumen_grm_loco, modelo_nulo_lmm, nulos_globales_pcs, perfil_reml}.csv",
        "04_preparacion_genetica_definitivo.ipynb §7.6 (tablas HTML recuperadas)")
