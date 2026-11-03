# Registros de ejecución

## finales/ (los que respaldan el manuscrito)
| Archivo | Contenido |
|:---|:---|
| `metricas_completas_ABC_AgenteCustom_20260814_005013.xlsx` | 30 ejecuciones (A, B, C) del Agente Híbrido; 360 filas |
| `metricas_completas_ABC_LangGraph_20260813_220302.xlsx` | 30 ejecuciones de LangGraph; 360 filas |
| `metricas_completas_ABC_LlamaIndex_20260814_063441.xlsx` | 30 ejecuciones de LlamaIndex Workflows; 360 filas (hojas `HIST_*` = lotes descartados) |
| `experimento_llamaindex_20260807_083208.xlsx` | Log original de LlamaIndex del 7-ago (escenario A). Contiene `Metricas_Transformacion.filas_entrada`, usado para corregir `Total_Filas` |

Estos tres logs concilian sin diferencias con `resultados/metricas/metricas_reformuladas_tesis.xlsx` (1,080 filas).

## lotes_descartados/ (conservados como evidencia; no se usan en los resultados)
| Archivo | Motivo |
|:---|:---|
| `Resultados_AgenteCustom_Final.xlsx`, `experimento_agentecustom_20260804_222910.xlsx` | Custom escenario C (4-5 ago): tablas sin vaciar entre corridas, con filas imputadas (hoja `HISTORICO_C_INVALIDO`); R08 de A con 11 archivos (`R08_HISTORICA_INVALIDA`) |
| `CUSTOM_verificacion_escenario_c_20260806_001114.xlsx` | Verificación cruzada del lote anterior |
| `Resultados_LangGraph_Final.xlsx` | LangGraph 10-ago: carpeta de entrada sin limpiar (23-24 archivos por corrida) |

Nota: las corridas de Custom C `R01_TEST` y `R02_TEST` son válidas (posteriores a la corrección); solo conservan el sufijo en el nombre.
