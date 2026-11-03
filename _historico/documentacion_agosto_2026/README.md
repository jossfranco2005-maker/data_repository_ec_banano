# Agentes de IA para Automatización ETL en BI del Sector Bananero Ecuatoriano

*Repositorio del Trabajo de Titulación — Universidad Técnica de Machala*

> *ETL Inteligente con Agentes de IA para el Sector Bananero del Ecuador*  
> Datos: ESPAC · SIPA · FAOSTAT · AEBE

---

### Autores y Afiliación

- Joselyn K. Franco – Universidad Técnica de Machala, Ecuador
- Camilly Y. Pacheco – Universidad Técnica de Machala, Ecuador
- Bertha E. Mazon – Universidad Técnica de Machala, Ecuador
- Maritza A. Pinta – Universidad Técnica de Machala, Ecuador

---

## 🌿 ¿Qué es este proyecto?

Pipeline ETL automatizado que extrae, transforma y carga datos públicos del sector bananero ecuatoriano usando **agentes de IA** orquestados con **Llama 4 Maverick** (`databricks-llama-4-maverick`) sobre **Databricks**. El experimento compara tres arquitecturas de orquestación (**Agente Custom (Híbrido Python-LangChain)**, **LangGraph** y **LlamaIndex Workflows**) bajo un marco de métricas $M_1$–$M_5$ formalizado y homogéneo.

---

## 🏗️ Arquitectura General

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
│   ├── agente_custom/            # Agente Híbrido Python (seleccionado para producción; ver Anexo A7)
│   ├── langgraph/                # Orquestación con LangGraph + Llama 4 Maverick
│   └── llamaindex/               # Orquestación con LlamaIndex Workflows
│
└── resultados/                   # Outputs del experimento (métricas y figuras en 300 DPI)
    ├── metricas/                 # Excel de resultados (1,080 instancias de archivo) y datos corregidos
    ├── logs/                     # Registros originales de cada ejecución (finales y lotes descartados)
    ├── tablas/                   # Tablas reconstruidas por analisis/analisis_ingenius.py
    ├── anexos/                   # Anexos A1-A7 (variables, perturbaciones, fuentes, matriz)
    └── graficos/                 # Figuras regeneradas con analisis/generar_figuras.py

analisis/                         # Scripts para reconstruir tablas y figuras a partir de los registros
VERSIONES.md                      # Versión del código y del entorno usada en cada celda experimental
REPRODUCIBILIDAD.md               # Requisitos, procedimiento y límites de la reproducción
requirements.txt / requirements_notebooks.txt  # Dependencias del análisis y de los notebooks
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
| **M5** | **Recuperación ante fallo** | Reintentos por corrida (suma de las 4 fuentes, contadas una vez) | Promedio por arquitectura en Escenario C |

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
| **Puntualidad** | Todas las arquitecturas procesan los mismos archivos y la antigüedad de los datos no varía entre tratamientos, por lo que esta dimensión no discrimina entre ellos. |

Formalmente, $M_2$ se calcula como:

$$M_2 = \left( \frac{\text{registros válidos}}{\text{total filas}} \right) \times 100$$

#### 🤖 M3. Llamadas al LLM
Contabiliza las llamadas al modelo realizadas durante el procesamiento, incluyendo exitosas, fallidas y repetidas. El total se normaliza según el número de archivos procesados y se registra en el campo `m5_llamadas_api` del código (equivalencias en `resultados/anexos`, hoja A2). Solo cuenta las llamadas de la transformación:

$$M_3 = \frac{\sum \text{llamadas}_{\text{LLM}}}{n_{\text{archivos procesados}}}$$

#### 🧩 M4. Resiliencia Semántica ante Perturbación
Cuantifica el porcentaje de fuentes correctamente identificadas bajo las cuatro perturbaciones del Escenario B (renombrado de columna en ESPAC, fila vacía en SIPA, campo adicional en FAOSTAT y renombrado del PDF de AEBE). Los registros solo confirman la aplicación en AEBE y FAOSTAT (ver `resultados/anexos`, hoja A3). Se registra en el campo `fuente`.

#### 🔄 M5. Recuperación ante Fallo
Un reintento es cada nueva descarga de un archivo tras fallar el primer intento (el primero no cuenta). En el Escenario C el primer intento de cada descarga se trunca a la mitad de sus bytes con probabilidad 0.5 y se permiten hasta 3 intentos. El agente de extracción lleva el contador por fuente (`reintentos_realizados`, tabla `LOG_EXTRACCION`) y el registro por archivo lo repite en cada archivo de esa fuente; por eso **M5 suma una sola vez los reintentos de las cuatro fuentes**. El número de reintentos mide el costo de la recuperación, no su eficiencia.

---

## 🚀 Cómo Ejecutar

### Pipeline de Producción (Databricks Job)
1. Importar los 3 notebooks de `pipeline_produccion/` a tu workspace de Databricks.
2. Crear un Job con 3 tareas encadenadas:
   - `tarea_extraccion` ➔ `1_Extraccion.ipynb`
   - `tarea_transformacion` ➔ `2_Transformacion.ipynb` *(condición: `hay_nuevos == "true"`)*
   - `tarea_carga` ➔ `3_Carga.ipynb` *(condición: `status == "success"`)*
3. Configurar las credenciales de Google Drive API en `SERVICE_ACCOUNT_INFO` o `FOLDER_OUTPUT_ID`.

### Experimentos de Comparación
Cada notebook en `experimentos_comparacion/` es autocontenido. Ejecutar en orden de bloques (0 ➔ 1 ➔ 2 ➔ ... ➔ N). El Bloque 0 vacía volúmenes y tablas; en los experimentos se ejecutó antes de cada corrida (salvo LlamaIndex, escenario A; ver `VERSIONES.md`). Antes de ejecutar hay que definir las credenciales propias: `FAOSTAT_USERNAME`, `FAOSTAT_PASSWORD`, `SERVICE_ACCOUNT_INFO` y `FOLDER_OUTPUT_ID`; los notebooks traen valores de ejemplo (`secret`).

### Reconstruir tablas y figuras a partir de los registros
```bash
pip install -r requirements.txt
python analisis/analisis_ingenius.py --datos resultados/metricas/metricas_reformuladas_tesis.xlsx \
    --log-llamaindex resultados/logs/finales/experimento_llamaindex_20260807_083208.xlsx \
    --salida resultados/tablas
python analisis/generar_figuras.py --datos resultados/tablas/datos_individuales_corregidos.csv --salida resultados/graficos
```
El script corrige el total de filas de LlamaIndex (escenario A) y cuenta los reintentos una vez por fuente.

### Reproducibilidad de los notebooks
Véase [`REPRODUCIBILIDAD.md`](REPRODUCIBILIDAD.md): requisitos, procedimiento, limitaciones y las variantes `*_reproducible.ipynb` (mismo código; Google Drive opcional y versiones fijadas, `requirements_notebooks.txt`).

---

## 🔁 Notas de Reproducibilidad

- Las tres arquitecturas (Agente Custom, LangGraph, LlamaIndex) se evalúan bajo un mismo marco de métricas M1–M5, pero **no son idénticas**: difieren en la identificación de fuentes, el tratamiento de errores y, en el Escenario B, en la perturbación de LangGraph. Los resultados corresponden a las soluciones completas.
- Las arquitecturas se ejecutaron entre el 4 y el 14 de agosto de 2026, en sesiones distintas y con orden fijo (A, B, C); las comparaciones son exploratorias.
- 90 ejecuciones (3 arquitecturas x 3 escenarios x 10 repeticiones) y 1,080 instancias de archivo (12 archivos por ejecución).
- Todas las fuentes se descargan y verifican por MD5 antes de procesarse, evitando reprocesamiento innecesario.
- Las tablas finales se materializan en Delta Lake (Unity Catalog) antes de exportarse a Google Drive.

---

## 🌾 Fuentes de Datos

| Fuente | Organismo | Período | Formato |
|:---|:---|:---:|:---:|
| **ESPAC** | INEC Ecuador | 2018–2025 (8 archivos en el experimento) | xlsx |
| **SIPA** | MAG Ecuador | 2 archivos (temperatura y precipitación; uso del suelo) | xlsx / xls |
| **FAOSTAT** | FAO | API QCL (Ecuador; banano y plátano), 1990 al año de ejecución | json |
| **AEBE** | AEBE Ecuador | último boletín publicado | pdf |

---

## 💻 Requisitos

- Databricks Free Edition, cómputo serverless (versión de entorno 5)
- Dependencias del análisis: `requirements.txt`
- PySpark
- Delta Lake
- LangChain / LangGraph / LlamaIndex
- Acceso a Databricks (Unity Catalog)
- Credenciales de Google Drive API (`SERVICE_ACCOUNT_INFO`)

---

## 🧾 Datos y licencias

- **FAOSTAT:** licencia CC BY 4.0, con atribución a la FAO.
- **INEC (ESPAC):** publica con licencia Creative Commons.
- **SIPA-MAG y AEBE:** no declaran una licencia de reutilización específica (AEBE indica que el usuario es responsable de la utilización y verificación de la información).
- Los datos no contienen información personal.

## ⚠️ Limitaciones conocidas

- LlamaIndex, escenario A: tablas sin vaciar entre ejecuciones; el total de filas se corrigió con `filas_entrada`.
- PDF de AEBE en LlamaIndex: el registro indica 1 registro cargado frente a 226 esperados; no pudo reverificarse.
- Perturbaciones de ESPAC y SIPA en el Escenario B: no hay evidencia de que se aplicaran.
- El registro de reintentos consulta `LOG_EXTRACCION`; si la consulta falla, los valores quedan por defecto (0 reintentos) sin aviso.

## ⚠️ Disclaimer

Este repositorio corresponde a un trabajo de titulación con fines académicos. Los datos provienen de fuentes públicas (ESPAC, SIPA, FAOSTAT, AEBE) y se procesan únicamente con fines de investigación.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## ✉️ Contacto

Para consultas sobre replicación o uso académico:

**Joselyn K. Franco**  
jfranco9@utmachala.edu.ec  
Universidad Técnica de Machala, Ecuador

