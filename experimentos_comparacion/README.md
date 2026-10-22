# Experimentos de Comparación — Arquitecturas de Agente ETL

Contiene los notebooks del **estudio comparativo de benchmark** entre tres arquitecturas de orquestación de agentes IA aplicadas al mismo pipeline ETL sobre datos del sector bananero del Ecuador.

---

## 🎯 Objetivo del Experimento

Determinar cuál arquitectura de agente produce el mejor balance entre **eficiencia de tiempo** ($M_1$), **calidad del dato** ($M_2$), **eficiencia LLM** ($M_3$), **resiliencia semántica** ($M_4$) y **estabilidad ante fallos** ($M_5$) en un pipeline ETL heterogéneo (xlsx, csv, pdf, json), bajo 3 escenarios experimentales (A: Nominal, B: Perturbación de Esquema, C: Fallo Controlado de Red) con **10 corridas por escenario (360 ejecuciones por framework, 1,080 registros totales)**.

---

## 🤖 Las Tres Arquitecturas Comparadas

| Carpeta | Framework | Descripcion & Arquitectura |
|:---|:---|:---|
| **`agente_custom/`** | **Agente Custom** (Ganador) | Agente Híbrido escrito en Python puro sin frameworks de orquestación externos. Clase `AgenteETL` con lista de tuplas `(paso, fn_paso, fn_ruta)` sobre un diccionario de estado compartido mutable. |
| **`langgraph/`** | **LangGraph** | Grafo de nodos con aristas condicionales (`StateGraph`). Estado tipado con `TypedDict`. Flujo estructurado: `lectura ➔ mapeo ➔ transformacion ➔ carga ➔ metricas`. |
| **`llamaindex/`** | **LlamaIndex Workflows** | Pipeline basado en eventos asíncronos (`Event`/`Step` decoradores con `ctx.send_event()`). Mantiene la misma estructura de métricas que LangGraph. |

Todos los experimentos utilizan el modelo **Llama 4 Maverick** (`databricks-llama-4-maverick`) sobre **Databricks** y procesan exactamente el mismo conjunto de datos pauta (**ESPAC**, **SIPA**, **FAOSTAT**, **AEBE**).

---

## 📂 Notebooks por Arquitectura

```
experimentos_comparacion/
├── agente_custom/
│   └── ESC_ETL_AgenteCustom_Banano_Experimento (10).ipynb   # (76 celdas, 0 outputs)
├── langgraph/
│   └── ESC_ETL_LangGraph_Banano_Experimento (10).ipynb     # (73 celdas, 0 outputs)
└── llamaindex/
    └── ESC_ETL_LlamaIndex_Banano_Experimento (5).ipynb       # (63 celdas, 0 outputs)
```

---

## 📊 Marco Formal de Métricas ($M_1$–$M_5$)

### Tabla 6. Métricas de Evaluación
| ID | Métrica | Unidad | Forma de Análisis |
|:---:|:---|:---:|:---|
| **M1** | **Tiempo de ejecución** | Segundos | Promedio por combinación de arquitectura y escenario |
| **M2** | **Calidad del dato** | Porcentaje ($\%$) | Promedio por combinación de arquitectura y escenario |
| **M3** | **Llamadas al LLM** | Llamadas por archivo | Promedio por combinación de arquitectura y escenario |
| **M4** | **Resiliencia semántica ante perturbación** | Porcentaje ($0$–$100\%$) | Reporte por arquitectura en Escenario B |
| **M5** | **Eficiencia de recuperación ante fallo** | Número de reintentos por corrida | Promedio por arquitectura en Escenario C |

---

### 🔍 Fórmulas y Dimensiones de Calidad

#### M2. Calidad del Dato
Evalúa completitud, validez y unicidad sobre cada registro procesado:

$$M_2 = \left( \frac{\text{registros válidos}}{\text{total filas}} \right) \times 100$$

*Dimensiones excluidas justificadamente:* Exactitud (requiere fuente independiente), Consistencia (destino único de almacenamiento) y Puntualidad (misma ventana temporal).

#### M3. Llamadas al LLM Normalizadas
$$M_3 = \frac{\sum \text{llamadas}_{\text{LLM}}}{n_{\text{archivos procesados}}}$$

---

## 📈 Hallazgos y Análisis Estadístico ()

- **Test Kruskal-Wallis:** Demostró diferencias estadísticamente significativas ($\alpha = 0.05$) en **$M_2$ Calidad del Dato** ($p = 0.003$), **$M_3$ Llamadas LLM** ($p < 0.001$) y **$M_5$ Reintentos** ($p < 0.001$).
- **Test Post-Hoc Dunn (Bonferroni):** Confirmó que el **Agente Custom** y **LlamaIndex** logran una eficiencia LLM significativamente superior ($M_3 = 0.94$ llamadas/archivo) respecto a LangGraph ($M_3 = 1.00$, $p = 0.0002$), al utilizar mapeo directo por regla para fuentes estructuradas conocidas.
- **Resiliencia Semántica ($M_4$):** LlamaIndex logró $100\%$ de resiliencia semántica al resolver el renombrado de PDFs AEBE, seguido por Agente Custom ($91.7\%$).
