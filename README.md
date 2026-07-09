# Agentes de IA para la Automatización de Procesos ETL en Aplicaciones de BI del Sector Bananero Ecuatoriano
Manuscript ID: (pendiente)

## data_repository_ec_agro

**Trabajo de Titulación — Universidad Técnica de Machala**

### Autores y Afiliación

- Joselyn K. Franco – Universidad Técnica de Machala, Ecuador
- Camilly Y. Pacheco – Universidad Técnica de Machala, Ecuador
- Bertha E. Mazon – Universidad Técnica de Machala, Ecuador
- Maritza A. Pinta – Universidad Técnica de Machala, Ecuador

---

## 📁 Contenido del repositorio

### Estructura raíz

| Carpeta / Archivo | Descripción |
|---|---|
| `pipeline_produccion/` | Notebooks de producción (DAG de Databricks Job): extracción, transformación y carga de datos. |
| `experimentos_comparacion/` | Material de investigación que compara tres arquitecturas de orquestación de agentes de IA. |
| `resultados/` | Outputs del experimento (métricas y gráficos), no contiene código. |

### Estructura de `pipeline_produccion/`

| Carpeta / Archivo | Descripción |
|---|---|
| `pipeline_produccion/1_Extraccion.ipynb` | Descarga las fuentes públicas (ESPAC, SIPA, FAOSTAT, AEBE) y realiza control de integridad vía MD5. |
| `pipeline_produccion/2_Transformacion.ipynb` | Limpieza y normalización de los datos, carga a Delta Lake (Unity Catalog). |
| `pipeline_produccion/3_Carga.ipynb` | Exportación de las tablas finales a Google Drive en formato `.xlsx`. |

### Estructura de `experimentos_comparacion/`

| Carpeta | Descripción |
|---|---|
| `experimentos_comparacion/agente_custom/` | Agente de IA implementado en Python puro, sin frameworks de orquestación. |
| `experimentos_comparacion/langgraph/` | Orquestación del agente con LangGraph + Llama 4 Maverick. |
| `experimentos_comparacion/llamaindex/` | Orquestación del agente con LlamaIndex Workflows. |

### Estructura de `resultados/`

| Carpeta | Descripción |
|---|---|
| `resultados/metricas/` | Tablas `metricas_*` en formato `xlsx`/`csv` con los resultados M1–M5 de cada arquitectura. |
| `resultados/graficos/` | Gráficos comparativos utilizados en el artículo enviado a INGENIUS. |

---

## 🏗️ Arquitectura general

```
Fuentes públicas                 Databricks (Unity Catalog)         Destino
─────────────────               ──────────────────────────          ──────────
 ESPAC (xlsx/pdf)  ─┐           ┌──────────────────────────┐
 SIPA  (xlsx)      ─┤  Agente   │  bd_banano_ec             │       Google Drive
 FAOSTAT (csv)     ─┤  de IA    │  ├─ dim_regiones          │  →    (5 xlsx)
 AEBE (xlsx)       ─┘  ──────►  │  ├─ dim_provincias        │
                                │  ├─ espac_banano_*         │
                                │  ├─ sipa_temperatura_*     │
                                │  └─ faostat_produccion_*   │
                                └──────────────────────────┘
```

**Stack tecnológico:** Python · PySpark · Delta Lake · LangChain · LangGraph · LlamaIndex · Llama 4 Maverick (DBRX) · Google Drive API

---

## 📊 Métricas del experimento (M1–M5)

| ID | Métrica | Descripción |
|----|---------|-------------|
| M1 | Tiempo total | Segundos desde inicio hasta fin del pipeline. |
| M2 | Intervención manual | Archivos que requirieron corrección manual. |
| M3 | Recuperación de errores | Archivos procesados con éxito tras un fallo inicial. |
| M4 | Calidad del dato | Porcentaje de filas válidas tras la transformación. |
| M5 | Llamadas al LLM | Total de invocaciones al modelo durante el pipeline. |

---

## 🗂️ Fuentes de datos

| Fuente | Organismo | Período | Formato |
|--------|-----------|---------|---------|
| ESPAC | INEC Ecuador | 2010–2025 | xlsx / csv |
| SIPA | MAG Ecuador | 2000–2024 | xlsx |
| FAOSTAT | FAO | 1990–2024 | csv |
| AEBE | AEBE | 2016–2026 | pdf |

---

## ▶️ Cómo ejecutar

### Pipeline de producción (Databricks Job)

1. Importar los 3 notebooks de `pipeline_produccion/` a tu workspace de Databricks.
2. Crear un Job con 3 tareas encadenadas:
   - `tarea_extraccion` → `1_Extraccion.ipynb`
   - `tarea_transformacion` → `2_Transformacion.ipynb` *(condición: `hay_nuevos == "true"`)*
   - `tarea_carga` → `3_Carga.ipynb` *(condición: `status == "success"`)*
3. Configurar el secreto de Google Drive en `SERVICE_ACCOUNT_INFO`.

### Experimentos de comparación

Cada notebook en `experimentos_comparacion/` es autocontenido. Ejecutar en orden de bloques (0 → 1 → 2 → ... → N). El Bloque 0 es opcional (reset del entorno).

---

## 🔁 Notas de reproducibilidad

- Las tres arquitecturas (Agente Custom, LangGraph, LlamaIndex) se evalúan bajo un mismo marco de métricas M1–M5.
- Todas las fuentes se descargan y verifican por MD5 antes de procesarse, evitando reprocesamiento innecesario.
- Las tablas finales se materializan en Delta Lake (Unity Catalog) antes de exportarse a Google Drive.

## 💻 Requisitos

- Python 3.10+
- PySpark
- Delta Lake
- LangChain
- LangGraph
- LlamaIndex
- Acceso a Databricks (Unity Catalog)
- Credenciales de Google Drive API (`SERVICE_ACCOUNT_INFO`)

Las versiones exactas de las dependencias se especifican en los archivos `requirements.txt` correspondientes.

## ⚠️ Disclaimer

Este repositorio corresponde a un trabajo de titulación con fines académicos. Los datos provienen de fuentes públicas (ESPAC, SIPA, FAOSTAT, AEBE) y se procesan únicamente con fines de investigación.

## ✉️ Contacto

Para consultas sobre replicación o uso académico:

**Joselyn K. Franco**
jfranco9@utmachala.edu.ec
Universidad Técnica de Machala
Ecuador
