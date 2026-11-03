# Registros de ejecución

## finales/ — respaldan el manuscrito
| Archivo | Contenido |
|:--|:--|
| `experimentos_3frameworks_todas_corridas_20261103_B_actualizado.xlsx` | Consolidado oficial: 90 ejecuciones, 1.080 instancias. Hojas: `Logs_TODAS_1080`, `Extraccion_TODAS_360`, `Transformacion_TODAS_1080`, `Carga_TODAS_1080`, `Evidencia_por_Archivo_1080`, `P6_Archivos_Escenario_B`, `P8_Resumen_Reintentos`, `P9_Registro_Corridas`, `P10_Entorno_Corridas` (y hojas de apoyo) |

Lotes: A y C = `corrida_oficial_2nov`; B = `corrida_oficial_3nov`. El B del 2-nov (sin perturbaciones) y el primer intento cancelado de LangGraph-B quedan **excluidos**; `P9_Registro_Corridas` y el anexo A5 documentan el motivo. Los exports intermedios citados en P9 no están en este repositorio.

Se añadió la hoja `Aclaraciones_manuscrito` (2026-11-03); no modifica datos. SHA-256 del archivo original antes de añadirla: `7624a06346d099468b23a89b746e7b02457ab21531db6f8347cee619fa3c3155`.

`analisis/analisis_ingenius.py` lee solo este archivo.

## Estado del consolidado (3-nov-2026)
El consolidado de esta carpeta es el vigente: 26 hojas (las 25 del original más `Aclaraciones_manuscrito`). Sobre el original se editaron solo celdas de texto y se añadieron filas a `P10_Entorno_Corridas`; **ninguna hoja de datos se modificó** (`Logs_TODAS_1080`, `Extraccion_TODAS_360`, `Transformacion_TODAS_1080`, `Carga_TODAS_1080`, `Evidencia_por_Archivo_1080` y las hojas P2-P9 son las del original):
- `P10_Entorno_Corridas`: B8, B9, B10 y B12 (versiones por framework), errata «ejutada» en A10, y filas 313-315 nuevas, «Versiones instaladas AgenteCustom / LlamaIndex / LangGraph (salida de instalación del notebook)» (P10 queda en 315 filas).
- `00_Guia_Lectura` (fila del índice de `Aclaraciones_manuscrito`, D30 y glosario), `Notas` A23 y `Verif_Revisor_10Puntos` F11 remiten a esas filas.
- `Aclaraciones_manuscrito` (hoja nueva): equivalencia M1–M6 consolidado ↔ manuscrito, causa del etiquetado INEC_ESPAC del archivo SIPA de uso del suelo en AgenteCustom (A, B y C), base de M2, WARNING, granularidad de M5, orden de ejecución y lotes.

Las versiones (LlamaIndex 0.14.25, workflows 2.26.1, LangGraph 1.0.1, langchain 0.3.30, etc.) provienen de la salida de instalación de cada notebook, **no** del `pip freeze` del compute (filas 13-312), que no lista `llama-index*`. `analisis_ingenius.py` lee las filas 313-315 y la limitación L4 indica esa fuente.

SHA-256 del consolidado: antes de estas ediciones `c4f99328a92c76435cc05cc5c2097e7748f57e4f1c51ce1e1a13b5889844be45`; actual `4b0ad39acfe9117d5106eb9606559d08c5f85801d9ca87f1370f66a7d02ff662`.

## Material de agosto
Los logs de agosto (finales y lotes descartados) están en `../../_historico/resultados_agosto_2026/logs/`. No se usan en los resultados vigentes.
