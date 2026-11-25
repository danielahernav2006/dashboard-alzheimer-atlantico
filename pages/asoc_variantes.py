import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.ui import STRETCH, callout, details, download, html, page_header, plot, section, sources
from utils.data import csv, fmt_p, gwas
from utils.theme import BLUE_GRAY, BURGUNDY, GOLD, GRAY, PETROL

page_header("Asociación", "Variantes priorizadas · candidatas exploratorias",
            "Señales sugestivas ordenadas por p sin ajustar. Ninguna supera Bonferroni ni FDR: son candidatas para "
            "anotación y replicación, no variantes confirmadas ni causales.", icon="search", deco="dna")

g = gwas()
APOE = "19:45411941-T-C"

callout("<b>Cómo leer las tarjetas.</b> β &gt; 0 → asociación con <b>mayor AOO</b> (inicio más tardío) por copia de ALT; "
        "β &lt; 0 → asociación con <b>menor AOO</b> (inicio más temprano). La evidencia corregida se muestra por variante; el ranking nominal no equivale a significancia.", "neutral")

c1, c2 = st.columns([1, 3])
n = c1.slider("Tarjetas", 4, 24, 12, 4)
dirsel = c2.segmented_control("Dirección", ["Todas", "β > 0 · AOO mayor", "β < 0 · AOO menor"], default="Todas")
top = g.nsmallest(60, "p")
if dirsel and "β > 0" in dirsel:
    top = top[top.beta > 0]
elif dirsel and "β < 0" in dirsel:
    top = top[top.beta < 0]
top = top.head(n)

cards = []
for r in top.itertuples():
    pos = r.beta > 0
    color = PETROL if pos else BURGUNDY
    cards.append(f"""<div class="vc" style="border-top:3px solid {color}"><div class="rk">#{r.rank_p}</div>
    <div class="id">{r.variante}</div>
    <div style="margin:4px 0 6px 0"><span class="badge gray">chr {r.crom}</span><span class="badge gray">{r.ref} → {r.alt}</span></div>
    <div class="row"><span>Posición</span><b>{r.pos:,}</b></div>
    <div class="row"><span>β (SE)</span><b>{r.beta:+.3f} ({r.se:.3f})</b></div>
    <div class="row"><span>p</span><b>{fmt_p(r.p)}</b></div>
    <div class="row"><span>FDR · Bonferroni</span><b>{r.p_fdr:.3f} · {r.p_bonferroni:.2f}</b></div>
    <div class="row"><span>Frecuencia ALT</span><b>{r.frecuencia_ALT:.3f}</b></div>
    <div class="dirtag" style="color:{color}">{'▲ asociada con AOO mayor' if pos else '▼ asociada con AOO menor'}</div></div>""".replace(",", "\u202f"))
html(f'<div class="vcards">{"".join(cards)}</div>')

section("Ficha de una variante", "Selección")
opts = list(g.nsmallest(200, "p").variante)
for marker in [APOE,"19:45412079-C-T"]:
    if marker in set(g.variante) and marker not in opts:opts.append(marker)
v = st.selectbox("Variante (top 200 por p + ambos marcadores APOE)", opts,
                 format_func=lambda x: x + ("  ·  " + g.set_index("variante").rsid_documentado[x] if g.set_index("variante").rsid_documentado[x] else ""))
r = g[g.variante == v].iloc[0]
c1, c2 = st.columns([1, 1.4])
with c1:
    color = PETROL if r.beta > 0 else BURGUNDY
    html(f"""<div class="card" style="border-top:4px solid {color}">
    <div class="id" style="font-family:var(--mono);font-size:1.05rem;color:#4A1128;font-weight:600">{r.variante}</div>
    <div class="vc" style="box-shadow:none;border:none;padding:6px 0 0 0">
    <div class="row"><span>Cromosoma</span><b>{r.crom}</b></div>
    <div class="row"><span>Posición (compatible con GRCh37; pendiente)</span><b>{int(r.pos):,}</b></div>
    <div class="row"><span>REF / ALT</span><b>{r.ref} / {r.alt}</b></div>
    <div class="row"><span>Frecuencia ALT (n = {int(r.n_modelo)})</span><b>{r.frecuencia_ALT:.4f}</b></div>
    <div class="row"><span>β (años por copia ALT)</span><b>{r.beta:+.4f}</b></div>
    <div class="row"><span>SE</span><b>{r.se:.4f}</b></div>
    <div class="row"><span>p</span><b>{fmt_p(r.p)}</b></div>
    <div class="row"><span>FDR (q)</span><b>{r.p_fdr:.4f}</b></div>
    <div class="row"><span>p Bonferroni</span><b>{r.p_bonferroni:.4f}</b></div>
    <div class="row"><span>Ranking por p</span><b>{int(r.rank_p):,} / {len(g):,}</b></div>
    <div class="row"><span>Genotipos 0/1/2 (755)</span><b>{int(r.n0)} / {int(r.n1)} / {int(r.n2)}</b></div></div>
    <div class="dirtag" style="color:{color};margin-top:8px;font-weight:600">{'Asociación con AOO mayor (inicio más tardío)' if r.beta > 0 else 'Asociación con AOO menor (inicio más temprano)'} · exploratoria</div>
    </div>""".replace(",", "\u202f"))
with c2:
    specs = pd.DataFrame({
        "Especificación": ["A comparable", "B · 3 PCs", "B · 5 PCs (principal)", "B · 10 PCs"],
        "beta": [r.beta_A, r.beta_B3, r.beta, r.beta_B10], "se": [r.se_A, r.se_B3, r.se, r.se_B10],
        "p": [r.p_A, r.p_B3, r.p, r.p_B10]})
    fig = go.Figure(go.Scatter(x=specs.beta, y=specs["Especificación"], mode="markers",
                               error_x=dict(type="data", array=1.96 * specs.se, color=GRAY, thickness=2),
                               marker=dict(size=14, color=[BLUE_GRAY, PETROL, BURGUNDY, PETROL], line=dict(color="white", width=2)),
                               customdata=specs.p, hovertemplate="%{y}<br>β = %{x:.3f}<br>p = %{customdata:.2e}<extra></extra>"))
    fig.add_vline(x=0, line=dict(color=GRAY, dash="dash"))
    fig.update_layout(title="β ± 1,96·SE en las cuatro especificaciones", xaxis_title="β (años por copia ALT)", height=330,
                      yaxis=dict(autorange="reversed"))
    plot(fig)
    st.caption("Intervalos de Wald aproximados (β ± 1,96·SE) solo como referencia visual; no están corregidos por multiplicidad.")

section("APOE: resultados individuales", "Ambos marcadores presentes")
st.dataframe(csv("apoe_individual.csv")[["rs","variante","ref","alt","n_modelo","frecuencia_ALT","MAC","beta","se","p","p_fdr","p_bonferroni"]],hide_index=True,**STRETCH)
callout("El Modelo B se ajustó sin APOE como covariable. rs429358 y rs7412 se probaron individualmente. Una asociación nominal no equivale a evidencia corregida; el alelo de efecto es ALT y la dirección se interpreta como AOO mayor o menor por copia.","info")
with st.expander("Combinaciones de APOE y fase"):
    st.dataframe(csv("apoe_combinaciones_resumen.csv"),hide_index=True,**STRETCH)
    st.caption("Algunas combinaciones no faseadas admiten más de un diplotipo compatible; no se fuerza una asignación. El ensamblaje sigue pendiente de certificación documental. No se realizó anotación funcional externa.")

section("Exportar candidatas", "CSV")
k_ = st.slider("Número de candidatas a exportar", 10, 500, 100, 10)
exp = g.nsmallest(k_, "p")[["rank_p", "variante", "crom", "pos", "ref", "alt", "frecuencia_ALT", "beta", "se", "p", "p_fdr",
                            "p_bonferroni", "beta_A", "p_A", "beta_B3", "p_B3", "beta_B10", "p_B10"]]
exp = exp.assign(gen="", rsID="", consecuencia="", clinvar="", notas="")
download(exp, "variantes_priorizadas_para_anotacion.csv", "Descargar plantilla de anotación (CSV)")

details("""
- **Criterio de priorización:** ranking por p sin ajustar del modelo B (5 PCs). No se usó un umbral sugestivo preespecificado.
- **Robustez:** la ficha muestra β en A comparable y B con 3/5/10 PCs; una señal estable entre especificaciones es mejor candidata
  para seguimiento, pero sigue siendo exploratoria.
- **Siguiente paso recomendado:** anotar en GRCh37 (gen más cercano, consecuencia, frecuencia poblacional), revisar LD con el panel
  completo post-QC (antes del pruning) y buscar replicación externa.
""")
sources("salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/gwas_principal.csv + sensibilidades", "04_preparacion_genetica_definitivo.ipynb §4.3 (rs429358)")
