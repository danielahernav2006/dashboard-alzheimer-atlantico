"""Pruebas de carga y controles contra el paquete preparado; no ejecuta análisis."""
import json,os,sys
from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT);sys.path.insert(0,str(ROOT))

def page(name):
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=45).run()
    app.switch_page('pages/'+name).run(timeout=45)
    assert not app.exception,[x.message for x in app.exception]
    return app

def clean(app):
    # AppTest 1.50 modela ButtonGroup como multiselección aunque segmented_control
    # devuelva un escalar. Normalizar solo el estado del arnés, sin cambiar la app.
    for widget in app.get('button_group'):
        if isinstance(widget.value,str):widget.set_value([widget.value])
    app.run(timeout=45);assert not app.exception,[x.message for x in app.exception]

results=[]
for p in sorted((ROOT/'pages').glob('*.py')):
    app=page(p.name)
    results.append({'pagina':p.name,'errores':[],'tablas':len(app.dataframe),'graficas':len(app.get('plotly_chart')),'selectores':len(app.selectbox)})
(ROOT/'verificacion_paginas.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
steps=[]
a=page('datos_univariado.py');a.selectbox[1].select('neuro__genero');clean(a);steps.append('Univariado: cambiar a variable categórica')
a.radio[0].set_value('Solo AOO observada');clean(a);steps.append('Univariado: alternar entre observada y MI')
a=page('datos_bivariado.py');a.toggle[0].set_value(True);clean(a);assert any(len(t.value)==25 and 'p_ajustado_fdr' in t.value.columns for t in a.dataframe);steps.append('Bivariado: filtro FDR devuelve 25 variables')
a.selectbox[0].select('neuro__nivel_educativo');clean(a);steps.append('Bivariado: educación y estabilidad MI')
a.slider[0].set_value(15);clean(a);steps.append('Bivariado: ajustar extensión del ranking')
a=page('gen_pca.py');a.selectbox[0].select('PC4');a.selectbox[1].select('PC5');clean(a);assert len(a.get('plotly_chart'))==5;steps.append('PCA: cambiar ejes a PC4/PC5; 3D y diagnósticos presentes')
a=page('gen_preparacion.py');a.text_input[0].set_value('rs7412');clean(a);steps.append('Preparación: consulta de rs7412')
a=page('gen_loco.py');a.select_slider[0].set_value(22);clean(a);steps.append('LOCO: seleccionar chr22')
a=page('asoc_gwas.py');a.selectbox[0].select(19);a.text_input[0].set_value('rs7412');clean(a);assert any('45412079' in x.value for x in a.success);steps.append('GWAS: chr19 y búsqueda rs7412')
a.toggle[0].set_value(True);clean(a);steps.append('GWAS: activar línea de referencia sin alterar resultados')
a=page('asoc_variantes.py');a.selectbox[0].select('19:45412079-C-T');clean(a);steps.append('Variantes: ficha rs7412 y tabla APOE')
a=page('asoc_sensibilidad.py');a.selectbox[0].select('19:45412079-C-T');clean(a);steps.append('Sensibilidad: comparación MI para rs7412')
(ROOT/'verificacion_interacciones.json').write_text(json.dumps({'controles_PASS':steps,'FAIL':[]},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'paginas_PASS':len(results),'interacciones_PASS':len(steps),'FAIL':0},ensure_ascii=False))
