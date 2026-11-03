# Material histórico (OBSOLETO)

Contiene lo que respaldaba la **primera versión enviada** a INGENIUS (agosto–octubre de 2026). **No son los resultados oficiales.** Se conserva para poder auditar qué cambió y por qué. No borrar.

| Carpeta | Contenido |
|:--|:--|
| `notebooks_comparacion_v1_enviado/` | Los tres notebooks enviados (idénticos al commit `994eda6`, 22-oct, salvo saltos de línea) |
| `resultados_agosto_2026/` | Logs, métricas, tablas y figuras de agosto; `graficos_commit_994eda6/` recupera de Git las figuras originales; `graficos_borrador_esquema_antiguo/` son borradores generados con el esquema antiguo |
| `analisis_esquema_antiguo/` | Scripts de agosto (esquema `7_Datos_Individuales`) y `crear_notebooks_reproducibles_agosto.py` (fija `llama-index==0.14.23` y `llama-index-workflows==2.22.2`; **esas versiones no coinciden con las registradas en la instalación de los notebooks (0.14.25 y 2.26.1) y no deben usarse**; el script no se regeneró para los notebooks nuevos) |
| `documentacion_agosto_2026/` | README, REPRODUCIBILIDAD, VERSIONES y requirements anteriores |

`resultados_agosto_2026/metricas/metricas_reformuladas_tesis.xlsx` es el Excel de métricas (1.080 instancias) que acompañaba la versión enviada (commit `994eda6`, con el nombre original `metricas_reformuladas_tesis (1).xlsx`); fue reemplazado por el consolidado de noviembre.

Vigente: tres notebooks en `experimentos_comparacion/`, consolidado de noviembre en `resultados/logs/finales/` y scripts en `analisis/`.
Las cifras de agosto (p. ej. M2 de LlamaIndex 98,75 %, M4 = 75 % por AEBE desconocida en Custom/LangGraph, M5 = 4,6/5,8/5,5) **ya no se sostienen**.
Recomendado al hacer commit: etiqueta `v1-enviado-ingenius` sobre el estado anterior.
