# Experimentos de Comparación — Arquitecturas de Agente ETL

Contiene los notebooks del **estudio comparativo** entre tres frameworks de orquestación de agentes aplicados al mismo pipeline ETL sobre datos bananeros del Ecuador.

---

## Objetivo del experimento

Determinar cuál arquitectura de agente produce el mejor balance entre **velocidad**, **calidad del dato** y **autonomía** en un pipeline ETL sobre datos agrícolas heterogéneos (xlsx, csv, pdf, json), evaluando además su robustez ante escenarios de perturbación controlada.

---

## Las tres arquitecturas comparadas

| Carpeta | Framework | Descripción |
|---------|-----------|-------------|
| `agente_custom/` | Python puro | Agente escrito 100% en Python sin frameworks de orquestación. Clases simples (`AgenteExtraccion`, `AgenteETL`, `AgenteExportacion`) sobre un estado compartido. |
| `langgraph/` | LangGraph | Grafo de nodos con aristas condicionales. Estado tipado con `TypedDict`. Nodos: extracción → transformación → carga → métricas. |
| `llamaindex/` | LlamaIndex Workflows | Pipeline basado en eventos (`Event`/`Step`). Orquestación asíncrona. Mantiene la misma estructura de métricas que LangGraph. |

Todos usan **Llama 4 Maverick** (Databricks Foundation Model) como LLM orquestador y el mismo conjunto de datos (ESPAC · SIPA · FAOSTAT · AEBE).

---

## Notebooks por arquitectura

### `agente_custom/`

| Notebook | Rol |
|----------|-----|
| `ETL Inteligente Agente Custom Banano Ecuador.ipynb` | Versión baseline — sin escenarios de fallo |
| `IA-ETL Inteligente Agente Custom Banano Ecuador.ipynb` | Versión de experimento — con escenarios A/B/C |

### `langgraph/`

| Notebook | Rol |
|----------|-----|
| `ETL Inteligente LangGraph Banano Ecuador.ipynb` | Versión baseline |
| `IA-ESC_ETL_LangGraph_Banano_Experimento (2).ipynb` | Versión de experimento con escenarios A/B/C |

### `llamaindex/`

| Notebook | Rol |
|----------|-----|
| `ETL_LlamaIndex_Banano_v3_pdfplumber (2).ipynb` | Versión baseline + soporte PDF con pdfplumber |
| `IA-ESC_ETL_LlamaIndex_Banano_Experimento.ipynb` | Versión de experimento con escenarios A/B/C |

---

## Diseño experimental

| Parámetro | Valor |
|-----------|-------|
| Corridas por combinación arquitectura-escenario | **10** |
| Escenarios | 3 (A, B, C) |
| Fuentes por corrida | 12 archivos |
| Total combinaciones | 9 (3 arq. × 3 esc.) |
| Registros totales en log | **960** |

> **Excepción documentada — LangGraph B y C:** en los escenarios perturbados, LangGraph procesó únicamente **6 de las 12 fuentes** (ESPAC 2020–2025), dejando sin procesar FAOSTAT, SIPA y AEBE. Por ello su log contiene **60 registros** por escenario (6 archivos × 10 corridas) en lugar de 120. Los promedios reportados en el artículo corresponden exclusivamente a las fuentes que sí completaron el proceso.

---

## Métricas recolectadas

### Métricas cuantitativas (M1–M3)

| ID | Métrica | Qué mide |
|----|---------|----------|
| M1 | Tiempo de ejecución | Segundos por archivo procesado por corrida |
| M2 | Calidad del dato | % de registros válidos tras transformación. Se excluyen del promedio ESPAC-2019 y AEBE-PDF (anomalías estructurales de las fuentes originales) |
| M3 | Llamadas al LLM | Invocaciones al modelo por archivo procesado |

### Métricas cualitativas (M4–M5, registros de ejecución)

| ID | Métrica | Qué documenta |
|----|---------|---------------|
| M4 | Robustez ante variación de esquema | Registros extraídos ante el renombrado del PDF de AEBE Bananotas en el Escenario B |
| M5 | Cobertura de fuentes | Número de fuentes completadas en escenarios perturbados (6/12 en LangGraph B y C) |

---

## Resultados por métrica y escenario

### M1 — Tiempo de ejecución promedio por archivo (segundos)

| Arquitectura | Escenario A | Escenario B | Escenario C | Promedio global |
|---|---:|---:|---:|---:|
| Custom | 13,22 | 13,40 | 13,24 | 13,33 |
| LangGraph | 12,52 | 13,98 | 13,79 | 13,20 |
| LlamaIndex Workflows | 14,79 | 12,75 | 13,76 | 13,77 |

*Menor es mejor. Nota: LangGraph B y C sobre 6 fuentes, no comparables directamente con Custom y LlamaIndex.*

### M2 — Calidad de datos promedio (%, excluye ESPAC-2019 y AEBE-PDF)

| Arquitectura | Escenario A | Escenario B | Escenario C | Promedio global |
|---|---:|---:|---:|---:|
| Custom | 72,32 | 72,32 | 71,45 | 72,03 |
| LangGraph | 72,32 | 64,04 | 64,04 | 66,80 |
| LlamaIndex Workflows | 72,32 | 72,32 | 72,32 | 72,32 |

*Mayor es mejor.*

### M3 — Llamadas al LLM promedio por archivo

| Arquitectura | Escenario A | Escenario B | Escenario C | Promedio global |
|---|---:|---:|---:|---:|
| Custom | 0,917 | 1,000 | 0,968 | 0,972 |
| LangGraph | 1,000 | 1,000 | 1,000 | 1,000 |
| LlamaIndex Workflows | 0,917 | 1,000 | 0,900 | 0,933 |

*Menor es mejor (menor dependencia del modelo durante la orquestación).*

---

## Escenarios del experimento (A / B / C)

| Escenario | Tipo de perturbación inyectada | Lo que se mide |
|-----------|-------------------------------|----------------|
| **A** — Nominal | Sin fallos (baseline limpio) | Rendimiento base de la arquitectura |
| **B** — Corrupción de datos | Valores nulos, tipos incorrectos, encoding roto + renombrado del PDF de AEBE | Capacidad de detección y corrección automática |
| **C** — Fallo de fuente | Fuente no disponible / timeout de descarga | Recuperación autónoma sin intervención manual |

---

## Estructura de tablas Delta por framework

### Agente Custom
```
bd_banano_ec.metricas_extraccion
bd_banano_ec.metricas_transformacion
bd_banano_ec.metricas_carga
bd_banano_ec.control_logs_agente_custom
```

### LangGraph
```
bd_banano_ec.metricas_extraccion
bd_banano_ec.metricas_transformacion
bd_banano_ec.metricas_carga
bd_banano_ec.control_logs_langgraph
```

### LlamaIndex
```
bd_banano_ec.metricas_extraccion_li
bd_banano_ec.metricas_transformacion_li
bd_banano_ec.metricas_carga_li
bd_banano_ec.control_logs_etl
```

---

## Cómo ejecutar un experimento

> ⚠️ **Antes de ejecutar**, localiza las primeras celdas del notebook y completa con tus propios valores:
> - `DB_NAME` — nombre de tu base de datos Delta en Unity Catalog (ej: `bd_banano_ec`)
> - Rutas `/Volumes/` — ajusta al esquema de volumen de tu workspace
> - `SERVICE_ACCOUNT_INFO` *(solo notebooks con exportación)* — JSON de cuenta de servicio de Google
>
> No ejecutes ningún bloque sin haber llenado estos valores.

1. Completar los secretos y parámetros de configuración (ver advertencia arriba)
2. Importar el notebook al workspace de Databricks
3. **Bloque 0 (opcional):** ejecutar solo si quieres resetear tablas y volúmenes desde cero
4. **Bloque 1:** instalar librerías y reiniciar kernel
5. Ejecutar el resto de los bloques en orden
6. Los resultados quedan en las tablas Delta y en `../resultados/metricas/`

> ⚠️ No ejecutes el Bloque 0 en la misma corrida que el pipeline. Primero resetea, luego ejecuta desde el Bloque 1.

---

## Resultados y comparativas

Los outputs del experimento (log en xlsx/csv con 960 registros, gráficos) están en `../resultados/`.
