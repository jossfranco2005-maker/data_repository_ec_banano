# data_repository_ec_agro

Repositorio del **Trabajo de Titulación — Universidad Técnica de Machala**

> *ETL Inteligente con Agentes de IA para el Sector Bananero del Ecuador*  
> Datos: ESPAC · SIPA · FAOSTAT · AEBE

---

## ¿Qué es este proyecto?

Pipeline ETL automatizado que extrae, transforma y carga datos públicos del sector bananero ecuatoriano usando **agentes de IA** orquestados con **Llama 4 Maverick** sobre **Databricks**. El experimento compara tres arquitecturas de orquestación (Agente Custom, LangGraph, LlamaIndex) bajo un marco de métricas M1–M5 homogéneo.

---

## Arquitectura general

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

## Estructura del repositorio

```
data_repository_ec_agro/
│
├── pipeline_produccion/          # Notebooks de producción (DAG de Databricks Job)
│   ├── 1_Extraccion.ipynb        # Descarga fuentes públicas, control MD5
│   ├── 2_Transformacion.ipynb    # Limpieza, normalización, carga a Delta Lake
│   └── 3_Carga.ipynb             # Exportación a Google Drive (.xlsx)
│
├── experimentos_comparacion/     # Material de investigación (3 arquitecturas)
│   ├── agente_custom/            # Python puro, sin frameworks de orquestación
│   ├── langgraph/                # Orquestación con LangGraph + Llama 4 Maverick
│   └── llamaindex/               # Orquestación con LlamaIndex Workflows
│
├── resultados/                   # Outputs del experimento (no código)
│   ├── metricas/                 # Tablas metricas_* en xlsx/csv
│   ├── graficos/                 # Comparativas para el artículo INGENIUS
│   └── tableau/                  # Modelo star schema + observabilidad
│
├── documentacion/
│   ├── prompt_job_etl_banano.md  # Configuración del Job de Databricks
│   ├── arquitectura_llmops.md    # Diagramas LLMOps / Medallion
│   └── articulo_ingenius/        # Borradores y versión final del paper
│
└── docs/
    └── diagrama_job.png          # Captura del DAG en Databricks
```

---

## Métricas del experimento (M1–M5)

| ID | Métrica | Descripción |
|----|---------|-------------|
| M1 | Tiempo total | Segundos desde inicio hasta fin del pipeline |
| M2 | Intervención manual | Archivos que requirieron corrección manual |
| M3 | Recuperación de errores | Archivos procesados tras fallo inicial |
| M4 | Calidad del dato | % de filas válidas tras transformación |
| M5 | Llamadas al LLM | Total de invocaciones al modelo durante el pipeline |

---

## Cómo ejecutar

### Pipeline de producción (Databricks Job)

1. Importar los 3 notebooks de `pipeline_produccion/` a tu workspace de Databricks
2. Crear un Job con 3 tareas encadenadas:
   - `tarea_extraccion` → `1_Extraccion.ipynb`
   - `tarea_transformacion` → `2_Transformacion.ipynb` *(condición: `hay_nuevos == "true"`)*
   - `tarea_carga` → `3_Carga.ipynb` *(condición: `status == "success"`)*
3. Configurar el secreto de Google Drive en `SERVICE_ACCOUNT_INFO`

### Experimentos de comparación

Cada notebook en `experimentos_comparacion/` es autocontenido. Ejecutar en orden de bloques (0 → 1 → 2 → ... → N). El Bloque 0 es opcional (reset).

---

## Fuentes de datos

| Fuente | Organismo | Período | Formato |
|--------|-----------|---------|---------|
| ESPAC | INEC Ecuador | 2010–2023 | xlsx / pdf |
| SIPA | MAG Ecuador | 2015–2023 | xlsx |
| FAOSTAT | FAO | 1990–2022 | csv |
| AEBE | AEBE | 2010–2023 | xlsx |
