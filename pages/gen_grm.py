import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.ui import STRETCH,callout,details,download,kpis,page_header,plot,section,sources
from utils.data import csv,kpis as load_kpis,fmt_int
from utils.theme import BURGUNDY,PETROL,GRAY
k=load_kpis();res=csv('grm_resumen.csv');umb=csv('grm_umbrales.csv')
page_header('Genética','GRM: matriz de relación genética','Similitud global estimada con los marcadores de estructura del panel nuevo. No equivale a identidad genotípica ni confirma parentesco.',icon='grid',deco='network')
kpis([{'label':'Individuos','value':str(k['muestras_geneticas']),'icon':'users','kind':'genetic'},{'label':'Marcadores de estructura','value':fmt_int(k['marcadores_estructura']),'icon':'dna','kind':'genetic'},{'label':'Pares GRM > 0,8','value':str(int(umb.loc[umb.umbral.eq(.8),'pares'].iloc[0])),'icon':'network'}])
section('Distribuciones','Diagonal y fuera de diagonal')
c1,c2=st.columns(2)
for container,name,title in [(c1,'grm_hist_diagonal.csv','Diagonal'),(c2,'grm_hist_offdiag.csv','Similitud entre pares')]:
    with container:
        h=csv(name);fig=go.Figure(go.Bar(x=(h.izq+h.der)/2,y=h.n,width=h.der-h.izq,marker_color=PETROL));fig.update_layout(title=title,xaxis_title='GRM',yaxis_title='Frecuencia');plot(fig)
st.dataframe(res,hide_index=True,**STRETCH);st.dataframe(umb,hide_index=True,**STRETCH)
section('Heatmap agregado','Bloques de la muestra AOO')
h=csv('grm_heatmap_bloques.csv').pivot(index='bloque_1',columns='bloque_2',values='GRM_media');plot(px.imshow(h,color_continuous_scale='RdBu_r',color_continuous_midpoint=0,labels={'color':'GRM media'}),height=560)
st.caption('Cada celda resume un bloque de individuos; se omite la diagonal individual. No se publican matrices individuales, IDs ni un orden recuperable de pacientes.')
section('Pares de similitud alta','Concordancia e IBS')
con=csv('grm_concordancia_extremos.csv');fig=px.scatter(con,x='GRM',y='concordancia_pct',hover_data=['Par','SNPs_comparables']);fig.add_hline(y=99.5,line_dash='dash',annotation_text='Bandera exploratoria 99,5 %');plot(fig)
st.dataframe(con,hide_index=True,**STRETCH);download(con,'concordancia_pares_agregada.csv')
callout('Los pares se muestran con números de tabla, sin identificadores. GRM alta, concordancia de dosis e identidad técnica son conceptos diferentes. No se confirma una repetición técnica ni se excluye ninguna muestra con estos diagnósticos.','warn')
details('GRM = ZZᵀ/M; Z = (G − 2p)/√(2p(1−p)), con frecuencias observadas en los genotipados. Los faltantes aportan cero tras centrar en bloques temporales. M es el número de marcadores de estructura, no el universo completo probado en GWAS. IBS2/IBS1/IBS0 corresponden a diferencias absolutas de dosis 0/1/2 sobre SNPs comparables; no son identidad por descendencia.')
sources('04_preparacion_genetica_definitivo.ipynb §6','data/grm_resumen.csv','data/grm_concordancia_extremos.csv')
