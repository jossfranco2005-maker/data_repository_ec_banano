# data_repository_ec_banano

Repositorio del **Trabajo de Titulación — Universidad Técnica de Machala**

> *ETL Inteligente con Agentes de IA para el Sector Bananero del Ecuador*  
> Datos: ESPAC · SIPA · FAOSTAT · AEBE

---

## 🌿 ¿Qué es este proyecto?

Pipeline ETL automatizado que extrae, transforma y carga datos públicos del sector bananero ecuatoriano usando **agentes de IA** orquestados con **Llama 4 Maverick** (`databricks-llama-4-maverick`) sobre **Databricks**. El experimento compara tres arquitecturas de orquestación (**Agente Custom (Híbrido Python-LangChain)**, **LangGraph** y **LlamaIndex Workflows**) bajo un marco de métricas $M_1$–$M_5$ formalizado y homogéneo.

---

## 📐 Arquitectura General

```
Fuentes públicas                 Databricks (Unity Catalog)         Destino
───────────────                 ──────────────────────────          ───────
ESPAC (xlsx/pdf)  ──┐           ┌──────────────────────────┐
SIPA  (xlsx)      ──┼── Agente  │  bd_banano_ec            │       Google Drive
FAOSTAT (csv)     ──┼──  de IA  │  ├─ dim_regiones         │  ──►  (Archivos .xlsx
AEBE (pdf/xlsx)   ──┘  └───────►│  ├─ dim_provincias       │        Deduplicados)
                                │  ├─ espac_banano_*       │
                                │  ├─ sipa_temperatura_*   │
                                │  └─ faostat_produccion_* │
                                └──────────────────────────┘
```

**Stack tecnológico:** Python · PySpark · Delta Lake · LangChain · LangGraph · LlamaIndex Workflows · Llama 4 Maverick · Google Drive API

---

## 📂 Estructura del Repositorio

```
data_repository_ec_banano/
│
├── pipeline_produccion/          # Notebooks de producción (DAG de Databricks Job)
│   ├── 1_Extraccion.ipynb        # Descarga fuentes públicas, control MD5 y control_descargas_fuentes
│   ├── 2_Transformacion.ipynb    # Limpieza, KNN inteligente, normalización y carga a Delta Lake Gold
│   └── 3_Carga.ipynb             # Exportación deduplicada a Google Drive API (.xlsx)
│
├── experimentos_comparacion/     # Material de investigación y benchmark (3 arquitecturas)
│   ├── agente_custom/            # Agente Híbrido Python (Ganador del benchmark)
│   ├── langgraph/                # Orquestación con LangGraph + Llama 4 Maverick
│   └── llamaindex/               # Orquestación con LlamaIndex Workflows
│
└── resultados/                   # Outputs del experimento (métricas y figuras en 300 DPI)
    ├── metricas/                 # Tablas de métricas consolidadas (CSV y Excel Tesis 1,080 registros)
    └── graficos/                 # Gráficos estadísticos y radar  en alta resolución
```

---

## 📊 Marco de Evaluación y Métricas ($M_1$–$M_5$)

### Tabla 6. Métricas de Evaluación
| ID | Métrica | Unidad | Forma de Análisis |
|:---:|:---|:---:|:---|
| **M1** | **Tiempo de ejecución** | Segundos | Promedio por combinación de arquitectura y escenario |
| **M2** | **Calidad del dato** | Porcentaje | Promedio por combinación de arquitectura y escenario |
| **M3** | **Llamadas al LLM** | Llamadas por archivo | Promedio por combinación de arquitectura y escenario |
| **M4** | **Resiliencia semántica ante perturbación** | Porcentaje de fuentes identificadas correctamente (0–100%) | Reporte por arquitectura en Escenario B |
| **M5** | **Eficiencia de recuperación ante fallo** | Número de reintentos HTTP por corrida | Promedio por arquitectura en Escenario C |

---

### 🔍 Definición Formal de las Métricas

#### ⏱️ M1. Tiempo de Ejecución
Mide el tiempo transcurrido desde el inicio del procesamiento hasta la persistencia exitosa en Delta Lake, expresado en segundos por archivo, y se calcula por combinación de arquitectura y escenario.

#### 🎯 M2. Calidad del Dato
La métrica $M_2$ evalúa la calidad sobre cada registro procesado considerando tres dimensiones fundamentales:

##### Tabla 7. Dimensiones consideradas para $M_2$
| Dimensión | Criterio Aplicado |
|:---|:---|
| **Completitud** | Los campos críticos (provincia, producto, período y valor numérico) deben estar presentes y sin valores nulos. |
| **Validez** | Fechas válidas dentro del período reportado, valores numéricos dentro de rangos aceptables y provincias existentes en el catálogo maestro. |
| **Unicidad** | La combinación fuente, período, provincia y producto debe ser única en el archivo; los registros duplicados se excluyen del numerador. |

##### Tabla 8. Dimensiones de calidad excluidas de $M_2$
| Dimensión | Motivo de Exclusión |
|:---|:---|
| **Exactitud** | Requeriría contrastar cada registro con una fuente de verdad independiente. |
| **Consistencia** | El flujo experimental posee un único destino de almacenamiento, por lo que no existe un segundo sistema con el cual comparar los datos. |
| **Puntualidad** | Todas las arquitecturas procesan los mismos archivos dentro de la misma ventana temporal, por lo que esta dimensión no discrimina entre tratamientos. |

Formalmente, $M_2$ se calcula como la proporción de registros que satisfacen simultáneamente completitud, validez y unicidad respecto al total de filas leídas:

$$M_2 = \left( \frac{\text{registros válidos}}{\text{total filas}} \right) \times 100$$

#### 🤖 M3. Llamadas al LLM
Contabiliza las llamadas al modelo realizadas durante el procesamiento, incluyendo exitosas, fallidas y repetidas. El total se normaliza según el número de archivos procesados y se registra en `m3_llamadas_api`. La última respuesta se conserva en `llm_response` para auditoría:

$$M_3 = \frac{\sum \text{llamadas}_{\text{LLM}}}{n_{\text{archivos procesados}}}$$

#### 🧩 M4. Resiliencia Semántica ante Perturbación
Cuantifica el porcentaje de fuentes correctamente identificadas bajo las cuatro perturbaciones estructurales del Escenario B (columna renombrada, fila vacía insertada, columna adicional y columna eliminada), como medida de robustez semántica. Se registra en `m4_resiliencia_semantica`.

#### 🔄 M5. Eficiencia de Recuperación ante Fallo
Registra el promedio de reintentos HTTP por corrida necesarios para completar la extracción en el Escenario C (simulación de fallos de red), y se registra en `m5_eficiencia_recuperacion`.

---

## 🚀 Cómo Ejecutar

### Pipeline de Producción (Databricks Job)
1. Importar los 3 notebooks de `pipeline_produccion/` a tu workspace de Databricks.
2. Crear un Job con 3 tareas encadenadas:
   - `tarea_extraccion` ➔ `1_Extraccion.ipynb`
   - `tarea_transformacion` ➔ `2_Transformacion.ipynb` *(condición: `hay_nuevos == "true"`)*
   - `tarea_carga` ➔ `3_Carga.ipynb` *(condición: `status == "success"`)*
3. Configurar las credenciales de Google Drive API en la variable global `SERVICE_ACCOUNT_INFO` o `FOLDER_OUTPUT_ID`.

### Experimentos de Comparación
Cada notebook en `experimentos_comparacion/` es autocontenido. Ejecutar en orden secuencial de bloques (0 ➔ 1 ➔ 2 ➔ ... ➔ N). El Bloque 0 es opcional (reset de prueba).

---

## 🌾 Fuentes de Datos

| Fuente | Organismo | Período | Formato |
|:---|:---|:---:|:---:|
| **ESPAC** | INEC Ecuador | 2010–2025 | xlsx / csv |
| **SIPA** | MAG Ecuador | 2015–2025 | xlsx / xls |
| **FAOSTAT** | FAO | 1990–2026 | json / csv |
| **AEBE** | AEBE Ecuador | 2010–2025 | pdf / xlsx |
