import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.ui import STRETCH,callout,details,download,page_header,plot,section,sources
from utils.data import csv,variables_meta,kpis
from utils.theme import BURGUNDY,PETROL,GRAY
k=kpis()
page_header('Datos','Análisis univariado','AOO observada como referencia y resúmenes entre veinte imputaciones; las demás variables conservan su distribución clínica original.',icon='chart',deco='dna')
section('AOO observado','Referencia empírica')
st.dataframe(csv('uni_descriptivos.csv').query("columna=='aoo'").drop(columns='columna'),hide_index=True,**STRETCH)
h=csv('uni_histogramas.csv').query("columna=='aoo'")
fig=go.Figure(go.Bar(x=(h.izq+h.der)/2,y=h.n,width=h.der-h.izq,marker_color=BURGUNDY))
fig.update_layout(title=f'AOO observada · n = {k["pacientes_aoo"]}',xaxis_title='AOO (años)',yaxis_title='Pacientes');plot(fig)
section('AOO ampliada mediante imputación múltiple','Veinte versiones alternativas')
st.dataframe(csv('u_comparacion_aoo_observado_vs_mi.csv'),hide_index=True,**STRETCH)
route=st.radio('Distribución que se muestra',['Observada y veinte bases MI','Solo AOO observada'],horizontal=True)
d=csv('aoo_distribuciones_MI.csv');fig=go.Figure()
for im,g in d.groupby('imputacion'):
    if route.startswith('Solo') and im!=0:continue
    fig.add_trace(go.Scatter(x=(g.izq+g.der)/2,y=g.densidad,mode='lines',line=dict(color=BURGUNDY if im==0 else PETROL,width=3 if im==0 else 1),opacity=1 if im==0 else .2,name='Observada' if im==0 else 'Una base MI',showlegend=im in [0,1]))
fig.update_layout(title='AOO observada y veinte distribuciones MI',xaxis_title='AOO (años)',yaxis_title='Densidad de frecuencia');plot(fig)
c1,c2=st.columns(2)
with c1:st.image('data/distribucion_aoo_observado_vs_mi.png',caption='Figura exportada por el univariado definitivo.')
with c2:st.image('data/boxplots_aoo_por_imputacion.png',caption='Una distribución por base; no son individuos independientes entre bases.')
with st.expander('Descriptivos, incertidumbre de la media y extremos por imputación'):
    for name in ['descriptivos_aoo_por_imputacion','resumen_descriptivos_aoo_mi','media_aoo_rubin','outliers_aoo_por_imputacion']:
        t=csv('u_'+name+'.csv');st.dataframe(t,hide_index=True,**STRETCH);download(t,name+'.csv')
callout('La similitud entre distribuciones no valida los AOO desconocidos. MICE–PMM generó valores plausibles mediante validación interna; la regresión hacia la media limita la recuperación de extremos. Los valores observados se conservan y no se eliminan por Tukey.','warn')
if (csv('u_resumen_discrepancia_missforest.csv') is not None):
    with st.expander('MissForest: sensibilidad descriptiva'):
        st.dataframe(csv('u_resumen_discrepancia_missforest.csv'),hide_index=True,**STRETCH)
section('Explorador de variables','Fuente original · tablas agregadas')
meta=variables_meta();stats=csv('uni_descriptivos.csv');cats=csv('uni_categorias.csv');hist=csv('uni_histogramas.csv')
meta=meta[meta.columna.isin(set(stats.columna)|set(cats.columna))]
fam=st.selectbox('Familia',['Todas']+sorted(meta.familia.dropna().unique()))
m=meta if fam=='Todas' else meta[meta.familia.eq(fam)]
col=st.selectbox('Variable',m.columna.tolist(),format_func=lambda c:meta.set_index('columna').etiqueta[c])
r=meta.set_index('columna').loc[col];st.caption(f'{r.tipo_analitico} · {r.fuente} · leakage: {r.riesgo_leakage_aoo}')
if col in set(stats.columna):
    t=stats[stats.columna.eq(col)].drop(columns='columna');st.dataframe(t,hide_index=True,**STRETCH)
    h=hist[hist.columna.eq(col)];fig=go.Figure(go.Bar(x=(h.izq+h.der)/2,y=h.n,width=h.der-h.izq,marker_color=BURGUNDY));fig.update_layout(xaxis_title=r.etiqueta,yaxis_title='Pacientes');plot(fig);download(t,'descriptivos_'+col+'.csv')
else:
    t=cats[cats.columna.eq(col)].drop(columns='columna');plot(px.bar(t,x='n',y='categoria',orientation='h',color_discrete_sequence=[PETROL]));st.dataframe(t,hide_index=True,**STRETCH);download(t,'frecuencias_'+col+'.csv')
details('Cada descriptivo MI se calcula dentro de una sola base de pacientes. Rubin se aplica a la media y su varianza de muestreo: T = Ū + (1 + 1/m) B. Medianas, cuantiles y extremos se resumen empíricamente entre bases; no se aplica Rubin automáticamente. Las otras variables no se replican ni se imputan para este análisis.')
sources('02_univariado_definitivo.ipynb','salidas/univariado_mi/','data/uni_descriptivos.csv')
