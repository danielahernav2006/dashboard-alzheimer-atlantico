import streamlit as st

from components.ui import callout, html, page_header, sources
from utils.data import literatura

page_header("Contexto", "Evolución de los enfoques genéticos y computacionales",
            "Del caso de Auguste Deter a los modelos de aprendizaje automático: la línea de tiempo de la infografía del "
            "proyecto, reconstruida y ampliada con las referencias citadas en los notebooks.",
            icon="book", deco="network")

lit = sorted(literatura(), key=lambda d: d["orden"])
TAGS = ["Alzheimer familiar", "APOE", "Age of Onset", "GWAS", "Machine Learning", "Deep Learning", "Colombia"]

c1, c2 = st.columns([3, 1])
with c1:
    sel = st.pills("Filtrar por tema", TAGS, selection_mode="multi", default=None,
                   help="Muestra los trabajos que tengan al menos uno de los temas seleccionados.")
with c2:
    modo = st.segmented_control("Vista", ["Detallada", "Compacta"], default="Detallada")

items = [d for d in lit if not sel or set(sel) & set(d["tags"]) or d.get("nuestro")]
st.caption(f"{len([d for d in items if not d.get('nuestro')])} trabajos mostrados + este proyecto.")


def tag_badges(tags):
    color = {"APOE": "gold", "Age of Onset": "burg", "GWAS": "petrol", "Colombia": "gold",
             "Machine Learning": "gray", "Deep Learning": "gray", "Alzheimer familiar": "burg"}
    return "".join(f'<span class="badge {color.get(t, "gray")}">{t}</span>' for t in tags)


rows = []
for d in items:
    nota = f'<div class="src">⚠ {d["nota"]}</div>' if d.get("nota") else ""
    if modo == "Compacta":
        body = f'<div class="au">{d["autores"]}</div><div class="ti">{d["trabajo"]}</div>{tag_badges(d["tags"])}'
    else:
        body = f"""
        <div class="au">{d['autores']}</div>
        <div class="ti">{d['trabajo']}</div>
        {tag_badges(d['tags'])}
        <div class="grid2" style="margin-top:10px">
          <div><b>Objetivo</b><br>{d['objetivo']}</div>
          <div><b>Muestra</b><br>{d['muestra']}</div>
          <div><b>Metodología</b><br>{d['metodologia']}</div>
          <div><b>Principal aporte</b><br>{d['aporte']}</div>
        </div>
        <div class="rel"><b>Relación con nuestro proyecto:</b> {d['relacion']}</div>
        {nota}
        <div class="src">Fuente: {d['fuente']}</div>"""
    cls = "it ours" if d.get("nuestro") else "it"
    rows.append(f'<div class="{cls}"><div class="yr">{d["anio"]}</div><div class="dot"></div><div class="box">{body}</div></div>')

html(f'<div class="tl">{"".join(rows)}</div>')

callout("La infografía original incluye 1907, 1991, 1993, 1995, 2009, 2013, 2019, 2021, 2023 y 2025. "
        "Se añadieron Kamboh et al. (2012), Vélez et al. (2016) y Langella et al. (2023) porque el notebook 05 los cita "
        "como respaldo de la AOO como desenlace y de la covariable educación. Otros hitos sugeridos (Naj 2014, "
        "Vélez 2013 pbGWAS) <b>no aparecen en los materiales del proyecto</b> y por eso no se incluyen. "
        "Donde la infografía no reporta tamaño muestral o método, se indica explícitamente.", "neutral")
sources("Infografía línea de tiempo (PDF, 4 páginas)", "04_preparacion_genetica_definitivo.ipynb §7.3.6", "data/literatura.json")
