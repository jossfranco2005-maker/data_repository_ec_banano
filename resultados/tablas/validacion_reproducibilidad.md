# Reporte de validacion y reproducibilidad estadistica

Archivo analizado: `experimentos_3frameworks_todas_corridas_20261103_B_actualizado.xlsx`

**Nivel de reproducibilidad demostrado:** reconstruccion de las estadisticas a partir de los registros del consolidado. **No** se ejecutaron los notebooks ni se accedio a Databricks; la reproduccion experimental real queda pendiente (ver `REPRODUCIBILIDAD.md`).

## 1. Verificaciones de integridad: 35/35 correctas

| verificacion | esperado | obtenido | ok | nota |
|:---|:---|:---|:---|:---|
| Filas en Logs | 1080 | 1080 | True |  |
| Filas en Transformacion | 1080 | 1080 | True |  |
| Filas en Carga | 1080 | 1080 | True |  |
| Filas en Evidencia_por_Archivo | 1080 | 1080 | True |  |
| Filas en Extraccion | 360 | 360 | True |  |
| execution_id faltantes en Logs | 0 | 0 | True |  |
| execution_id faltantes en Extraccion | 0 | 0 | True |  |
| execution_id faltantes en Transformacion | 0 | 0 | True |  |
| execution_id faltantes en Carga | 0 | 0 | True |  |
| Duplicados (execution_id, file_name) en Logs | 0 | 0 | True |  |
| Duplicados (execution_id, file_name) en Transformacion | 0 | 0 | True |  |
| Duplicados (execution_id, file_name) en Carga | 0 | 0 | True |  |
| Duplicados (execution_id, file_name) en Evidencia | 0 | 0 | True |  |
| Duplicados (execution_id, fuente) en Extraccion | 0 | 0 | True |  |
| Ejecuciones distintas (Logs) | 90 | 90 | True |  |
| 10 ejecuciones por framework x escenario (9 combinaciones) | True | True | True |  |
| 12 archivos por ejecucion | True | True | True |  |
| 4 fuentes por ejecucion en Extraccion | True | True | True |  |
| Mismas llaves Logs = Transformacion | True | True | True |  |
| Mismas llaves Logs = Carga | True | True | True |  |
| Mismas llaves Logs = Evidencia | True | True | True |  |
| Mismas ejecuciones Logs = Extraccion | True | True | True |  |
| filas_entrada y filas_salida: Transformacion = Evidencia | True | True | True |  |
| registros_insertados (Carga) = filas_salida (Transformacion) | True | True | True |  |
| Escenario del execution_id coincide con la columna escenario | True | True | True |  |
| Filas con status ERROR (Logs) | 0 | 0 | True |  |
| Filas con error_message (Logs) | 0 | 0 | True |  |
| WARNING totales (Logs) | 80 | 80 | True | Distribucion observada: LangGraph-A=20; LangGraph-B=20; LangGraph-C=20; LlamaIndex-B=20. WARNING = advertencia de calidad, no ERROR. |
| Lote: A y C = corrida_oficial_2nov; B = corrida_oficial_3nov | True | True | True |  |
| P9 registra el B del 2-nov como descartado | True | True | True |  |
| Discrepancias total_filas (Logs) vs filas_entrada | 225 | 225 | True | Todas en LlamaIndex A/C: True. Para M2 se usan filas_entrada y filas_salida. |
| archivos_error total en Extraccion | 0 | 0 | True |  |
| P6: filas (12 archivos x 3 frameworks) | 36 | 36 | True |  |
| P6: 10 corridas por archivo | True | True | True |  |
| P6: 12 archivos por framework | True | True | True |  |

## 2. Contraste con las cifras oficiales del manuscrito: 25/25 coinciden

| metrica | detalle | oficial | calculado | ok |
|:---|:---|:---|:---|:---|
| M1 | A AgenteCustom media +- DE | 14.57 +- 1.25 | 14.57 +- 1.25 | True |
| M1 | A LangGraph media +- DE | 14.73 +- 0.79 | 14.73 +- 0.79 | True |
| M1 | A LlamaIndex media +- DE | 15.28 +- 0.60 | 15.28 +- 0.60 | True |
| M1 | B AgenteCustom media +- DE | 14.12 +- 0.61 | 14.12 +- 0.61 | True |
| M1 | B LangGraph media +- DE | 12.27 +- 0.64 | 12.27 +- 0.64 | True |
| M1 | B LlamaIndex media +- DE | 14.99 +- 0.79 | 14.99 +- 0.79 | True |
| M1 | C AgenteCustom media +- DE | 14.59 +- 1.25 | 14.59 +- 1.25 | True |
| M1 | C LangGraph media +- DE | 15.36 +- 1.73 | 15.36 +- 1.73 | True |
| M1 | C LlamaIndex media +- DE | 15.24 +- 0.36 | 15.24 +- 0.36 | True |
| M1 | Kruskal-Wallis A (p) | 0.01298 | 0.01297779 | True |
| M1 | Kruskal-Wallis B (p) | 3.57e-05 | 3.571285e-05 | True |
| M1 | Kruskal-Wallis C (p) | 0.01183 | 0.01182642 | True |
| M2 | media simple | 98.64 | 98.6349 | True |
| M2 | promedio ponderado por filas | 87.24 | 87.2412 | True |
| M3 | escenario A (3 frameworks) | 0.9167 | 0.9167 | True |
| M3 | escenario B (3 frameworks) | 1 | 1.0000 | True |
| M3 | escenario C (3 frameworks) | 0.9167 | 0.9167 | True |
| M4 | AgenteCustom en B (fuente / archivo) | 75.0 / 91.7 | 75.0 / 91.7 | True |
| M4 | LangGraph en B (fuente / archivo) | 100.0 / 100.0 | 100.0 / 100.0 | True |
| M4 | LlamaIndex en B (fuente / archivo) | 100.0 / 100.0 | 100.0 / 100.0 | True |
| M5 | AgenteCustom en C media +- DE | 5.3 +- 1.34 | 5.3 +- 1.34 | True |
| M5 | LangGraph en C media +- DE | 5.7 +- 2.36 | 5.7 +- 2.36 | True |
| M5 | LlamaIndex en C media +- DE | 6.6 +- 1.43 | 6.6 +- 1.43 | True |
| M5 | Kruskal-Wallis C (p) | 0.1866 | 0.1866 | True |
| M5 | Recuperacion final en C (3 frameworks) | 100 % | 100.0 % | True |

## 3. Pruebas estadisticas (M1)

| escenario | H | gl | p |
|:---|:---|:---|:---|
| A | 8.6890 | 2 | 0.01297779 |
| B | 20.4800 | 2 | 3.571285e-05 |
| C | 8.8748 | 2 | 0.01182642 |

Pares (Mann-Whitney bilateral; Holm por escenario = 3 comparaciones):

| escenario | comparacion | p | p_holm_escenario | p_holm_global_9 | menor_media |
|:---|:---|:---|:---|:---|:---|
| A | AgenteCustom vs LangGraph | 0.27304 | 0.27304 | 0.54607 | AgenteCustom |
| A | AgenteCustom vs LlamaIndex | 0.00459 | 0.01376 | 0.02752 | AgenteCustom |
| A | LangGraph vs LlamaIndex | 0.07566 | 0.15132 | 0.30265 | LangGraph |
| B | AgenteCustom vs LangGraph | 0.00058 | 0.00117 | 0.00466 | LangGraph |
| B | AgenteCustom vs LlamaIndex | 0.02575 | 0.02575 | 0.12874 | AgenteCustom |
| B | LangGraph vs LlamaIndex | 0.00018 | 0.00055 | 0.00164 | LangGraph |
| C | AgenteCustom vs LangGraph | 0.07566 | 0.15132 | 0.30265 | AgenteCustom |
| C | AgenteCustom vs LlamaIndex | 0.00361 | 0.01083 | 0.02527 | AgenteCustom |
| C | LangGraph vs LlamaIndex | 0.30749 | 0.30749 | 0.54607 | LlamaIndex |

## 4. Efecto de orden de ejecucion (diagnostico post hoc)

| escenario | framework | rho_spearman | p | p_holm_9 | signif_holm_0.05 |
|:---|:---|:---|:---|:---|:---|
| A | AgenteCustom | -0.733 | 0.0158 | 0.1106 | False |
| A | LangGraph | -0.939 | 0.0001 | 0.0005 | True |
| A | LlamaIndex | -0.842 | 0.0022 | 0.0178 | True |
| B | AgenteCustom | -0.309 | 0.3848 | 1.0000 | False |
| B | LangGraph | -0.285 | 0.4250 | 1.0000 | False |
| B | LlamaIndex | -0.673 | 0.0330 | 0.1982 | False |
| C | AgenteCustom | -0.127 | 0.7261 | 1.0000 | False |
| C | LangGraph | 0.576 | 0.0816 | 0.4078 | False |
| C | LlamaIndex | 0.103 | 0.7770 | 1.0000 | False |

## 5. Limitaciones documentadas por el script

| id | limitacion | detalle |
|:---|:---|:---|
| L1 | Orden de ejecucion no aleatorizado | Cada framework x escenario se ejecuto en un bloque de 10 corridas sin intercalar. Diagnostico post hoc (Spearman corrida vs M1, Holm sobre 9): efecto de orden significativo en A-LangGraph (rho=-0.94, p_Holm=0.0005), A-LlamaIndex (rho=-0.84, p_Holm=0.0178). En esos casos M1 baja con el numero de corrida, por lo que las diferencias en A pueden mezclar arquitectura y orden. |
| L2 | Ejecuciones solapadas en el tiempo | Ventanas temporales de las corridas (execution_timestamp): B-AgenteCustom solapa con LlamaIndex; B-LlamaIndex solapa con AgenteCustom. Si dos frameworks se ejecutaron en paralelo comparten infraestructura. |
| L3 | Compute no vinculado a cada execution_id | Las tablas de metricas no registran el cluster/compute de cada corrida. El pip freeze de P10 corresponde al compute del workspace en el momento de captura (3-nov-2026), no a cada ejecucion. No se puede reconstruir esta trazabilidad desde el consolidado. |
| L4 | Versiones de LlamaIndex registradas en P10 | P10 registra: llama-index==0.14.25, llama-index-core==0.14.25, llama-index-embeddings-openai==0.6.0, llama-index-instrumentation==0.6.0, llama-index-llms-openai==0.7.10, llama-index-workflows==2.26.1. Fuente: salida de instalacion del notebook (no pip freeze). No corresponden a una captura por ejecucion ni a un freeze por corrida (ver L3). |
| L5 | Reintentos contados por fuente y ejecucion | No hay eventos de intento por archivo; M5 se agrega por ejecucion (suma de las 4 fuentes). No se reporta una tasa de reintentos por archivo. M5 mide costo de recuperacion, no eficiencia. |
| L6 | Fallo controlado sin semilla | El truncamiento de C usa random.random() < 0.5 sin semilla en los tres notebooks: la proporcion de fallos es reproducible en distribucion, no archivo por archivo. No se puede reconstruir desde el consolidado que descargas se truncaron. |
| L7 | M2 mide integridad/validez por reglas, no exactitud semantica | M2 = filas_salida / filas_entrada. No contrasta contra una fuente de verdad independiente. La DE de M2 entre ejecuciones es 0, por lo que no se aplican pruebas de hipotesis. |
| L8 | Filas de LlamaIndex A/C con total_filas distinto de filas_entrada | 225 registros del log; para M2 se usan filas_entrada y filas_salida de Transformacion. |
| L9 | Implementaciones completas, no solo arquitecturas | Las tres soluciones comparten los helpers de perturbacion pero difieren en identificacion de fuentes, manejo de errores y reintentos. Ejemplo verificado: Custom antepone 'ESPAC_' al archivo SIPA de uso del suelo en la descarga, por lo que identificar_fuente (misma logica en los tres) lo etiqueta INEC_ESPAC en A, B y C. Las conclusiones se limitan a las soluciones completas evaluadas. |
| L10 | Estadisticos exploratorios | n = 10 ejecuciones por combinacion; los 12 archivos de una ejecucion no son observaciones independientes. Kruskal-Wallis y Mann-Whitney con Holm son exploratorios. |

## 6. Lo que NO se puede reproducir desde el consolidado

- Que descarga concreta se trunco en C (sin semilla ni evento por archivo).
- Compute/cluster de cada ejecucion (no esta vinculado a execution_id).
- Tiempo de recuperacion e intentos por archivo (no se registraron eventos individuales).
- Exactitud semantica de los datos transformados (M2 solo mide integridad/validez por reglas).
