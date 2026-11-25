import streamlit as st
from components.ui import STRETCH,callout,html,page_header,section,sources
from utils.data import csv,fmt_dec,kpis
k=kpis();s=csv('m_comparacion_sensibilidad.csv');mi=csv('gwas_MI_resumen.csv');apoe=csv('apoe_individual.csv')
page_header('Cierre','Conclusiones','Hallazgos estadísticos, limitaciones y próximos pasos; asociación no implica causalidad.',icon='target',deco='brain')
t1,t2,t3,t4=st.tabs(['Hallazgos metodológicos','Resultados de asociación','Limitaciones','Trabajo futuro'])
with t1:
    st.markdown(f'''
- Cohorte trazable de **{k['cohorte_clinica']}** pacientes: **{k['pacientes_aoo']}** AOO observadas y **{k['aoo_faltante']}** originalmente faltantes. M1b añade una ruta ampliada separada, con incertidumbre entre veinte versiones.
- El bivariado conserva **{k['biv_FDR']}** asociaciones observadas tras FDR; **{k['biv_recurrentes_20']}** recurren en 20/20. Educación y FVFs mantienen signo 20/20 y FDR 19/20.
- El panel nuevo aporta **{k['snps_probados']:,}** SNPs probados, con **{k['marcadores_estructura']:,}** marcadores para PCA/GRM tras poda local. No se atribuye toda diferencia al MAF.
- PC1–PC10 acumulan **{k['pca_var_acum_10']:.3f} %**; cinco PCs ajustan el modelo principal y tres/diez son sensibilidad.
- El diagnóstico global del panel nuevo ya era interior; al excluir chr8 sigue interior. El paso de frontera a interior es histórico del panel anterior.
''')
with t2:
    callout(f"Resultado principal: {k['n_fdr']} asociaciones tras FDR y {k['n_bonferroni']} tras Bonferroni, con N={k['n_modelo_B']} y {k['snps_probados']:,} SNPs.",'key')
    st.markdown(f"La menor p corresponde a **{k['snp_menor_p']}**, β={k['beta_menor_p']:+.3f} años por copia ALT, p={k['p_min']:.3g}; λGC={k['lambda_gc']:.4f}. Es una señal nominal exploratoria, no un hallazgo confirmado.")
    st.dataframe(s,hide_index=True,**STRETCH)
    st.dataframe(apoe[['rs','beta','se','p','p_fdr']],hide_index=True,**STRETCH)
    st.markdown(f"MI incorporó **{k['adicionales_MI']}** casos, hasta **{k['n_modelo_MI']}** por versión; las **{len(mi)}** corridas tuvieron cero asociaciones corregidas. No se combinan sus p/q.")
with t3:
    st.markdown(f'''
- Tamaño moderado de muestra y variantes de frecuencia baja: revisar MAC y genotipos observados. La ausencia de significancia no descarta efectos pequeños.
- Cobertura del panel disponible; ausencia de matriz pre-LD y parámetros del proveedor pendientes de corroboración. La poda local para estructura no limita el conjunto probado.
- Ensamblaje pendiente de certificación y fase APOE ambigua en algunas combinaciones, aunque ambos SNPs estén presentes.
- M1b es clínico y no incluyó genotipos/PCs: la sensibilidad genética no equivale a validación de la AOO imputada.
- Temporalidad de medidas cognitivas/funcionales, error de recuerdo de AOO y ausencia de replicación externa. Asociación no implica causalidad.
''')
with t4:
    st.markdown('Confirmar documentación del panel, fase y trazabilidad de similitud genética; revisar anotación funcional y replicación externa en etapas posteriores. Mantener el resultado observado como referencia y evaluar otras especificaciones solo con justificación metodológica.')
sources('01–04 notebooks definitivos','data/kpis.json','data/gwas_MI_resumen.csv','data/apoe_individual.csv')
