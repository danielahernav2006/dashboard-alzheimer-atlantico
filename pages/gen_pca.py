import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.ui import STRETCH,callout,details,kpis,page_header,plot,section,sources
from utils.data import csv,kpis as load_kpis,fmt_dec,fmt_int
from utils.theme import BURGUNDY,PETROL,GRAY,GOLD
k=load_kpis();pcs=csv('pca_individuos.csv');var=csv('pca_varianza.csv');par=csv('pca_analisis_paralelo.csv')
page_header('Genética','PCA y estructura poblacional','Todos los genotipados; AOO, sexo y variables clínicas no intervienen en el cálculo. Visualización sin identificadores de pacientes.',icon='network',deco='network')
kpis([{'label':'Individuos','value':str(len(pcs)),'icon':'users','kind':'genetic'},{'label':'Marcadores de estructura','value':fmt_int(k['marcadores_estructura']),'icon':'dna','kind':'genetic'},{'label':'Varianza PC1','value':f'{var.iloc[0,1]:.2f} %','icon':'chart'},{'label':'PCs > p95 nulo','value':f'{int(par.supera_p95.sum())}/{len(par)}','icon':'sigma'},{'label':'Extremos PC1–PC3','value':str(int(pcs.extremo_PC1_PC3.sum())),'icon':'alert'}])
section('Varianza explicada','Scree y análisis paralelo')
c1,c2=st.columns(2)
with c1:plot(px.bar(var,x='PC',y='Varianza explicada (%)',color_discrete_sequence=[BURGUNDY]))
with c2:
    fig=go.Figure()
    for col,name in [('autovalor_observado','Observado'),('autovalor_nulo_p95','Percentil 95 nulo')]:fig.add_trace(go.Scatter(x=par.PC,y=par[col],name=name,mode='lines+markers'))
    plot(fig)
st.caption(f'PC1–PC10 acumulan {k["pca_var_acum_10"]:.3f} %. Las {int(par.n_permutaciones.iloc[0])} permutaciones aportan evidencia adicional de estructura; no eligen automáticamente los PCs del GWAS.')
section('Proyecciones 2D','Selector interactivo')
c1,c2=st.columns(2);opts=var.PC.tolist();x=c1.selectbox('Eje X',opts,index=0);y=c2.selectbox('Eje Y',opts,index=1)
d=pcs.assign(Grupo=np.where(pcs.extremo_PC1_PC3,'Bandera exploratoria','Sin bandera PC1–PC3'))
fig=px.scatter(d,x=x,y=y,color='Grupo',color_discrete_map={'Bandera exploratoria':GOLD,'Sin bandera PC1–PC3':PETROL},hover_data={c:False for c in d.columns if c not in [x,y,'Grupo']})
plot(fig)
section('PC1–PC2–PC3','PCA 3D sin identificadores')
fig3=px.scatter_3d(d[['PC1','PC2','PC3','Grupo']],x='PC1',y='PC2',z='PC3',color='Grupo',color_discrete_map={'Bandera exploratoria':GOLD,'Sin bandera PC1–PC3':PETROL})
fig3.update_traces(hovertemplate='PC1=%{x:.3f}<br>PC2=%{y:.3f}<br>PC3=%{z:.3f}<extra></extra>');plot(fig3,key='pca_3d',height=620)
st.download_button('Descargar PCA 3D anónimo (HTML)',fig3.to_html(include_plotlyjs=True).encode('utf8'),'pca_3d_sin_identificadores.html','text/html')
callout('La rotación ayuda a distinguir puntos superpuestos en 2D y revisar la nube. La separación visual no identifica grupos biológicos ni justifica excluir personas. Los puntos no incluyen IDs, atributos clínicos ni el orden de filas de la fuente.','info')
section('Distancia estandarizada y extremos','Diagnóstico exploratorio')
fig=px.histogram(pcs,x='dist_std_PC1_PC3',color='extremo_PC1_PC3',nbins=40,barmode='overlay',labels={'dist_std_PC1_PC3':'Norma euclidiana de z-scores PC1–PC3'});plot(fig)
st.dataframe(csv('pca_rastreo_resumen.csv'),hide_index=True,**STRETCH)
st.dataframe(csv('pca_calidad_extremos.csv'),hide_index=True,**STRETCH)
st.caption('Calidad genética: denominador de marcadores de estructura; comparación descriptiva, sin exclusiones.')
st.dataframe(csv('g_comparacion_clinica_extremos.csv'),hide_index=True,**STRETCH)
callout('Se mantiene |z| ≥ 3 como bandera exploratoria y se conserva a todos los genotipados. Las causas del enlace se muestran agregadas; estar fuera de la cohorte maestra no permite inferir un diagnóstico. Los extremos podrían reflejar ancestría, parentesco u otra fuente de estructura.','neutral')
details('La selección local para estructura se distingue del conjunto de asociación. Imputación por media solo en bloques temporales para PCA, centrado y escalado por SNP, acumulación del Gram individuo × individuo y diagonalización. El análisis paralelo permuta individuos independientemente por SNP. Se mantienen cinco PCs en el Modelo B; tres y diez son sensibilidades preespecificadas, no una selección basada en AOO.')
sources('04_preparacion_genetica_definitivo.ipynb §5','data/pca_varianza.csv','data/pca_analisis_paralelo.csv','data/pca_rastreo_resumen.csv')
