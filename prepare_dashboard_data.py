"""Prepara datos agregados de los cuatro notebooks definitivos; no ejecuta análisis.
Uso desde la app: python prepare_dashboard_data.py --project-root ../..
También admite ALZHEIMER_PROJECT_ROOT y descubrimiento de raíz por notebooks.
"""
from __future__ import annotations
import argparse,hashlib,html,json,os,re,shutil
from datetime import datetime
from io import StringIO
from pathlib import Path
import numpy as np
import pandas as pd

def leer_tablas_html_celda(nb: dict, idx: int) -> list[pd.DataFrame]:
    """Devuelve las tablas HTML guardadas en las salidas de una celda."""
    tablas = []
    for out in nb["cells"][idx].get("outputs", []):
        h = "".join(out.get("data", {}).get("text/html", []))
        for tabla in re.findall(r"<table\b.*?</table>", h, flags=re.S):
            filas = re.findall(r"<tr\b[^>]*>(.*?)</tr>", tabla, flags=re.S)
            partes = [[html.unescape(re.sub(r"<[^>]+>", " ", x)).strip()
                       for x in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", f, flags=re.S)]
                      for f in filas]
            partes = [p for p in partes if p]
            if not partes:
                continue
            cab = partes[0]
            cuerpo = partes[1:]
            # pandas incluye una primera columna de índice vacía en la cabecera
            if cuerpo and len(cuerpo[0]) == len(cab) + 1:
                cab = ["_idx"] + cab
            elif cab and cab[0] == "" and cuerpo and len(cuerpo[0]) == len(cab):
                cab = ["_idx"] + cab[1:]
            cuerpo = [c for c in cuerpo if len(c) == len(cab)]
            df = pd.DataFrame(cuerpo, columns=cab)
            if "_idx" in df:
                df = df.drop(columns="_idx")
            tablas.append(_num(df))
    return tablas


def _num(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in out.columns:
        conv = pd.to_numeric(out[c], errors="coerce")
        if conv.notna().sum() == out[c].replace("", np.nan).notna().sum():
            out[c] = conv
    return out


def texto_markdown_celda(nb: dict, idx: int) -> str:
    textos = []
    for out in nb["cells"][idx].get("outputs", []):
        md = out.get("data", {}).get("text/markdown")
        if md:
            textos.append("".join(md))
    return "\n".join(textos)


def buscar_celda(nb: dict, inicio: str) -> int:
    for i, c in enumerate(nb["cells"]):
        if "".join(c["source"]).lstrip().startswith(inicio):
            return i
    raise ValueError(f"No se encontró la celda que empieza por: {inicio!r}")


def sha256_stream(stream):
    h=hashlib.sha256()
    for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

NOTEBOOKS = ['01_preprocesamiento_definitivo.ipynb','02_univariado_definitivo.ipynb',
             '03_bivariado_definitivo.ipynb','04_preparacion_genetica_definitivo.ipynb']

def project_root(value=None):
    if value or os.environ.get('ALZHEIMER_PROJECT_ROOT'):
        p=Path(value or os.environ['ALZHEIMER_PROJECT_ROOT']).expanduser().resolve()
    else:
        p=next((x for x in Path(__file__).resolve().parents if all((x/n).is_file() for n in NOTEBOOKS)),None)
    if p is None or not all((p/n).is_file() for n in NOTEBOOKS):
        raise FileNotFoundError('La raíz debe contener los cuatro notebooks definitivos; usa --project-root.')
    return p

def main(src,dst):
    src=project_root(src);dst=Path(dst).resolve();dst.mkdir(parents=True,exist_ok=True)
    inputs={};controls=[];pending=[];provenance=[];generated=set()
    def record(p):
        p=Path(p)
        if p not in inputs:
            with p.open('rb') as f:inputs[p]=sha256_stream(f)
        return p
    def read(p,**kw):return pd.read_csv(record(p),**kw)
    def js(p):return json.loads(record(p).read_text(encoding='utf8'))
    def save(t,name):
        name=name if name.endswith(('.csv','.csv.gz')) else name+'.csv'
        temporary=dst/(name+'.tmp')
        t.to_csv(temporary,index=False,compression='gzip' if name.endswith('.gz') else None)
        temporary.replace(dst/name)
        generated.add(name);return t
    def writej(t,name):
        temporary=dst/(name+'.tmp')
        temporary.write_text(json.dumps(t,ensure_ascii=False,indent=1,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),encoding='utf8')
        temporary.replace(dst/name);generated.add(name)
    def check(name,ok):
        controls.append({'Control':name,'Estado':'PASS' if bool(ok) else 'FAIL'})
        if not ok:raise ValueError('Discrepancia antes de publicar: '+name)
    def copytable(folder,name,dest=None,optional=False):
        p=folder/(name+'.csv')
        if not p.is_file():
            if optional:pending.append(str(p.relative_to(src)));return None
            raise FileNotFoundError(p)
        t=read(p)
        # Se presentan medianas/rangos p/q por base, nunca promedios como evidencia combinada.
        t=t.drop(columns=[c for c in ['p_MI_medio','q_MI_medio','p_MI_DE','q_MI_DE'] if c in t])
        return save(t,dest or name)
    nbs={n:js(src/n) for n in NOTEBOOKS}
    sources={n:'\n'.join(''.join(c['source']) for c in nb['cells']) for n,nb in nbs.items()}
    def linked(notebook,folder):
        check(notebook+' documenta '+folder,Path(folder).name in sources[notebook])
    for n,f in zip(NOTEBOOKS,['salidas/imputacion_aoo','salidas/univariado_mi','salidas/bivariado_mi_revisado','salidas/genetica_panel_nuevo_MI_integrado']):linked(n,f)
    S=src/'salidas';I=S/'imputacion_aoo';U=S/'univariado_mi';B=S/'bivariado_mi_revisado';G=S/'genetica_panel_nuevo_MI_integrado'
    manifest=js(G/'manifiesto_ejecucion_integrada.json')
    def run(key):
        p=src/Path(manifest[key].replace('\\','/'))
        # Cotejar el manifiesto con la ruta impresa por el notebook ejecutado.
        output='\n'.join((''.join(o.get('text',[])) if isinstance(o.get('text',''),list) else o.get('text','')) for c in nbs[NOTEBOOKS[3]]['cells'] for o in c.get('outputs',[]))
        check(key+' coincide con salida del notebook',str(p.relative_to(src)).replace('/','\\') in output or str(p.relative_to(src)).replace('\\','/') in output)
        return p
    P=run('salida_PCA');R=run('salida_GRM');W=run('salida_GWAS')
    base=pd.read_pickle(record(S/'base_full.pkl'));base_aoo=pd.read_pickle(record(S/'base_aoo.pkl'))
    inv=pd.read_pickle(record(S/'inventario.pkl'));pre=pd.read_pickle(record(S/'objetos_preprocesamiento.pkl'))
    mi=pd.read_pickle(record(I/'base_full_aoo_mice_long.pkl'));meta_mi=js(I/'reproducibilidad_imputacion_aoo.json')
    check('Cohorte 391 y AOO original 370 + 21',len(base)==391 and base.aoo.notna().sum()==370 and base.aoo.isna().sum()==21 and len(base_aoo)==370)
    check('M1b seleccionada',meta_mi['modelo_seleccionado']=='M1b_con_edad_brecha')
    check('Veinte imputaciones',mi.imputacion.nunique()==20)
    original=base.set_index('id').aoo
    for im,d in mi.groupby('imputacion'):
        ref=d.id.map(original);observ=ref.notna()
        check(f'MI {im}: mismos IDs, observados intactos y flag',len(d)==391 and d.id.is_unique and set(d.id)==set(base.id) and d.aoo_analisis.notna().all() and np.array_equal(d.loc[observ,'aoo_analisis'],ref[observ]) and np.array_equal(d.flag_aoo_imputado,ref.isna().astype(int)))
    meta=inv[[c for c in ['columna','etiqueta','original','familia','fuente','tipo_analitico','riesgo_leakage_aoo','descripcion','etiquetas_codigos_dict'] if c in inv]].copy()
    meta['etiquetas_codigos_dict']=meta.etiquetas_codigos_dict.apply(lambda x:{str(k):str(v) for k,v in x.items()} if isinstance(x,dict) else {})
    if not meta.columna.eq('aoo').any():
        meta=pd.concat([meta,pd.DataFrame([{'columna':'aoo','etiqueta':'Edad de inicio (AOO)','original':'AOO','familia':'Desenlace','fuente':'AOO revisada','tipo_analitico':'cuantitativa continua','riesgo_leakage_aoo':'desenlace','descripcion':'Edad de inicio observada; MI se presenta por separado.','etiquetas_codigos_dict':{}}])],ignore_index=True)
    writej(meta.to_dict('records'),'variables_meta.json')
    # Una variable a la vez: histogramas, frecuencias y descriptivos; nunca filas clínicas.
    stats_rows=[];hist_rows=[];cat_rows=[];mi_hist=[]
    def stats_serie(v,n):
        v=pd.to_numeric(v,errors='coerce').dropna();q1,q3=v.quantile([.25,.75]);iqr=q3-q1
        return {'n':len(v),'faltantes':n-len(v),'media':v.mean(),'mediana':v.median(),'DE':v.std(),'varianza':v.var(),'Q1':q1,'Q3':q3,'min':v.min(),'max':v.max(),'RIQ':iqr,'skewness':v.skew(),'kurtosis':v.kurt(),'n_extremos':int(((v<q1-1.5*iqr)|(v>q3+1.5*iqr)).sum())}
    for _,r in meta.iterrows():
        c=r.columna
        if c not in base:continue
        v=base[c];numeric=r.tipo_analitico in ['cuantitativa continua','cuantitativa discreta'] or c=='aoo'
        if numeric:
            x=pd.to_numeric(v,errors='coerce').dropna()
            if not len(x):continue
            stats_rows.append({'columna':c,**stats_serie(x,len(base))})
            edges=np.histogram_bin_edges(x,bins=27 if c=='aoo' else 30)
            counts,_=np.histogram(x,bins=edges)
            hist_rows.extend({'columna':c,'izq':a,'der':b,'n':int(z)} for a,b,z in zip(edges[:-1],edges[1:],counts))
            if c=='aoo':
                edges=np.linspace(min(mi.aoo_analisis.min(),x.min()),max(mi.aoo_analisis.max(),x.max()),29)
                for im,d in [(0,base_aoo.rename(columns={'aoo':'aoo_analisis'}))]+list(mi.groupby('imputacion')):
                    cnt,_=np.histogram(d.aoo_analisis,bins=edges)
                    mi_hist.extend({'imputacion':im,'izq':a,'der':b,'densidad':z/(len(d)*(b-a))} for a,b,z in zip(edges[:-1],edges[1:],cnt))
        elif v.nunique(dropna=True)<=30 and not str(r.tipo_analitico).startswith('texto libre'):
            mapa=r.etiquetas_codigos_dict
            def label(v):
                if pd.isna(v):return 'Faltante'
                key=str(int(v)) if isinstance(v,(float,int,np.number)) and float(v).is_integer() else str(v)
                return mapa.get(key,key)
            counts=v.map(label).value_counts(dropna=False)
            cat_rows.extend({'columna':c,'categoria':str(a),'n':int(z),'pct_total':100*z/len(base)} for a,z in counts.items())
    save(pd.DataFrame(stats_rows),'uni_descriptivos');save(pd.DataFrame(hist_rows),'uni_histogramas');save(pd.DataFrame(cat_rows),'uni_categorias');save(pd.DataFrame(mi_hist),'aoo_distribuciones_MI')
    for name in ['comparacion_aoo_observado_vs_mi','descriptivos_aoo_por_imputacion','resumen_descriptivos_aoo_mi','media_aoo_rubin','outliers_aoo_por_imputacion','resumen_missingness_aoo','rutas_analiticas','resumen_discrepancia_missforest']:
        copytable(U,name,'u_'+name,optional=name=='resumen_discrepancia_missforest')
    for name in ['distribucion_aoo_observado_vs_mi','boxplots_aoo_por_imputacion']:
        f=U/(name+'.png')
        if f.exists():shutil.copyfile(record(f),dst/f.name);generated.add(f.name)
        else:pending.append(str(f.relative_to(src)))
    # Auditorías agregadas del preprocesamiento.
    for key,dest in [('resumen_fuentes','q_resumen_fuentes'),('auditoria_ids','q_auditoria_ids'),('resumen_consistencia','q_consistencia_aoo'),('tabla_reduccion_neuro','q_reduccion_neuro'),('revision_pendiente_agrupada','q_revision_pendiente')]:
        t=pre[key].copy()
        # Eliminar listas de identificadores, si las incluye la auditoría de fuente.
        t=t.drop(columns=[c for c in t if str(c).lower() in ['id','ids','ids_solo_fuente','ids_solo_hxgen'] or 'lista_id' in str(c).lower()],errors='ignore')
        save(t,dest)
    save(pre['auditoria_aoo'].estado_aoo.value_counts().rename_axis('estado').reset_index(name='n'),'q_estado_aoo')
    for key,col,dest in [('auditoria_codigos_especiales','decision','q_codigos_especiales'),('auditoria_modificaciones','tipo_hallazgo','q_modificaciones'),('auditoria_limpieza','tipo_hallazgo','q_hallazgos_limpieza')]:
        group=[col] if key=='auditoria_codigos_especiales' else ['fuente',col]
        save(pre[key].groupby(group).size().rename('n').reset_index(),dest)
    fuentes=read(S/'auditoria_fuentes_paciente.csv');save(fuentes.drop(columns='id').astype(bool).value_counts().rename('n').reset_index(),'q_cobertura_fuentes')
    miss=inv[['columna','etiqueta','familia','fuente','tipo_analitico','n_valido','n_faltante']].copy();miss['pct_faltante']=100*miss.n_faltante/len(base);save(miss,'q_missing_variables')
    # Bivariado definitivo, con precisión completa y misma familia de pruebas.
    obs=read(B/'resultados_bivariados_observados.csv');est=read(B/'resumen_estabilidad_bivariada_mi.csv')
    check('Bivariado: 142 / 90 / 25',len(obs)==142 and obs.evaluable.sum()==90 and obs.p_ajustado_fdr.lt(.05).sum()==25)
    consistent=est.loc[est.FDR_observado.lt(.05),'n_imputaciones_FDR_significativa'].eq(20).sum()
    check('23 observadas FDR recurrentes 20/20',consistent==23)
    for pattern in ['nivel_educativo','fvfs']:
        t=est[est.columna.eq('neuro__'+pattern)];check(pattern+' signo20 FDR19',len(t)==1 and t.n_mismo_signo.iloc[0]==20 and t.n_imputaciones_FDR_significativa.iloc[0]==19)
    for name in ['resultados_bivariados_observados','resumen_estabilidad_bivariada_mi','fdr_por_imputacion','resumen_global_bivariado_mi','dunn_observado','resumen_dunn_mi','motivos_no_evaluacion','senales_emergentes_mi','hipertension_contraste_codigos','auditoria_predictores_m1b','auditoria_participacion_senales_m1b','concordancia_edades_fuentes']:
        copytable(B,name,'b_'+name)
    # Mantener contrato del explorador de covariables; enriquecer con estadísticas definitivas.
    ev=read(W/'evaluacion_covariables.csv')
    mapping={'descripcion':'variable','prueba_EDA':'prueba','n_EDA':'n','Estadístico':'estadistico','efecto_EDA':'medida_efecto','tipo_efecto_EDA':'medida_efecto_nombre','IC 95% inf.':'ic95_efecto_inf','IC 95% sup.':'ic95_efecto_sup','direccion_EDA':'direccion','Medianas por grupo':'medianas_por_grupo','tamanos_grupo':'tamanos_grupo','p_EDA':'p_valor','FDR_EDA':'p_ajustado_fdr'}
    indexed=obs.set_index('columna')
    for target,column in mapping.items():ev[target]=ev.variable.map(indexed[column])
    ev['evidencia_estadistica_EDA']=np.select([ev.FDR_EDA.lt(.05),ev.p_EDA.lt(.05),ev.p_EDA.notna()],['Evidencia estadística tras corrección FDR','Exploratoria nominal','Sin evidencia estadística detectable'],default='No evaluable')
    ev['p_EDA_mostrado']=ev.p_EDA.map(lambda x:f'{x:.4g}' if pd.notna(x) else '—');ev['FDR_EDA_mostrado']=ev.FDR_EDA.map(lambda x:f'{x:.4g}' if pd.notna(x) else '—')
    save(ev,'eda_bivariado')
    # Paneles: auditoría existente, no reprocesamiento del archivo genético.
    for name in ['comparacion_paneles_estructura','qc_comparado','qc_informado_y_fuentes','denominadores_integrados','comparacion_clinica_extremos']:
        copytable(G,name,'g_'+name)
    snp=read(G/'qc_snp_nuevo_genotipados.csv');snp['crom']=snp.crom.astype(int)
    check('Panel nuevo 18391 SNPs',len(snp)==18391)
    save(snp.groupby('crom').agg(n_snps=('variante','size'),freq_alt_media=('frecuencia_ALT','mean'),missing_media=('faltantes','mean')).reset_index(),'g_snps_por_cromosoma')
    panels=read(G/'comparacion_paneles_estructura.csv');new=panels.loc[panels.panel.eq('nuevo')].iloc[0]
    den=read(G/'denominadores_integrados.csv').iloc[0]
    trace=read(G/'trazabilidad_todas_muestras.csv',dtype={'GENCELLID':str});gr_ids=read(R/'grm_ids.csv',dtype=str).GENCELLID
    check('Muestra genética alineada',trace.GENCELLID.tolist()==gr_ids.tolist())
    save(pd.DataFrame({'Indicador':['Muestras genéticas','Enlaces genético-clínicos','Enlaces con AOO revisada','Enlaces sin AOO','IDs clínicos sin genotipo'],'n':[len(trace),den.casos_cohorte,den.casos_aoo_observada,den.casos_cohorte-den.casos_aoo_observada,len(base)-den.casos_cohorte]}),'g_resumen_cruce')
    save(pd.DataFrame({'Indicador':['Variantes iniciales','SNPs conservados','SNPs autosómicos','SNPs no autosómicos','Inserciones excluidas','Deleciones excluidas'],'n':[new.variantes_iniciales,new.snp_simples,new.snp_autosomicos,new.no_autosomicos,new.inserciones,new.deleciones]}),'g_resumen_variantes')
    missing_pct=float(100*snp.faltantes.sum()/(len(trace)*len(snp)))
    save(pd.DataFrame([{'Muestras':len(trace),'SNPs':len(snp),'Faltantes (%)':missing_pct}]),'g_resumen_calidad')
    # PCA: puntos sin IDs ni atributos clínicos; permutación de filas para no exponer el orden fuente.
    pcs=read(P/'pca_individuos.csv',dtype={'Patient ID':str});pc_cols=[f'PC{i}' for i in range(1,11)]
    check('PCA corresponde a todos los genotipados',pcs['Patient ID'].tolist()==gr_ids.tolist())
    z=(pcs[pc_cols]-pcs[pc_cols].mean())/pcs[pc_cols].std(ddof=0);flags=z.abs().ge(3)
    public=pcs[pc_cols].copy();public['n_PCs_extremos']=flags.sum(axis=1);public['extremo_PC1_PC3']=flags.iloc[:,:3].any(axis=1);public['dist_std_PC1_PC3']=np.linalg.norm(z.iloc[:,:3],axis=1)
    save(public.sample(frac=1,random_state=42).reset_index(drop=True),'pca_individuos')
    copytable(P,'pca_varianza_explicada','pca_varianza');copytable(P,'evaluacion_estadistica_pcs','pca_analisis_paralelo')
    ext=read(G/'rastreo_clinico_extremos.csv');save(ext.groupby(['caso_cohorte','diagnostico_enlace'],dropna=False).size().reset_index(name='n'),'pca_rastreo_resumen')
    selection=read(G/'seleccion_marcadores_estructura.csv');n_structure=int(selection.iloc[:,-1].sum()) if selection.iloc[:,-1].dtype==bool else int(manifest['snps_estructura'])
    check('18254 marcadores de estructura',n_structure==18254)
    # Calidad individual resumida por grupos de extremos, sin exportar filas identificables.
    doses=np.load(record(G/'dosis_snps.npy'),mmap_mode='r');mask=selection.usar_estructura.to_numpy(bool)
    check('Dosis, PCs y selección alineados',doses.shape==(len(pcs),len(selection)) and selection.variante.tolist()==snp.variante.tolist())
    na=np.zeros(len(pcs),dtype=int);het=np.zeros(len(pcs),dtype=int)
    js_structure=np.flatnonzero(mask)
    for start in range(0,len(js_structure),2048):
        block=doses[:,js_structure[start:start+2048]];na+=np.isnan(block).sum(axis=1);het+=(block==1).sum(axis=1)
    quality=pd.DataFrame({'extremo_PC1_PC3':flags.iloc[:,:3].any(axis=1),'missing_pct':100*na/len(js_structure),'heterocigosidad_pct':100*het/(len(js_structure)-na)})
    qrows=[];qhist=[]
    for flag,g in quality.groupby('extremo_PC1_PC3'):
        for col in ['missing_pct','heterocigosidad_pct']:
            v=g[col];qrows.append({'extremo_PC1_PC3':flag,'indicador':col,'n':len(v),'media':v.mean(),'mediana':v.median(),'DE':v.std(),'min':v.min(),'max':v.max()})
            edges=np.histogram_bin_edges(quality[col],bins=30);counts,_=np.histogram(v,bins=edges)
            qhist.extend({'extremo_PC1_PC3':flag,'indicador':col,'izq':a,'der':b,'n':z} for a,b,z in zip(edges[:-1],edges[1:],counts))
    save(pd.DataFrame(qrows),'pca_calidad_extremos');save(pd.DataFrame(qhist),'g_calidad_histogramas')
    # GRM: distribuciones agregadas y heatmap por bloques, sin matriz ni IDs individuales.
    grm=np.load(record(R/'grm_todos.npy'),mmap_mode='r');off=grm[np.triu_indices(len(grm),1)]
    cnt,edges=np.histogram(off,bins=120);save(pd.DataFrame({'izq':edges[:-1],'der':edges[1:],'n':cnt}),'grm_hist_offdiag')
    cnt,edges=np.histogram(np.diag(grm),bins=45);save(pd.DataFrame({'izq':edges[:-1],'der':edges[1:],'n':cnt}),'grm_hist_diagonal')
    save(pd.DataFrame({'umbral':[.1,.2,.4,.8],'pares':[(off>x).sum() for x in [.1,.2,.4,.8]]}),'grm_umbrales');copytable(R,'resumen_grm','grm_resumen')
    aoogr=np.load(record(R/'grm_aoo.npy'),mmap_mode='r');blocks=np.array_split(np.arange(len(aoogr)),25);heat=[]
    for i,a in enumerate(blocks):
        for j,b in enumerate(blocks):
            sub=np.array(aoogr[np.ix_(a,b)],dtype=float)
            if i==j:np.fill_diagonal(sub,np.nan)
            heat.append({'bloque_1':i+1,'bloque_2':j+1,'GRM_media':float(np.nanmean(sub))})
    save(pd.DataFrame(heat),'grm_heatmap_bloques')
    con=read(G/'pares_grm_alta_nuevos.csv');safe=con[[c for c in ['GRM','SNPs_comparables','concordancia_pct','pct_IBS2','pct_IBS1','pct_IBS0','Interpretacion_exploratoria'] if c in con]].copy();safe.insert(0,'Par',np.arange(1,len(safe)+1));save(safe,'grm_concordancia_extremos')
    for name in ['resumen_grm_loco','modelo_nulo_lmm','nulos_globales_pcs','perfil_reml','resumen_gwas','resumen_muestras_modelos','comparacion_sensibilidad','comparacion_AB_muestra_comun','vif_modelo_B','gwas_top_variantes']:copytable(W,name,'m_'+name)
    # Tablas guardadas, identificadas por el código y no por un índice frágil de celda.
    nb=nbs[NOTEBOOKS[3]];extracted=set()
    for i,c in enumerate(nb['cells']):
        s=''.join(c['source'])
        for needle,name in [('modelos_nulos_loco=pd.DataFrame','m_nulos_loco_diagnostico'),('filas_diagnostico7 = []','m_auditoria_cromosomas')]:
            if needle in s:
                tables=leer_tablas_html_celda(nb,i)
                if tables:save(tables[0],name);extracted.add(name)
        if c['cell_type']=='markdown':
            for marker,name,ti in [('7.3.10','cov_educacion_codigos',1),('7.3.11','cov_educacion_agrupada',0),('7.3.14','cov_educacion_por_sexo',0)]:
                if marker in s.split('\n')[0]:
                    tables=leer_tablas_html_celda(nb,i+1)
                    if len(tables)>ti:save(tables[ti],name);extracted.add(name)
    check('Diagnósticos y educación recuperados',len(extracted)==5)
    writej({},'textos_notebook.json')
    # Resultados completos por variante y modelos; no genotipos individuales.
    gw=read(W/'gwas_principal.csv');rg=read(W/'resumen_gwas.csv').iloc[0]
    for key,file in {'B3':'gwas_sensibilidad_3pcs','B10':'gwas_sensibilidad_10pcs','A':'gwas_referencia_A_comparable'}.items():
        t=read(W/(file+'.csv'))[['variante','beta','se','p','p_fdr']].rename(columns={c:f'{c}_{key}' for c in ['beta','se','p','p_fdr']})
        check('Mismo universo '+key,set(t.variante)==set(gw.variante));gw=gw.merge(t,on='variante',validate='one_to_one')
    gw=gw.merge(snp[['variante','n_0','n_1','n_2','faltantes','frecuencia_ALT']].rename(columns={'n_0':'n0','n_1':'n1','n_2':'n2','frecuencia_ALT':'freq_alt_755'}),on='variante',validate='one_to_one')
    gw['missing_pct_755']=100*gw.faltantes/len(trace);gw['rank_p']=gw.p.rank(method='min').astype(int)
    gw['rsid_documentado']=gw.variante.map({'19:45411941-T-C':'rs429358','19:45412079-C-T':'rs7412'}).fillna('')
    save(gw,'gwas_resultados.csv.gz');copytable(G,'apoe_gwas_observado','apoe_individual')
    apoe=read(G/'apoe_combinaciones_no_faseadas.csv');save(apoe.groupby(['estado','configuraciones_posibles'],dropna=False).size().reset_index(name='n'),'apoe_combinaciones_resumen')
    mi_gwas=copytable(G,'resumen_MI_por_imputacion','gwas_MI_resumen');copytable(G,'comparacion_observado_MI','gwas_MI_estabilidad')
    add=read(G/'auditoria_21_aoo_imputados.csv');save(add.groupby(['elegible_B_MI','motivo'],dropna=False).size().reset_index(name='n'),'gwas_MI_elegibilidad')
    check('Modelo B: 334, 18391, cero corregidas',rg.n_pacientes==334 and len(gw)==18391 and gw.p_fdr.lt(.05).sum()==0 and gw.p_bonferroni.lt(.05).sum()==0)
    check('MI:18 adicionales, 352 por base,20 corridas,cero corregidas',add.elegible_B_MI.sum()==18 and len(mi_gwas)==20 and mi_gwas.n.eq(352).all() and mi_gwas.FDR.eq(0).all() and mi_gwas.Bonferroni.eq(0).all())
    var=read(P/'pca_varianza_explicada.csv')
    k={'cohorte_clinica':len(base),'pacientes_aoo':int(base.aoo.notna().sum()),'aoo_faltante':int(base.aoo.isna().sum()),'n_imputaciones':mi.imputacion.nunique(),'aoo_media':base.aoo.mean(),'aoo_mediana':base.aoo.median(),'aoo_sd':base.aoo.std(),'aoo_min':base.aoo.min(),'aoo_max':base.aoo.max(),'muestras_geneticas':len(trace),'enlaces_genetico_clinicos':int(den.casos_cohorte),'enlaces_con_aoo':int(den.casos_aoo_observada),'enlaces_sin_aoo':int(den.casos_cohorte-den.casos_aoo_observada),'clinicos_sin_genotipo':len(base)-int(den.casos_cohorte),'n_modelo_B':int(rg.n_pacientes),'n_modelo_MI':int(mi_gwas.n.iloc[0]),'adicionales_MI':int(add.elegible_B_MI.sum()),'variantes_iniciales':int(new.variantes_iniciales),'snps_simples':int(new.snp_simples),'indels':int(new.indels),'inserciones':int(new.inserciones),'deleciones':int(new.deleciones),'snps_no_autosomicos':int(new.no_autosomicos),'snps_autosomicos':len(snp),'snps_probados':len(gw),'marcadores_estructura':n_structure,'cromosomas':snp.crom.nunique(),'lambda_gc':rg.lambda_GC,'umbral_bonferroni':rg.umbral_bonferroni,'n_bonferroni':int(rg.n_bonferroni),'n_fdr':int(rg.n_fdr),'snp_menor_p':rg.snp_menor_p,'beta_menor_p':rg.beta,'p_min':gw.p.min(),'fdr_min':gw.p_fdr.min(),'n_pcs_principal':int(rg.n_pcs),'h2_loco_min_B':rg.h2_loco_min,'h2_loco_max_B':rg.h2_loco_max,'pca_var_pc1':var.iloc[0,1],'pca_var_acum_10':var.iloc[-1,2],'missing_global_pct':missing_pct,'fuente_gwas':str(W.relative_to(src)).replace('\\','/'),'fuente_pca':str(P.relative_to(src)).replace('\\','/'),'fuente_grm':str(R.relative_to(src)).replace('\\','/'),'panel_actual':'functional-variants.txt','biv_variables':len(obs),'biv_evaluables':int(obs.evaluable.sum()),'biv_FDR':int(obs.p_ajustado_fdr.lt(.05).sum()),'biv_recurrentes_20':int(consistent)}
    writej(k,'kpis.json')
    flow=pd.DataFrame([('Cohorte clínica',len(base)),('Con AOO observada',k['pacientes_aoo']),('Casos enlazados con genotipo',k['enlaces_genetico_clinicos']),('Genotipo + AOO observada',k['enlaces_con_aoo']),('Modelo B observado',k['n_modelo_B'])],columns=['etapa','n']);save(flow,'cohort_flow')
    for pages,folder,nbname in [('Inicio; Cohorte; Calidad',S,NOTEBOOKS[0]),('Univariado',U,NOTEBOOKS[1]),('Bivariado; Covariables',B,NOTEBOOKS[2]),('Genética; PCA; GRM; LOCO; GWAS; Sensibilidad; APOE',G,NOTEBOOKS[3])]:provenance.append({'Páginas':pages,'Exportaciones':str(folder.relative_to(src)).replace('\\','/'),'Notebook definitivo':nbname})
    save(pd.DataFrame(provenance),'trazabilidad_paginas')
    # El paquete público solo conserva archivos generados y literatura; retirar derivados antiguos identificados.
    for old in dst.iterdir():
        if old.is_file() and old.name not in generated and old.name!='literatura.json':old.unlink()
    for f in dst.glob('*.csv*'):
        cols=pd.read_csv(f,nrows=0).columns
        check('Sin columnas de identidad: '+f.name,not any(re.search(r'(^id$|GENCELLID|Patient ID|ID_1|ID_2|fila_G|mes_y_anio)',c,re.I) for c in cols))
    for p,h in inputs.items():
        with p.open('rb') as f:check('Entrada preservada '+str(p.relative_to(src)),sha256_stream(f)==h)
    save(pd.DataFrame(controls),'auditoria_dashboard')
    writej({'notebooks':NOTEBOOKS,'corridas':{key:str(runp.relative_to(src)).replace('\\','/') for key,runp in [('PCA',P),('GRM',R),('GWAS',W)]},'entradas_sha256':{str(p.relative_to(src)).replace('\\','/'):h for p,h in inputs.items()},'pendientes':pending,'controles_PASS':len(controls),'privacidad':'Tablas agregadas; PCs anónimos sin datos clínicos ni orden fuente; no se distribuyen dosis ni IDs.','recalculo_analisis':False,'fecha':datetime.now().isoformat()},'fuentes_dashboard.json')
    print(json.dumps({'data':str(dst),'archivos':len(generated),'PASS':len(controls),'pendientes':pending,'corrida_principal':str(W.relative_to(src))},ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-root','--source',dest='source',help='Raíz con los cuatro notebooks definitivos')
    ap.add_argument('--out',default=str(Path(__file__).resolve().parent/'data'))
    args=ap.parse_args();main(args.source,Path(args.out))
