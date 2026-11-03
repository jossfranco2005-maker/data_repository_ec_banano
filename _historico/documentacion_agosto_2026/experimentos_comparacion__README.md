# Experimentos de Comparación — Arquitecturas de Agente ETL

Contiene los notebooks del **estudio comparativo de benchmark** entre tres arquitecturas de orquestación de agentes IA aplicadas al mismo pipeline ETL sobre datos del sector bananero del Ecuador.

---

## 🎯 Objetivo del Experimento

Determinar cuál arquitectura de agente produce el balance entre **tiempo** ($M_1$), **calidad del dato** ($M_2$), **llamadas al LLM** ($M_3$), **resiliencia semántica** ($M_4$) y **recuperación ante fallos** ($M_5$) en un pipeline ETL heterogéneo (xlsx, csv, pdf, json), bajo 3 escenarios experimentales (A: Nominal, B: Perturbación de Esquema, C: Fallo Controlado de Red) con **10 corridas por escenario (30 ejecuciones y 360 instancias de archivo por framework; 90 ejecuciones y 1,080 instancias en total)**.

---

## 🤖 Las Tres Arquitecturas Comparadas

| Carpeta | Framework | Descripcion & Arquitectura |
|:---|:---|:---|
| **`agente_custom/`** | **Agente Custom** (seleccionado para producción) | Agente Híbrido escrito en Python puro sin frameworks de orquestación externos. Clase `AgenteETL` con lista de tuplas `(paso, fn_paso, fn_ruta)` sobre un diccionario de estado compartido mutable. |
| **`langgraph/`** | **LangGraph** | Grafo de nodos con aristas condicionales (`StateGraph`). Estado tipado con `TypedDict`. Flujo estructurado: `lectura ➔ mapeo ➔ transformacion ➔ carga ➔ metricas`. |
| **`llamaindex/`** | **LlamaIndex Workflows** | Pipeline basado en eventos asíncronos (`Event`/`Step` decoradores con `ctx.send_event()`). Mantiene la misma estructura de métricas que LangGraph. |

Todos los experimentos utilizan el modelo **Llama 4 Maverick** (`databricks-llama-4-maverick`) sobre **Databricks** y procesan exactamente el mismo conjunto de datos pauta (**ESPAC**, **SIPA**, **FAOSTAT**, **AEBE**).

---

## 📂 Notebooks por Arquitectura

```
experimentos_comparacion/
├── agente_custom/
│   └── ESC_ETL_AgenteCustom_Banano_Experimento.ipynb   # (77 celdas, 0 outputs)
├── langgraph/
│   └── ESC_ETL_LangGraph_Banano_Experimento.ipynb     # (73 celdas, 0 outputs)
└── llamaindex/
    └── ESC_ETL_LlamaIndex_Banano_Experimento.ipynb       # (70 celdas, 0 outputs)
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
| **M5** | **Recuperación ante fallo** | Reintentos por corrida (una vez por fuente) | Promedio por arquitectura en Escenario C |

---

### 🔍 Fórmulas y Dimensiones de Calidad

#### M2. Calidad del Dato
Evalúa completitud, validez y unicidad sobre cada registro procesado:

$$M_2 = \left( \frac{\text{registros válidos}}{\text{total filas}} \right) \times 100$$

*Dimensiones excluidas justificadamente:* Exactitud (requiere fuente independiente), Consistencia (destino único de almacenamiento) y Puntualidad (misma ventana temporal).

#### M3. Llamadas al LLM Normalizadas
$$M_3 = \frac{\sum \text{llamadas}_{\text{LLM}}}{n_{\text{archivos procesados}}}$$

---

## 📈 Hallazgos y análisis estadístico (exploratorio)

La unidad de análisis es la ejecución (n = 10 por combinación); los 12 archivos de una ejecución no son observaciones independientes. Las pruebas (Mann-Whitney, Kruskal-Wallis y corrección de Holm) son exploratorias porque las arquitecturas se ejecutaron en sesiones distintas y sin aleatorizar el orden. Las figuras se regeneran con `analisis/generar_figuras.py`.

- **M1 (tiempo del ETL por archivo):** LangGraph fue más rápida que las otras dos en A y B (p de Holm entre 0.003 y 0.036) y LlamaIndex Workflows en C. M1 no incluye la extracción, por lo que no refleja el costo de los reintentos del Escenario C.
- **M2 (calidad):** equivalente (98.63 % sin el PDF de AEBE en las tres); idéntica en todas las ejecuciones y escenarios.
- **M3 (llamadas al LLM):** 0.92 llamadas por archivo en el Agente Custom y LlamaIndex Workflows frente a 1.00 en LangGraph (escenario A).
- **M4 (resiliencia semántica):** LlamaIndex Workflows identificó correctamente el PDF renombrado de AEBE (100 % de las fuentes); Agente Custom y LangGraph lo clasificaron como DESCONOCIDA (75 %).
- **M5 (recuperación):** 100 % de recuperación en las tres; 4.6, 5.8 y 5.5 reintentos por corrida, cercanos a los 6 esperados por diseño y sin diferencias distinguibles del azar (Kruskal-Wallis, p = 0.20).
