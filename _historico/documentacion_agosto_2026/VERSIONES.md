# Versiones y entorno

- **Plataforma:** Databricks Free Edition, cómputo serverless, versión de entorno 5 (según los metadatos de los notebooks).
- **Python:** no se registró `sys.version` durante los experimentos. La autora reportó Python 3.11, mientras que la documentación de Databricks asocia el entorno serverless versión 5 con Python 3.12.3.
- **Modelo:** `databricks-llama-4-maverick`.
- **Código:** etiqueta `v1.0-revision-ingenius`. El repositorio contiene únicamente la versión final de los notebooks.

## Cronología de ejecución
| Arquitectura | Escenario A | Escenario B | Escenario C |
|:---|:---|:---|:---|
| Agente Custom | 04-ago (R08_REP: 13-ago) | 13-ago | 13 y 14-ago |
| LangGraph | 13-ago | 13-ago | 13-ago |
| LlamaIndex | 07-ago | 13-ago | 14-ago |

## Diferencias de versión y protocolo conocidas
- **LlamaIndex, escenario A (07-ago):** se ejecutó con una versión anterior del notebook, que no está en el historial de este repositorio. Las tablas no se vaciaron entre ejecuciones, por lo que el total de filas del registro acumulaba el conteo de la tabla (corregido con `filas_entrada`).
- En los demás escenarios se vaciaron volúmenes y tablas de la corrida anterior antes de cada ejecución. La sesión no se reinició y no hubo ejecuciones de calentamiento.
- La perturbación del Escenario B de LangGraph difiere de la de las otras dos (renombrado de la primera columna en Excel y FAOSTAT).
