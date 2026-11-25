import streamlit as st
from components.ui import STRETCH,callout,page_header,pipeline,section,sources
from utils.data import csv,jsonf,kpis
k=kpis();f=jsonf('fuentes_dashboard.json')
page_header('Cierre','Metodología y trazabilidad','Fuentes definitivas, corridas verificadas y preparación reproducible del paquete agregado.',icon='layers',deco='dna')
pipeline(['Datos clínicos','EDA','Genotipos','Estructura','PCA','GRM','LOCO','GWAS','Sensibilidad','Interpretación'],2,9)
section('Notebooks definitivos y exportaciones','Fuente de verdad')
st.dataframe(csv('trazabilidad_paginas.csv'),hide_index=True,**STRETCH)
st.json(f['corridas'])
callout('El cambio de nombre de los notebooks no renombra las carpetas de salida. La preparación coteja las rutas impresas por el notebook ejecutado con el manifiesto integrado y verifica indicadores antes de publicar el paquete. La carpeta dashboard/ es histórica y no se usa como raíz de datos.','info')
section('Metodología','Dos rutas de AOO y un panel actual')
st.markdown(f'''
- **Clínica:** {k['cohorte_clinica']} pacientes; {k['pacientes_aoo']} AOO observadas y {k['aoo_faltante']} faltantes originales, preservados.
- **MICE–PMM M1b:** imputa la brecha edad de evaluación − AOO y reconstruye AOO; {k['n_imputaciones']} versiones de la misma cohorte. MissForest es sensibilidad separada.
- **Bivariado:** Spearman, Mann–Whitney y Kruskal–Wallis con **eta cuadrado basado en H (η²_H)**; IC bootstrap observados y Dunn–Holm. BH se aplica por ruta/imputación; la recurrencia MI es descriptiva.
- **Panel actual:** `functional-variants.txt`; {k['snps_probados']:,} SNPs de asociación. El profesor informó MAF > 0,01; falta corroborar GCR/HWE/poda del proveedor y certificar ensamblaje.
- **Estructura:** {k['marcadores_estructura']:,} marcadores tras poda local de dosis (ventana 50, paso 5, r² > 0,5). Esta selección solo afecta PCA/GRM, no el universo de GWAS.
- **PCA:** todos los genotipados, imputación técnica temporal por media, estandarización y Gram individuo × individuo. Veinte permutaciones y banderas exploratorias sin exclusión.
- **GWAS observado principal:** Modelo B con sexo, educación agrupada, cinco PCs y GRM–LOCO; REML bajo el nulo por cromosoma y Wald bilateral. N={k['n_modelo_B']}; λGC={k['lambda_gc']:.4f}.
- **Sensibilidad:** 3/10 PCs y A comparable, con mismas filas. AOO MI: {k['adicionales_MI']} casos adicionales, N={k['n_modelo_MI']} por versión. M1b no incluyó PCs ni genotipos; no se combinan p/q ni se usa la media individual de AOO para inferencia.
- **APOE:** rs429358 y rs7412 probados individualmente; algunas configuraciones no faseadas son ambiguas. APOE no fue covariable del Modelo B.
''')
section('Controles','Concordancia y privacidad')
audit=csv('auditoria_dashboard.csv');st.caption(f'{len(audit)} controles; {int(audit.Estado.eq("FAIL").sum())} fallidos. No se ejecutaron los notebooks ni los análisis genéticos.')
with st.expander('Ver auditoría y pendientes'):
    st.dataframe(audit,hide_index=True,**STRETCH);st.json(f['pendientes'])
callout(f['privacidad'],'neutral')
section('Regeneración y arranque','Desde dashboard_alzheimer/dashboard_alzheimer/')
st.code('python prepare_dashboard_data.py --project-root ../..\npython -m streamlit run app.py',language='bash')
sources(*f['notebooks'],'data/fuentes_dashboard.json','data/trazabilidad_paginas.csv')
