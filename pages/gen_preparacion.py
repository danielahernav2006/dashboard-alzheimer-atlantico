import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from components.ui import STRETCH,callout,details,html,kpis,page_header,plot,section,sources
from utils.data import csv,kpis as load_kpis,gwas,fmt_int
from utils.theme import BURGUNDY,PETROL,GRAY
k=load_kpis();g=gwas()
page_header('Genética','Preparación genética y codificación 0/1/2','Panel actual functional-variants.txt; comparación histórica y distinción entre asociación y estructura.',icon='dna',deco='chromosome')
kpis([{'label':'Genotipados','value':fmt_int(k['muestras_geneticas']),'icon':'users','kind':'genetic'},{'label':'Variantes iniciales','value':fmt_int(k['variantes_iniciales']),'icon':'layers','kind':'genetic'},{'label':'SNPs de asociación','value':fmt_int(k['snps_probados']),'icon':'dna','kind':'genetic'},{'label':'Marcadores de estructura','value':fmt_int(k['marcadores_estructura']),'icon':'network','kind':'genetic'},{'label':'Faltantes globales','value':f'{k["missing_global_pct"]:.5f} %','icon':'search'}])
section('Paneles comparados','Actual e histórico')
st.dataframe(csv('g_comparacion_paneles_estructura.csv'),hide_index=True,**STRETCH)
callout('El profesor informó <b>MAF > 0,01</b> para el panel nuevo. GCR, HWE y poda del proveedor están pendientes de corroboración documental. El panel histórico exosoms-qc-full.txt analizó 128.757 SNPs autosómicos con MAF mínima documentada de 0,05. La menor cobertura del panel nuevo no puede atribuirse íntegramente al cambio de MAF.','info')
st.dataframe(csv('g_qc_informado_y_fuentes.csv'),hide_index=True,**STRETCH)
section('Conversión y selección','Dosis respecto a ALT')
html('<div class="pipe"><div class="st g">REF / REF → 0</div><div class="ar">→</div><div class="st g">REF / ALT → 1</div><div class="ar">→</div><div class="st f">ALT / ALT → 2</div></div>')
callout('«?» es una llamada de alelo indeterminada. Si impide deducir la dosis exacta, se registra como NaN. ALT no implica riesgo ni protección. Se conservan SNPs simples bialélicos autosómicos sin reaplicar filtros de MAF, GCR o HWE.','neutral')
st.dataframe(csv('g_resumen_variantes.csv'),hide_index=True,**STRETCH)
callout('La poda local (ventana 50, paso 5, r² de dosis > 0,5) se aplica únicamente a los marcadores usados para PCA y GRM. No es CHM ni un filtro del proveedor; no reduce el universo de SNPs probado en el GWAS.','key')
st.dataframe(csv('g_qc_comparado.csv'),hide_index=True,**STRETCH)
section('Descriptivos del panel','Interactivo')
t1,t2,t3=st.tabs(['SNPs por cromosoma','Frecuencia ALT y MAC','Consultar SNP'])
with t1:plot(px.bar(csv('g_snps_por_cromosoma.csv'),x='crom',y='n_snps',color_discrete_sequence=[PETROL]))
with t2:
    sample=st.radio('Muestra',['Todos los genotipados','Modelo B observado'],horizontal=True);col='freq_alt_755' if sample.startswith('Todos') else 'frecuencia_ALT'
    plot(px.histogram(g,x=col,nbins=50,color_discrete_sequence=[BURGUNDY]));st.caption('El filtro informado por el proveedor y las frecuencias de la submuestra del modelo tienen denominadores distintos. ALT no siempre es el alelo menor.')
    plot(px.histogram(g,x='MAC',nbins=50,color_discrete_sequence=[PETROL],title='Conteo del alelo menor en el Modelo B'))
with t3:
    q=st.text_input('Variante o rsID',value='rs429358');t=g[g.variante.eq(q)|g.rsid_documentado.eq(q)]
    if t.empty:st.info('No se encontró el marcador.')
    else:
        r=t.iloc[0];plot(go.Figure(go.Bar(x=['0','1','2','NaN'],y=[r.n0,r.n1,r.n2,k['muestras_geneticas']-r.n0-r.n1-r.n2])))
        st.dataframe(t[['variante','rsid_documentado','ref','alt','freq_alt_755','frecuencia_ALT','MAF','MAC','n_valido','n_modelo']],hide_index=True,**STRETCH)
details('El ensamblaje es compatible con GRCh37 según la auditoría de coordenadas y alelos, pero falta certificación documental. Ambos marcadores APOE están presentes; sus asociaciones individuales se muestran en Variantes priorizadas. No se publica la matriz de dosis ni identificadores de pacientes.')
sources('04_preparacion_genetica_definitivo.ipynb §1–6','data/g_comparacion_paneles_estructura.csv','data/g_qc_comparado.csv')

section("Missingness y heterocigosidad", "Conjunto de estructura · resúmenes por grupo")
h=csv("g_calidad_histogramas.csv")
for metric in h.indicador.unique():
    t=h[h.indicador.eq(metric)];fig=go.Figure()
    for flag,g in t.groupby("extremo_PC1_PC3"):
        fig.add_trace(go.Bar(x=(g.izq+g.der)/2,y=g.n,width=g.der-g.izq,name="Extremos PC1–PC3" if flag else "Resto",opacity=.6))
    fig.update_layout(title=metric,barmode="overlay",xaxis_title="Porcentaje",yaxis_title="Individuos");plot(fig)
