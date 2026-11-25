import pandas as pd
import streamlit as st

from components.ui import STRETCH, callout, html, page_header, section, sources
from utils.data import csv, fmt_dec, kpis

k = kpis()
page_header("Asociación", "Modelos lineales mixtos (LMM)",
            "Un modelo por SNP: efectos fijos para el SNP y las covariables, y un efecto genético aleatorio con covarianza "
            "proporcional a la GRM LOCO.", icon="sigma", deco="dna")

section("Especificaciones preespecificadas", "A y B")
c1, c2 = st.columns(2)
with c1:
    html(f"""<div class="card"><span class="badge gray">MODELO A · genético estructural</span>
    <div class="eq" style="margin-top:10px">AOO ~ <span class="snp">SNP</span> + <span class="cov">PC1–PC5</span> + <span class="rand">u<sub>GRM_LOCO</sub></span></div>
    <p style="margin-top:10px;font-size:.92rem">Asociación genética ajustada solo por estructura poblacional y similitud
    genética. <b>A completo</b> usa {k['enlaces_con_aoo']} pacientes; <b>A comparable</b> usa las mismas {k['n_modelo_B']} filas que B para compararlos.</p></div>""")
with c2:
    html(f"""<div class="card" style="border-color:#D8B8C4"><span class="badge solid">MODELO B · clínico-genético · PRINCIPAL</span>
    <div class="eq" style="margin-top:10px">AOO ~ <span class="snp">SNP</span> + <span class="cov">sexo + educación + PC1–PC5</span> + <span class="rand">u<sub>GRM_LOCO</sub></span></div>
    <p style="margin-top:10px;font-size:.92rem">Añade las covariables basales seleccionadas. Casos completos: <b>{k['n_modelo_B']}</b>
    pacientes ({k['enlaces_con_aoo']-k['n_modelo_B']} sin covariables completas). Es la base de la inferencia principal y de las sensibilidades 3/10 PCs.</p></div>""")

t1, t2 = st.tabs(["Resumen", "Detalle metodológico"])
with t1:
    html(f"""<div class="card">
    <h4>¿Qué hace el modelo?</h4>
    <ul>
    <li><b style="color:#721C3B">SNP</b>: dosis 0/1/2 del alelo ALT. Su coeficiente <b>β</b> es el cambio promedio de AOO (años) por copia.</li>
    <li><b style="color:#3E6870">Efectos fijos</b>: sexo, educación (factor, referencia No escolarizada) y PC1–PC5, que ajustan diferencias clínicas
        y de ancestría global.</li>
    <li><b style="color:#8F6A38">Efecto aleatorio</b>: captura que personas genéticamente parecidas (según la GRM) tienden a tener AOO más parecidas,
        evitando falsos positivos por parentesco o estructura fina.</li>
    <li><b>LOCO</b>: para cada SNP, la GRM excluye su propio cromosoma.</li>
    <li><b>Prueba</b>: Wald bilateral para β = 0; luego corrección Bonferroni y FDR sobre los SNPs efectivamente evaluados.</li>
    </ul></div>""")
    tab = pd.DataFrame([
        ["A completo", k["enlaces_con_aoo"], "SNP + PC1–PC5", "GRM LOCO", "Referencia descriptiva de la muestra máxima"],
        ["A comparable", k["n_modelo_B"], "SNP + PC1–PC5", "GRM LOCO", "Comparación con B en las mismas filas"],
        ["B · 5 PCs (principal)", k["n_modelo_B"], "SNP + sexo + educación + PC1–PC5", "GRM LOCO", "Inferencia principal"],
        ["B · 3 PCs", k["n_modelo_B"], "SNP + sexo + educación + PC1–PC3", "GRM LOCO", "Sensibilidad estructural"],
        ["B · 10 PCs", k["n_modelo_B"], "SNP + sexo + educación + PC1–PC10", "GRM LOCO", "Sensibilidad estructural"],
    ], columns=["Especificación", "n", "Efectos fijos", "Efecto aleatorio", "Rol"])
    st.dataframe(tab, hide_index=True, **STRETCH)
    callout(f"Componentes de varianza del modelo B (22 nulos LOCO, REML): h² del componente GRM entre "
            f"{fmt_dec(k['h2_loco_min_B'],3)} y {fmt_dec(k['h2_loco_max_B'],3)}, todos con solución interior. "
            "Describen el ajuste en esta muestra y modelo; no son una estimación de heredabilidad poblacional de la AOO.", "info")
with t2:
    st.markdown(r"""
**Modelo para un SNP del cromosoma $c$ (modelo B):**

$$\mathrm{AOO}_i=\beta_0+\beta_{\mathrm{SNP}}G_{ic}+\beta_{\mathrm{sexo}}\mathrm{Sexo}_i+\sum_{l}\beta_{\mathrm{edu},l}\,\mathrm{Edu}_{il}+\sum_{j=1}^{5}\beta_j\mathrm{PC}_{ij}+u_{i,-c}+\varepsilon_i$$

$$u_{-c}\sim N(0,\sigma^2_{g,c}K_{-c}),\qquad \varepsilon\sim N(0,\sigma^2_{e,c}I),\qquad V_c=\sigma^2_{g,c}K_{-c}+\sigma^2_{e,c}I$$

- **Efectos fijos:** intercepto, SNP, sexo, 3 indicadoras de educación agrupada (Primaria, Preparatoria/bachillerato, Educación superior;
  referencia No escolarizada) y PC1–PC5 → 11 parámetros fijos por SNP (10 en el nulo); rango completo verificado.
- **Efecto aleatorio:** $u$ con covarianza proporcional a la GRM LOCO $K_{-c}$ (submatriz 334 × 334).
- **REML:** para cada cromosoma se estima $h^2=\sigma^2_g/(\sigma^2_g+\sigma^2_e)$ bajo el modelo nulo (sin SNP), minimizando
  la −2 log-verosimilitud restringida perfilada; el optimizador se contrastó con una malla densa de $h^2$.
- **Esquema tipo EMMAX:** los componentes de varianza del nulo se fijan y se reutilizan para todos los SNPs del cromosoma;
  cada SNP se estima por GLS rotando el modelo con la descomposición espectral de $K_{-c}$ ($y^\* = U^\top y$, pesos $1/\sqrt{\lambda+\delta}$).
- **Prueba de Wald:** $z=\hat\beta_{\mathrm{SNP}}/\mathrm{SE}$, bilateral. El motor espectral se validó contra una solución GLS
  independiente por Cholesky en SNPs piloto (modelos de sexo + 5 PCs y modelo B).
- **Faltantes del SNP:** la media observada del SNP se usa solo en el bloque temporal para mantener el mismo conjunto de pacientes y la misma
  covarianza; la frecuencia ALT se calcula con genotipos observados.
- **Multiplicidad:** Bonferroni 0,05 dividido por el número real de SNPs probados (error familiar) y Benjamini–Hochberg (FDR) dentro de cada especificación.
- **λGC:** mediana de $z^2$ / mediana de $\chi^2_1$; diagnóstico descriptivo, no se usa para recalibrar.
- **Sin APOE como covariable:** cambiaría el estimando. rs429358 y rs7412 se probaron individualmente; algunas combinaciones sin fase admiten más de un diplotipo.
""")
    st.dataframe(csv("m_resumen_muestras_modelos.csv"), hide_index=True, **STRETCH)

sources("salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/resumen_gwas.csv", "salidas/genetica_panel_nuevo_MI_integrado/gwas/ (corrida del manifiesto)/modelo_nulo_lmm.csv",
        "04_preparacion_genetica_definitivo.ipynb §7.2–7.9")
