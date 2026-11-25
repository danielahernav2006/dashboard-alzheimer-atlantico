import numpy as np
import plotly.graph_objects as go
import streamlit as st

from components.ui import callout, details, html, page_header, plot, section, sources
from utils.data import csv, fmt_dec, kpis
from utils.theme import BURGUNDY, GOLD_DARK, PETROL

k = kpis()
page_header("Contexto", "Problema y objetivos",
            "El estudio no pregunta quién desarrolla Alzheimer, sino <b>cuándo</b> comienza en quienes ya lo tienen.",
            icon="brain", deco="brain")

section("Dos preguntas distintas", "Riesgo vs. edad de inicio")
c1, c2 = st.columns(2)
with c1:
    html("""<div class="card"><span class="badge gray">No es el objetivo</span>
    <h4 style="margin-top:8px">Riesgo de desarrollar Alzheimer</h4>
    <p>Compara <b>casos frente a controles</b>. El desenlace es binario (enfermo / no enfermo) y los modelos
    estiman razones de odds. Es el diseño clásico de los GWAS de susceptibilidad (CLU, PICALM, 11 loci de Lambert et al.).</p>
    <p style="font-size:.88rem;color:#66707A">Pregunta: <i>¿qué variantes aumentan la probabilidad de enfermar?</i></p></div>""")
with c2:
    html("""<div class="card" style="border-color:#E6CFD8"><span class="badge solid">Este estudio</span>
    <h4 style="margin-top:8px">Edad de inicio (AOO)</h4>
    <p>Usa <b>solo pacientes</b> y modela la AOO como <b>variable cuantitativa continua</b> (años). Cada SNP se
    evalúa por su asociación lineal con la AOO mediante un modelo lineal mixto.</p>
    <p style="font-size:.88rem;color:#66707A">Pregunta: <i>¿qué variantes se asocian con un inicio más temprano o más tardío?</i></p></div>""")

section("Cómo leer β", "Dirección de la asociación")
html("""
<div class="dir">
  <div class="c pos"><div class="h">β &gt; 0</div>
    <div class="s">Cada copia adicional del alelo <b>ALT</b> se asocia con una <b>AOO mayor</b>: inicio más tardío, en promedio, en esta cohorte.</div>
    <div class="agebar"><div class="m" style="left:45%;background:#7B8791"></div><div class="m" style="left:70%;background:#3E6870"></div></div>
    <div style="font-size:.78rem;color:#7B8791">referencia → con ALT (desplazamiento hacia edades mayores)</div></div>
  <div class="c neg"><div class="h">β &lt; 0</div>
    <div class="s">Cada copia adicional del alelo <b>ALT</b> se asocia con una <b>AOO menor</b>: inicio más temprano, en promedio, en esta cohorte.</div>
    <div class="agebar"><div class="m" style="left:25%;background:#721C3B"></div><div class="m" style="left:50%;background:#7B8791"></div></div>
    <div style="font-size:.78rem;color:#7B8791">con ALT ← referencia (desplazamiento hacia edades menores)</div></div>
</div>""")
callout("β se expresa en <b>años de AOO por copia del alelo ALT</b> (codificación aditiva 0/1/2). ALT designa el alelo "
        "alternativo del panel: no implica riesgo ni protección. Una asociación estadística <b>no</b> demuestra que la "
        "variante cause el adelanto o el retraso del inicio.", "warn")

section("La variable de respuesta", "AOO en la cohorte")
t = csv("uni_descriptivos.csv").query("columna=='aoo'").iloc[0]
h = csv("uni_histogramas.csv").query("columna=='aoo'")
c1,c2=st.columns([2,1])
with c1:
    fig=go.Figure(go.Bar(x=(h.izq+h.der)/2,y=h.n,width=h.der-h.izq,marker_color=BURGUNDY))
    fig.update_layout(title="AOO observada · referencia",xaxis_title="AOO (años)",yaxis_title="Pacientes");plot(fig)
with c2:
    html(f"<div class='card'><h4>AOO observada</h4><p>{int(t.n)} valores; media {t.media:.2f}, DE {t.DE:.2f}; mediana {t.mediana:.1f}; rango {t['min']:.0f}–{t['max']:.0f}.</p></div>")
    st.caption("La fuente conserva sus faltantes. La ruta ampliada MICE–PMM M1b usa veinte bases separadas, preservando los valores observados.")

section("Objetivos", "Lo que busca el proyecto")
html("""<div class="card"><h4>Objetivo general</h4>
<p>Identificar variantes genéticas asociadas con la edad de inicio de la enfermedad de Alzheimer en pacientes del Atlántico,
mediante análisis de estructura poblacional y asociación genética, sobre una base clínica caracterizada con rigor.</p>
<h4 style="margin-top:12px">Objetivos específicos (siguiendo el flujo de los notebooks)</h4>
<ol>
<li>Integrar y depurar las fuentes clínicas y construir una cohorte trazable con AOO revisada (notebook 01).</li>
<li>Describir la cohorte y explorar la asociación de variables clínicas, sociodemográficas y neuropsicológicas con la AOO (02–03).</li>
<li>Preparar la matriz genotípica (dosis 0/1/2) y enlazarla de forma inequívoca con la clínica (04).</li>
<li>Caracterizar la estructura poblacional (PCA) y la similitud genética entre individuos (GRM) (04).</li>
<li>Estimar la asociación SNP–AOO con un modelo lineal mixto con GRM LOCO y evaluar su sensibilidad (04).</li>
</ol></div>""")

details("""
- **Unidad de análisis:** paciente con Alzheimer de la cohorte maestra HXGEN (391). La AOO está disponible en 370.
- **Desenlace:** `aoo`, edad de inicio revisada (años), tomada de la fuente consolidada; las edades históricas de
  neuropsicología se conservan solo para auditoría.
- **Estimando genético:** cambio esperado en AOO por copia adicional del alelo ALT, ajustado por sexo, educación
  agrupada y PC1–PC5, con un efecto genético aleatorio de covarianza proporcional a la GRM LOCO.
- **Interpretación:** exploratoria y no causal. Un β ≠ 0 describe covariación en esta muestra; puede deberse a
  desequilibrio de ligamiento, estructura residual, azar o sesgos de medición.
""")
sources("data/uni_histogramas.csv ← salidas/base_full.pkl", "00_presentacion.ipynb", "04_preparacion_genetica_definitivo.ipynb (7.1)")
