# Versiones y entorno (lote oficial, noviembre de 2026)

Fuentes: (1) hoja `P10_Entorno_Corridas` del consolidado: entorno común y `pip freeze` (299 paquetes) capturado el 2026-11-03 03:45 UTC en el compute del workspace; (2) versiones por framework, tomadas del resultado de la instalación de cada notebook y aportadas por las autoras.

**Límite que se mantiene:** el `pip freeze` es del compute del workspace en la fecha de captura (3-nov-2026), **no de cada ejecución**, y no está vinculado a cada `execution_id`. Las versiones por framework provienen de la instalación de cada notebook, no de un freeze por corrida.

**Dónde están las versiones por framework en el consolidado:** en `P10_Entorno_Corridas` (filas 8-10 y 12 y filas 313-315, «Versiones instaladas …»), tomadas de la salida de instalación de cada notebook. El `pip freeze` de esa hoja (filas 13-312) no lista `llama-index*`; por eso `analisis/analisis_ingenius.py` lee las filas de instalación y la limitación L4 indica que la fuente no es el freeze. Detalle y SHA-256 en `resultados/logs/README.md`.

## Entorno común (todos los notebooks)
| Componente | Valor |
|:--|:--|
| Plataforma | Databricks Free Edition, serverless; Linux 6.1.189 aarch64 (ARM), glibc 2.39 |
| Python | 3.12.3 |
| Databricks Runtime | 18.2 (databricks-connect 18.2.8) |
| Spark | pyspark 4.1.0+databricks.connect.18.2.8 (`spark.version` reporta 4.2.0); delta-spark 3.4.0+databricks.connect.18.2.8 |
| Databricks SDK | databricks-sdk 0.67.0 |
| Modelo | `databricks-llama-4-maverick` (Foundation Models, sin API externa) |
| pandas / numpy / openpyxl / xlrd / pdfplumber / scikit-learn | 2.2.3 / 2.1.3 / 3.1.5 / 2.0.2 / 0.11.10 / 1.6.1 |

## Versiones por notebook (resultado de la instalación de cada notebook)
| Notebook | Paquetes |
|:--|:--|
| AgenteCustom (sin framework de orquestación; código a medida) | langchain 0.3.30; langchain-core 0.3.86; langchain-databricks 0.1.2; langchain-text-splitters 0.3.11 |
| LangGraph | langgraph 1.0.1 (langgraph-prebuilt 1.0.1, langgraph-checkpoint 3.0.1, langgraph-sdk 0.2.15); langchain 0.3.30; langchain-core 0.3.86; langchain-databricks 0.1.2 |
| LlamaIndex Workflows | llama-index 0.14.25; llama-index-core 0.14.25; llama-index-workflows 2.26.1; llama-index-embeddings-openai 0.6.0; llama-index-instrumentation 0.6.0; llama-index-llms-openai 0.7.10; langchain-core 0.3.86; langchain-databricks 0.1.2 |

Instalaciones por sesión: AgenteCustom 2026-11-02 23:38; LlamaIndex 2026-11-02 23:44; LangGraph 2026-11-03 00:18.

## Código
Los notebooks de `experimentos_comparacion/` provienen de las versiones sincronizadas el 2-nov (23:36–23:37) y usadas en la re-ejecución del escenario B el 3-nov. Se publican sin salidas y con datos personales normalizados; fuera de eso, sin cambios. Los notebooks con que se ejecutaron los escenarios A y C (antes de esa sincronización) no se conservaron.

### Identificación de la versión del código
| Versión | Etiqueta | Commit | Contenido |
|:--|:--|:--|:--|
| Enviada a INGENIUS | `v1-enviado-ingenius` | `994eda6` | Primera versión enviada (obsoleta; ver `_historico/`) |
| Revisión INGENIUS (citada en el manuscrito) | `v2-revision-ingenius` | `c12ffac` | Notebooks, scripts de análisis, consolidado y anexos de la revisión |
| Actualización de documentación (este archivo) | — | <mark>HASH_NUEVO_COMMIT</mark> | Solo corrige este documento; no modifica notebooks, datos ni resultados |

La versión de los notebooks queda fijada por su suma SHA-256 en `SHA256SUMS.txt` y por la etiqueta `v2-revision-ingenius`. Mapa de las celdas relevantes (perturbaciones, identificación de fuente, métricas) en `experimentos_comparacion/MAPA_DE_CODIGO.md`.

## Cronología de lotes
| Lote | Fecha | Estado |
|:--|:--|:--|
| Precedente LangGraph | 1-nov | No incluido (versión temprana; AEBE leído como 1 fila) |
| Pruebas AgenteCustom y LlamaIndex | 2-nov | Descartadas (sin `execution_id` / combinaciones ausentes) |
| `corrida_oficial_2nov` A y C | 2-nov | **Incluidos** |
| `corrida_oficial_2nov` B | 2-nov | **Descartado**: no aplicó las perturbaciones |
| Intento LangGraph-B | 3-nov ~01:00 | Cancelado, sin datos |
| `corrida_oficial_3nov` B (3 frameworks) | 3-nov | **Incluido** |

Ventanas por combinación: anexo A6 y hoja `Cronologia_ventanas` de `resultados/tablas/tablas_ingenius.xlsx`.

## Diferencias de protocolo conocidas
- A/C y B se ejecutaron en días y sesiones distintos; cada combinación en un bloque de 10 corridas, sin aleatorizar ni intercalar; sin ejecuciones de calentamiento registradas.
- En B, las ventanas de AgenteCustom (01:10–02:05) y LlamaIndex (01:06–02:01) se solapan en el tiempo y pudieron compartir infraestructura.
- 225 registros de LlamaIndex (A/C) tienen `total_filas` distinto de `filas_entrada`; M2 usa `filas_entrada`/`filas_salida`.
