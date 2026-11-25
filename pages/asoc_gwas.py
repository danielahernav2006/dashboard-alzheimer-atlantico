import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from components.ui import STRETCH, callout, details, download, html, kpis, page_header, plot, section, sources
from utils.data import fmt_dec, fmt_int, gwas, kpis as load_kpis, manhattan_coords
from utils.theme import BLUE_GRAY, BURGUNDY, BURGUNDY_DARK, GOLD, GOLD_DARK, GRAY, PETROL

k = load_kpis()
page_header("Asociación", "Resultados GWAS SNP–AOO",
            f"Panel nuevo · AOO observada · Modelo B: sexo + educación + cinco PCs + GRM LOCO · {k['n_modelo_B']} pacientes · {fmt_int(k['snps_probados'])} SNPs.",
            icon="chart", deco="chromosome")

html(f"""<div class="callout warn" style="font-size:1.04rem"><div class="ic"></div><div>
<b>Ninguna variante alcanzó significancia después de corrección Bonferroni o FDR en el análisis principal.</b><br>
<span style="font-size:.9rem">Menor p = {k['p_min']:.2e} (umbral Bonferroni {k['umbral_bonferroni']:.2e}); menor FDR (q) = {k['fdr_min']:.3f}.
Las señales con menor p son <i>sugestivas/exploratorias</i>.</span></div></div>""")

kpis([
    {"label": "SNPs probados", "value": fmt_int(k["snps_probados"]), "sub": "0 excluidos por estimabilidad", "icon": "dna", "kind": "genetic"},
    {"label": "Pacientes", "value": str(k["n_modelo_B"]), "sub": "casos completos modelo B", "icon": "users", "kind": "genetic"},
    {"label": "λ GC", "value": fmt_dec(k["lambda_gc"], 4), "sub": "≈ 1: sin inflación global relevante", "icon": "sigma", "kind": "accent"},
    {"label": "Bonferroni", "value": str(k["n_bonferroni"]), "sub": f"p < {k['umbral_bonferroni']:.2e}", "icon": "target", "kind": "accent"},
    {"label": "FDR < 0,05", "value": str(k["n_fdr"]), "sub": "Benjamini–Hochberg", "icon": "check", "kind": "accent"},
])

g = gwas()
d, ticks, chroms = manhattan_coords()
bonf = -np.log10(k["umbral_bonferroni"])

section("Manhattan plot interactivo", "Explorar")
c1, c2, c3, c4 = st.columns([1.1, 1, 1, 1.3])
csel = c1.selectbox("Cromosoma", ["Todos"] + chroms, index=0, key="gw_c")
topn = c2.number_input("Resaltar top N", 0, 200, 20, 5, key="gw_top")
sug = c3.toggle("Línea de referencia 1×10⁻⁵", value=False, key="gw_sug",
                help="Referencia convencional de 'sugestivo' en la literatura GWAS. NO fue preespecificada en este análisis; "
                     "No es un umbral de significancia del estudio.")
q = c4.text_input("Buscar SNP", placeholder="p. ej. 3:196559676-G-A o rs429358", key="gw_q")
minlog = st.slider("Mostrar SNPs con −log10(p) ≥", 0.0, 3.0, 0.0, 0.25, key="gw_min",
                   help="Filtra visualmente los SNPs con p grandes; no altera los resultados.")
if st.button("Restablecer filtros", icon=":material/restart_alt:"):
    for kk in ["gw_c", "gw_top", "gw_sug", "gw_q", "gw_min"]:
        st.session_state.pop(kk, None)
    st.rerun()

view = d if csel == "Todos" else d[d.crom == csel]
view = view[view.logp >= minlog]
xcol = "x" if csel == "Todos" else "pos"
top_ids = set(g.nsmallest(int(topn), "p").variante) if topn else set()
hover = ("<b>%{customdata[0]}</b> %{customdata[1]}<br>chr %{customdata[2]} · pos %{customdata[3]:,}<br>REF %{customdata[4]} → ALT %{customdata[5]}"
         "<br>β = %{customdata[6]:.3f} · SE = %{customdata[7]:.3f}<br>p = %{customdata[8]:.3e}<br>FDR = %{customdata[9]:.4f} · "
         "Bonferroni = %{customdata[10]:.3g}<br>frecuencia ALT = %{customdata[11]:.3f} · rango %{customdata[12]}<extra></extra>")
cdcols = ["variante", "rsid_documentado", "crom", "pos", "ref", "alt", "beta", "se", "p", "p_fdr", "p_bonferroni", "frecuencia_ALT", "rank_p"]

fig = go.Figure()
detalle = view[view.p < 0.1]
fondo = view[view.p >= 0.1]
for par, col in [(0, BURGUNDY), (1, BLUE_GRAY)]:
    f = fondo[fondo.crom % 2 == par]
    fig.add_trace(go.Scattergl(x=f[xcol], y=f.logp, mode="markers", marker=dict(color=col, size=4, opacity=.55),
                               hoverinfo="skip", showlegend=False))
    s = detalle[detalle.crom % 2 == par]
    fig.add_trace(go.Scattergl(x=s[xcol], y=s.logp, mode="markers", marker=dict(color=col, size=5.5, opacity=.85),
                               customdata=s[cdcols].to_numpy(), hovertemplate=hover, showlegend=False))
if top_ids:
    t = view[view.variante.isin(top_ids)]
    fig.add_trace(go.Scatter(x=t[xcol], y=t.logp, mode="markers", name=f"Top {topn} por p",
                             marker=dict(color=GOLD, size=11, line=dict(color=BURGUNDY_DARK, width=1.5)),
                             customdata=t[cdcols].to_numpy(), hovertemplate=hover))
if q:
    key = {'rs429358':'19:45411941-T-C','rs7412':'19:45412079-C-T'}.get(q.strip().lower(),q.strip())
    hit = d[d.variante == key]
    if hit.empty:
        st.warning(f"«{q}» no está en el panel (formato crom:pos-REF-ALT).")
    else:
        h = hit.iloc[0]
        hx = h.x if xcol == "x" else h.pos
        if csel == "Todos" or h.crom == csel:
            fig.add_trace(go.Scatter(x=[hx], y=[h.logp], mode="markers+text", text=[h.variante], textposition="top center",
                                     marker=dict(color=PETROL, size=15, symbol="diamond", line=dict(color="white", width=2)),
                                     name="Buscado", customdata=hit[cdcols].to_numpy(), hovertemplate=hover))
        st.success(f"{h.variante}: β = {h.beta:.3f}, p = {h.p:.3e}, FDR = {h.p_fdr:.3f}, rango {h.rank_p:,} de {len(g):,}".replace(",", "."))
fig.add_hline(y=bonf, line=dict(color=BURGUNDY, dash="dash", width=1.5),
              annotation_text=f"Bonferroni (p = {k['umbral_bonferroni']:.2e})", annotation_position="top left")
if sug:
    fig.add_hline(y=5, line=dict(color=GOLD_DARK, dash="dot", width=1.5),
                  annotation_text="Referencia 1×10⁻⁵ (no preespecificada)", annotation_position="bottom left")
if csel == "Todos":
    fig.update_xaxes(tickvals=ticks, ticktext=[str(c) for c in chroms], title="Cromosoma", showgrid=False)
else:
    fig.update_xaxes(title=f"Posición en el cromosoma {csel} (compatible con GRCh37; certificado pendiente)", tickformat=",")
fig.update_yaxes(title="−log10(p)", range=[0, max(bonf + 0.6, view.logp.max() + 0.5 if len(view) else 7)])
fig.update_layout(height=520, legend=dict(orientation="h", y=1.06, x=1, xanchor="right"), dragmode="zoom")
plot(fig, key="manhattan")
st.caption("Arrastra para hacer zoom, doble clic para restablecer. Alternancia burgundy/gris por cromosoma. "
           "SNPs con p ≥ 0,1 se dibujan sin ficha de hover para mantener la fluidez.")

section("QQ plot e inflación genómica", "Calibración")
c1, c2 = st.columns([1.3, 1])
with c1:
    n = len(g)
    obs = np.sort(g.logp.to_numpy())[::-1]
    i = np.arange(1, n + 1)
    exp = -np.log10((i - 0.5) / n)
    keep = np.unique(np.r_[np.arange(min(n, 3000)), np.linspace(0, n - 1, 3000).astype(int)])
    lo = -np.log10(stats.beta.ppf(0.975, i[keep], n - i[keep] + 1))
    hi = -np.log10(stats.beta.ppf(0.025, i[keep], n - i[keep] + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=np.r_[exp[keep], exp[keep][::-1]], y=np.r_[hi, lo[::-1]], fill="toself",
                             fillcolor="rgba(62,104,112,.13)", line=dict(width=0), name="IC 95 % bajo H0", hoverinfo="skip"))
    fig.add_trace(go.Scattergl(x=exp[keep], y=obs[keep], mode="markers", marker=dict(color=BURGUNDY, size=5),
                               name="SNPs", hovertemplate="esperado %{x:.2f}<br>observado %{y:.2f}<extra></extra>"))
    m = max(exp.max(), obs.max()) + 0.3
    fig.add_trace(go.Scatter(x=[0, m], y=[0, m], mode="lines", line=dict(color=GRAY, dash="dash"), name="y = x"))
    fig.add_annotation(x=0.8, y=m - 0.6, text=f"λGC = {k['lambda_gc']:.4f}", showarrow=False,
                       font=dict(size=16, color=BURGUNDY_DARK, family="Source Serif 4, Georgia"))
    fig.update_layout(title="QQ plot (modelo B)", xaxis_title="−log10(p) esperado", yaxis_title="−log10(p) observado",
                      legend=dict(orientation="h", y=-0.2), height=470)
    plot(fig)
with c2:
    callout("La nube sigue la diagonal dentro de la banda esperada y λGC próximo a 1: no hay inflación global relevante "
            "tras el ajuste; la cola debe interpretarse junto con la multiplicidad. λGC es un diagnóstico descriptivo; <b>no se usó para recalibrar</b> los p.", "info")
    callout("Con 334 pacientes, la potencia para detectar efectos pequeños por SNP es limitada: no detectar señales "
            "corregidas <b>no descarta</b> efectos de menor magnitud.", "neutral")

section("Significancia genome-wide vs. señales sugestivas", "Dos niveles distintos")
c1, c2 = st.columns(2)
with c1:
    html(f"""<div class="card" style="border-top:4px solid #721C3B"><span class="badge solid">SIGNIFICANCIA GENOME-WIDE</span>
    <h4 style="margin-top:8px">0 variantes</h4>
    <p>Requiere superar la corrección por múltiples pruebas: Bonferroni (p &lt; {k['umbral_bonferroni']:.2e}) o FDR &lt; 0,05.
    Ningún SNP lo logra; la menor FDR es {k['fdr_min']:.3f}.</p></div>""")
with c2:
    html("""<div class="card" style="border-top:4px solid #C89B62"><span class="badge gold">SEÑALES SUGESTIVAS / EXPLORATORIAS</span>
    <h4 style="margin-top:8px">Ranking por p sin ajustar</h4>
    <p>Las variantes con menor p (p nominal, sin superar los ajustes) se <b>priorizan para seguimiento</b> —anotación funcional y
    replicación—, no se reportan como asociadas. No se definió un umbral sugestivo en el análisis.</p></div>""")

section("Tabla de variantes principales", "Ordenable · descargable")
c1, c2 = st.columns([1, 3])
nt = c1.slider("Número de variantes", 10, 500, 50, 10)
dirf = c2.segmented_control("Dirección", ["Todas", "AOO mayor (β > 0)", "AOO menor (β < 0)"], default="Todas")
tt = g.nsmallest(nt, "p")
if dirf and dirf.startswith("AOO mayor"):
    tt = tt[tt.beta > 0]
elif dirf and dirf.startswith("AOO menor"):
    tt = tt[tt.beta < 0]
cols = ["rank_p", "variante", "crom", "pos", "ref", "alt", "frecuencia_ALT", "beta", "se", "p", "p_fdr", "p_bonferroni"]
st.dataframe(tt[cols], hide_index=True, **STRETCH, height=420,
             column_config={"rank_p": "Rango", "frecuencia_ALT": st.column_config.NumberColumn("Frec. ALT", format="%.3f"),
                            "beta": st.column_config.NumberColumn("β (años/copia)", format="%.3f"),
                            "se": st.column_config.NumberColumn("SE", format="%.3f"),
                            "p": st.column_config.NumberColumn("p", format="%.2e"),
                            "p_fdr": st.column_config.NumberColumn("FDR (q)", format="%.4f"),
                            "p_bonferroni": st.column_config.NumberColumn("p Bonferroni", format="%.3f"),
                            "pos": st.column_config.NumberColumn("Posición", format="%d")})
download(tt[cols], "gwas_variantes_principales.csv")

details("""
- **Fuente:** `gwas_principal.csv` (corrida del manifiesto integrado, panel nuevo). El dashboard no recalcula el GWAS.
- **Columnas:** β en años de AOO por copia ALT; SE de Wald; p bilateral; FDR = Benjamini–Hochberg; *p Bonferroni* = p × número real de pruebas truncado en 1.
- **Frecuencia ALT:** en los individuos de cada prueba (334).
- **Manhattan:** posición acumulada por cromosoma del panel probado (compatible con GRCh37; certificado pendiente). La altura visual no determina por sí sola evidencia corregida.
- **QQ:** banda del 95 % de los estadísticos de orden uniformes (distribución beta); se muestran las 3.000 colas superiores y una rejilla del resto.
- **Cobertura:** el escaneo cubre el panel nuevo disponible; la poda local para PCA/GRM no reduce su universo de asociación. QC/LD del proveedor y ensamblaje están pendientes de certificación.
""")
sources("salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/gwas_principal.csv", "salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/resumen_gwas.csv",
        "04_preparacion_genetica_definitivo.ipynb §7.7–7.12")
