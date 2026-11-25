# Dashboard · Alzheimer y edad de inicio en el Atlántico

Seminario Investigativo · Universidad del Norte  
Daniela Hernández · Alejandra Meneses · Mariangel Yepes

Aplicación existente de Streamlit + Plotly: se conservan sus 18 páginas, navegación por secciones, componentes, tema y literatura. El resultado principal es el **Modelo B con AOO observada del panel nuevo**. Asociación no implica causalidad.

## Regenerar datos y arrancar

Desde la raíz del proyecto:

```bash
cd dashboard_alzheimer/dashboard_alzheimer
python -m pip install -r requirements.txt
python prepare_dashboard_data.py --project-root ../..
python -m streamlit run app.py --server.port 8502
```

La instalación solo es necesaria en un entorno que aún no tenga las dependencias. Se recomienda un entorno dedicado con Python 3.10 o superior. No es necesario instalar paquetes para regenerar desde un entorno ya compatible.

La preparación admite una raíz explícita, la variable de entorno `ALZHEIMER_PROJECT_ROOT` o el descubrimiento automático de los cuatro notebooks definitivos en los directorios superiores. No utiliza rutas de Windows escritas a mano ni la carpeta histórica `dashboard/`.

```bash
python prepare_dashboard_data.py                 # descubre la raíz desde la ubicación del script
python prepare_dashboard_data.py --project-root /ruta/al/proyecto
```

La app se abre en http://localhost:8502. Su navegación se define en `app.py`. Las versiones de dependencias se indican en `requirements.txt`. Las pruebas de esta actualización usaron Streamlit 1.50.0 y Plotly 6.6.0 con los paquetes ya instalados; no se instalaron ni entrenaron modelos.

## Fuentes definitivas y corridas

Se leen completos los cuatro notebooks definitivos para comprobar sus referencias. Las rutas de salida se conservan aunque haya cambiado el nombre del notebook.

| Etapa | Notebook de referencia | Exportaciones |
|---|---|---|
| Preprocesamiento y M1b | `01_preprocesamiento_definitivo.ipynb` | `salidas/base_full.pkl`, `base_aoo.pkl`, `inventario.pkl`, `objetos_preprocesamiento.pkl`; `salidas/imputacion_aoo/` |
| Univariado | `02_univariado_definitivo.ipynb` | `salidas/univariado_mi/` |
| Bivariado | `03_bivariado_definitivo.ipynb` | `salidas/bivariado_mi_revisado/` |
| Genética, PCA, GRM, LOCO, GWAS y MI | `04_preparacion_genetica_definitivo.ipynb` | `salidas/genetica_panel_nuevo_MI_integrado/` |

El manifiesto `manifiesto_ejecucion_integrada.json` fija la corrida y la preparación comprueba que las rutas también figuren en las salidas guardadas del notebook. Corridas verificadas en esta actualización:

- PCA: `pca/ejecucion_p8hyn8hn`.
- GRM: `grm/ejecucion_juoce88v`.
- GWAS observado y sensibilidades por PCs: `gwas/ejecucion_9rw2nf6n`.
- MI genética: resumen de las veinte corridas en `resumen_MI_por_imputacion.csv` y comparación descriptiva en `comparacion_observado_MI.csv`.

Todas estas subcarpetas pertenecen a `salidas/genetica_panel_nuevo_MI_integrado/`. No se elige la carpeta más reciente por fecha ni se mezclan corridas.

## Página → datos preparados → notebook

| Página | Archivos preparados en `data/` | Notebook |
|---|---|---|
| Portada y Problema | `kpis.json`, `uni_descriptivos.csv`, `uni_histogramas.csv` | 01 y 04 definitivos |
| Cohorte | `cohort_flow.csv`, `g_resumen_cruce.csv`, `u_rutas_analiticas.csv`, `gwas_MI_elegibilidad.csv` | 01 y 04 |
| Calidad | `q_*.csv`, `u_resumen_missingness_aoo.csv` | 01 y 02 |
| Univariado | `uni_*.csv`, `u_*.csv`, `aoo_distribuciones_MI.csv`, dos PNG de AOO | 02 |
| Bivariado | `b_resultados_bivariados_observados.csv`, `b_resumen_estabilidad_bivariada_mi.csv`, `b_fdr_por_imputacion.csv`, `b_dunn_observado.csv`, `b_resumen_dunn_mi.csv`, auditorías `b_*` | 03 |
| Preparación genética | `g_comparacion_paneles_estructura.csv`, `g_qc_*.csv`, `g_snps_por_cromosoma.csv`, `g_calidad_histogramas.csv` | 04 §§1–4 |
| PCA | `pca_individuos.csv` anónimo, `pca_varianza.csv`, `pca_analisis_paralelo.csv`, `pca_rastreo_resumen.csv`, `pca_calidad_extremos.csv`, `g_comparacion_clinica_extremos.csv` | 04 §5 |
| GRM | `grm_resumen.csv`, `grm_hist_*.csv`, `grm_heatmap_bloques.csv`, `grm_concordancia_extremos.csv` | 04 §6 |
| LOCO | `m_resumen_grm_loco.csv`, `m_nulos_loco_diagnostico.csv`, `m_auditoria_cromosomas.csv`, `m_nulos_globales_pcs.csv`, `m_perfil_reml.csv` | 04 §7.6 |
| Covariables y LMM | `eda_bivariado.csv`, `cov_educacion_*.csv`, `m_vif_modelo_B.csv`, `m_modelo_nulo_lmm.csv`, `m_resumen_muestras_modelos.csv` | 03 y 04 |
| GWAS | `gwas_resultados.csv.gz`, `m_resumen_gwas.csv` | 04 §§7.7–7.12 |
| Sensibilidad | `m_comparacion_sensibilidad.csv`, `m_comparacion_AB_muestra_comun.csv`, `gwas_MI_resumen.csv`, `gwas_MI_estabilidad.csv` | 04 §7.13 y MI |
| Variantes y APOE | `gwas_resultados.csv.gz`, `apoe_individual.csv`, `apoe_combinaciones_resumen.csv` | 04 |
| Cierre | `kpis.json`, `trazabilidad_paginas.csv`, `auditoria_dashboard.csv`, `fuentes_dashboard.json` | 01–04 |

Literatura conserva su archivo `literatura.json` y las referencias/contexto válidos existentes. `fuentes_dashboard.json` registra entradas con SHA-256, corridas, pendientes y controles. `trazabilidad_paginas.csv` es el registro compacto para repetir la actualización.

## Interpretación y controles de concordancia

- Clínica: 391 pacientes, 370 AOO observadas y 21 originalmente faltantes. MICE–PMM M1b imputa la **brecha edad de evaluación − AOO** y reconstruye AOO. Cada una de las veinte bases mantiene exactamente los mismos pacientes y los valores observados. MissForest es sensibilidad separada.
- Univariado: estadísticos dentro de cada imputación y resumen entre estimadores. Rubin se reserva para la media y su incertidumbre; los otros descriptivos son resúmenes empíricos. No se utilizan 7.820 filas como individuos independientes.
- Bivariado: 142 variables, 90 evaluables, 25 asociaciones observadas tras FDR; 23 recurren en 20/20. Educación/FVFs conservan signo 20/20 y FDR 19/20. Kruskal–Wallis: **eta cuadrado basado en H (η²_H)**. Las etiquetas de hipertensión se mantienen por código mientras falta respaldo. BH se calcula por separado por base; recurrencia es sensibilidad descriptiva a M1b, no inferencia combinada.
- Panel histórico: `exosoms-qc-full.txt`, 128.757 SNPs autosómicos. Panel actual: `functional-variants.txt`, 18.391 SNPs de asociación y 18.254 marcadores de estructura. MAF > 0,01 informado; GCR/HWE/poda del proveedor y ensamblaje pendientes de corroboración documental. La poda local para PCA/GRM no filtra el universo de GWAS.
- GWAS principal: 334 casos, cinco PCs, sexo y educación agrupada, GRM–LOCO, REML nulo por cromosoma y Wald bilateral. Cero FDR/Bonferroni, λGC ≈ 1,0248. SNP con menor p: `17:5086956-A-C`, p ≈ 3,475×10⁻⁵; exploratorio. Los números mostrados proceden de tablas, no de este texto de control.
- MI genética: 18 casos adicionales elegibles, N=352 en cada una de veinte corridas, cero asociaciones corregidas. M1b no incluyó PCs/genotipos: sensibilidad descriptiva, sin combinar p/q.
- APOE: ambos rs429358/rs7412 probados individualmente, sin APOE como covariable del Modelo B. Algunas combinaciones no faseadas admiten más de un diplotipo compatible.
- Diagnóstico de chr8: el global con sexo/3,5,10 PCs ya era interior; con cinco PCs h² ≈ 0,538 y LOCO sin chr8 ≈ 0,495. Cero de 22 diagnósticos LOCO con varianza residual cero. La transición frontera/interior es histórica, no un hallazgo actual ni del Modelo B con educación.

## Privacidad del paquete de presentación

No se distribuyen bases clínicas por paciente, IDs, dosis individuales, matrices GRM individuales ni imputaciones long. Se conservan localmente en el proyecto fuente. La preparación sustituye los derivados antiguos identificables de `data/` por:

- Frecuencias, histogramas y descriptivos de una variable a la vez.
- PCs anónimos, sin IDs ni atributos clínicos y con orden de filas permutado de forma reproducible. El HTML 3D se genera a partir de esta tabla; **no se copia el HTML local con identificadores**.
- Trazabilidad de extremos agregada y comparaciones clínicas/genéticas por grupo.
- Distribuciones de GRM y heatmap de medias por bloques; IBS por número de par sin identidad.
- Resultados por variante, estadísticos, auditorías y resúmenes por imputación.

Los puntos PCA no se vinculan en la app con sexo ni AOO individual. Los gráficos bivariados se basan en efectos/estabilidad ya exportados, no en la publicación de pares clínicos.

## Verificación

```bash
python tests/verify_dashboard.py
```

La prueba carga las 18 páginas con `streamlit.testing.v1.AppTest`, verifica tablas y figuras y cambia controles de páginas clave. Guarda `verificacion_paginas.json` y `verificacion_interacciones.json`. Se recomienda volver a ejecutarla tras regenerar `data/`. El arnés normaliza el estado escalar de `segmented_control` para AppTest 1.50; no altera los controles de la aplicación. Los mensajes `missing ScriptRunContext` del hilo principal pertenecen al arnés de AppTest, no a errores de las páginas.

La preparación verifica fuentes preservadas, IDs/observados en MI, denominadores, número de SNPs, significancia corregida, alineación de las tablas, procedencia de las corridas y ausencia de columnas identificadoras en los CSV de presentación. No recalcula imputación, PCA, GRM, modelos nulos ni GWAS; únicamente resume salidas existentes y matrices guardadas.


## Diseño vigente

Se conserva el diseño visual anterior a la propuesta editorial: portada con degradado, barra lateral vinotinto, tipografía, tarjetas y composición originales. Los datos y funciones actuales (MI, panel nuevo, PCA 3D, LOCO, GWAS y APOE) se mantienen. Se conservan también los selectores nuevos de distribución observada/MI y extensión del ranking. Ver `restauracion_diseno.json`.
