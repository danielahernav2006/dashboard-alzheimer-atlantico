import plotly.graph_objects as go
import streamlit as st
from components.ui import STRETCH,callout,details,html,page_header,plot,section,sources
from utils.data import csv,fmt_int,kpis
from utils.theme import BURGUNDY,PETROL,GRAY,BLUE_GRAY
k=kpis()
page_header('Datos','Cohorte y flujo de pacientes','Ruta principal con AOO observada y sensibilidad ampliada MICE–PMM M1b.',icon='users',deco='network')
flow=csv('cohort_flow.csv')
c1,c2=st.columns([1,1.25])
with c1:
    section('Ruta observada','Denominadores distintos')
    desc=['Cohorte clínica maestra','Desenlace observado de referencia','Casos de la cohorte con genotipo enlazado','Genotipo y AOO observada','Sexo y educación completos']
    parts=[f'<div class="node"><div><div class="l">{r.etapa}</div><div class="d">{desc[i]}</div></div><div class="n">{fmt_int(r.n)}</div></div>' for i,r in flow.iterrows()]
    html('<div class="flow">'+'<div class="arrow">↓</div>'.join(parts)+'</div>')
    st.caption('La disponibilidad clínica de AOO y el enlace genético son ramas distintas; no deben leerse como exclusiones secuenciales entre todos los escalones.')
with c2:
    labels=['Cohorte','AOO observada','AOO faltante','Genotipo + AOO','Sin genotipo','Genotipo sin AOO','Modelo B observado','Sin covariables completas']
    values=[k['pacientes_aoo'],k['aoo_faltante'],k['enlaces_con_aoo'],k['pacientes_aoo']-k['enlaces_con_aoo'],k['enlaces_sin_aoo'],k['n_modelo_B'],k['enlaces_con_aoo']-k['n_modelo_B']]
    fig=go.Figure(go.Sankey(node=dict(label=labels,color=[BURGUNDY,PETROL,GRAY,PETROL,GRAY,GRAY,BURGUNDY,GRAY]),link=dict(source=[0,0,1,1,2,3,3],target=[1,2,3,4,5,6,7],value=values)))
    fig.update_layout(title='Disponibilidad de AOO, genotipo y covariables',height=420);plot(fig)
section('Ruta ampliada','Imputación múltiple')
st.dataframe(csv('u_rutas_analiticas.csv'),hide_index=True,**STRETCH)
callout(f'M1b imputa la <b>brecha = edad de evaluación − AOO</b> y reconstruye AOO = edad de evaluación − brecha imputada. Las {k["n_imputaciones"]} bases contienen los mismos {k["cohorte_clinica"]} pacientes y preservan las {k["pacientes_aoo"]} AOO observadas. La fuente original conserva {k["aoo_faltante"]} desconocidas.','info')
st.dataframe(csv('gwas_MI_elegibilidad.csv'),hide_index=True,**STRETCH)
callout(f'{k["adicionales_MI"]} de los {k["aoo_faltante"]} casos originalmente sin AOO tienen genotipo y covariables completas: N = {k["n_modelo_MI"]} en cada sensibilidad genética. No se apilan las bases ni se reemplaza AOO por la media individual.','key')
section('Muestras por modelo','Genética')
st.dataframe(csv('m_resumen_muestras_modelos.csv'),hide_index=True,**STRETCH)
st.dataframe(csv('g_resumen_cruce.csv'),hide_index=True,**STRETCH)
callout(f'{k["muestras_geneticas"]-k["enlaces_genetico_clinicos"]} muestras genéticas están fuera de la cohorte enlazada. No se les atribuye diagnóstico ni identidad por prefijo. Participan en estructura; el GWAS de AOO utiliza casos elegibles.','neutral')
details('La AOO observada proviene de la fuente clínica oficial. Las imputaciones clínicas ya existían y no se recalculan en el dashboard. MissForest se conserva como sensibilidad, separada de MICE–PMM.')
sources('01_preprocesamiento_definitivo.ipynb','04_preparacion_genetica_definitivo.ipynb','data/cohort_flow.csv','data/gwas_MI_elegibilidad.csv')
