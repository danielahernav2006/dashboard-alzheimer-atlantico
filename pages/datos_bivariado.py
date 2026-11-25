import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.ui import STRETCH,callout,details,download,kpis,page_header,plot,section,sources
from utils.data import csv,kpis as load_kpis
from utils.theme import BURGUNDY,PETROL,GOLD
k=load_kpis();obs=csv('b_resultados_bivariados_observados.csv');mi=csv('b_resumen_estabilidad_bivariada_mi.csv')
page_header('Datos','Análisis bivariado: relaciones con AOO','Ruta observada y estabilidad descriptiva frente a MICE–PMM M1b. Asociación exploratoria, sin interpretación causal.',icon='scale',deco='network')
kpis([{'label':'Consideradas','value':str(k['biv_variables']),'icon':'layers'},{'label':'Evaluables','value':str(k['biv_evaluables']),'icon':'check'},{'label':'FDR observada','value':str(k['biv_FDR']),'icon':'target'},{'label':'Observadas FDR en 20/20','value':str(k['biv_recurrentes_20']),'icon':'chart'}])
callout('Cada prueba mantiene su familia original: Spearman, Mann–Whitney o Kruskal–Wallis. BH se aplica por separado en la ruta observada y dentro de cada imputación. La recurrencia FDR es sensibilidad descriptiva al modelo M1b; no constituye un q combinado. Las bases comparten las AOO observadas.','info')
section('Evidencia observada','Tabla filtrable')
fam=st.multiselect('Familias',sorted(obs.familia.dropna().unique()));q=st.text_input('Buscar variable');only=st.toggle('Solo FDR observada < 0,05',False)
t=obs.copy()
if fam:t=t[t.familia.isin(fam)]
if q:t=t[t.variable.str.contains(q,case=False,na=False)|t.columna.str.contains(q,case=False,na=False)]
if only:t=t[t.p_ajustado_fdr.lt(.05)]
cols=['variable','familia','prueba','n','medida_efecto','medida_efecto_nombre','ic95_efecto_inf','ic95_efecto_sup','p_valor','p_ajustado_fdr','temporalidad','riesgo_leakage_aoo']
st.dataframe(t[cols],hide_index=True,**STRETCH);download(t[cols],'bivariado_observado_filtrado.csv')
section('Estabilidad entre imputaciones','Efectos y recurrencia')
var=st.selectbox('Variable evaluable',mi.loc[mi.prueba_observada.notna(),'columna'].tolist(),format_func=lambda c:mi.set_index('columna').variable[c])
r=mi.set_index('columna').loc[var]
st.dataframe(mi[mi.columna.eq(var)][['variable','prueba_observada','medida_efecto_nombre','n_observado','efecto_observado','FDR_observado','efecto_MI_medio','efecto_MI_min','efecto_MI_max','n_mismo_signo','recurrencia_FDR','q_MI_mediano']],hide_index=True,**STRETCH)
fig=go.Figure(go.Scatter(x=[r.efecto_observado,r.efecto_MI_medio],y=['Observado','Media de efectos MI'],mode='markers',marker=dict(size=13,color=[BURGUNDY,PETROL]),error_x=dict(type='data',symmetric=False,array=[0,r.efecto_MI_max-r.efecto_MI_medio],arrayminus=[0,r.efecto_MI_medio-r.efecto_MI_min])))
fig.update_layout(title=f'{r.variable} · {r.medida_efecto_nombre}',xaxis_title='Efecto; rango empírico MI (no IC combinado)');plot(fig)
rank_n=st.slider('Variables en el ranking',10,50,35,5)
rank=mi.sort_values('n_imputaciones_FDR_significativa',ascending=False).head(rank_n)
plot(px.bar(rank,x='n_imputaciones_FDR_significativa',y='variable',orientation='h',color_discrete_sequence=[PETROL],height=760,labels={'n_imputaciones_FDR_significativa':'Imputaciones con FDR < 0,05'}))
st.dataframe(csv('b_fdr_por_imputacion.csv'),hide_index=True,**STRETCH)
with st.expander('Dunn–Holm y motivos de no evaluación'):
    for name in ['dunn_observado','resumen_dunn_mi','motivos_no_evaluacion']:
        table=csv('b_'+name+'.csv');st.markdown('**'+name.replace('_',' ')+'**');st.dataframe(table,hide_index=True,**STRETCH);download(table,name+'.csv')
with st.expander('Procedencia de M1b y señales sensibles a la ampliación'):
    st.dataframe(csv('b_auditoria_predictores_m1b.csv'),hide_index=True,**STRETCH)
    st.dataframe(csv('b_auditoria_participacion_senales_m1b.csv'),hide_index=True,**STRETCH)
    st.dataframe(csv('b_senales_emergentes_mi.csv'),hide_index=True,**STRETCH)
    st.dataframe(csv('b_hipertension_contraste_codigos.csv'),hide_index=True,**STRETCH)
callout('Educación y FVFs conservan el signo en 20/20 y FDR < 0,05 en 19/20. Las pruebas cognitivas, funcionalidad, vivienda e informante caracterizan la cohorte; la elegibilidad como covariable del GWAS depende de la pregunta del modelo y de la temporalidad. La hipertensión se interpreta como contraste entre códigos mientras sus etiquetas no estén documentadas.','neutral')
details('Kruskal–Wallis: eta cuadrado basado en H (η²_H) = (H − k + 1)/(n − k). Se conservan los efectos e IC bootstrap observados. Los rangos MI no son IC bootstrap ni estimadores combinados. Las covariables clínicas mantienen sus faltantes; cada contraste utiliza pares completos dentro de cada base. No se usan las 7.820 filas apiladas como pacientes independientes.')
sources('03_bivariado_definitivo.ipynb','salidas/bivariado_mi_revisado/','data/b_resumen_estabilidad_bivariada_mi.csv')
