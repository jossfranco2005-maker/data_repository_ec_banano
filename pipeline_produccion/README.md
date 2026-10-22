# Pipeline de Producción — ETL Banano Ecuador

Contiene los **3 notebooks de producción** que forman el DAG del Databricks Job productivo.  
Son la versión limpia, modular y desacoplada del pipeline, seleccionada para producción tras el estudio comparativo de arquitecturas, y lista para ejecutarse de forma autónoma y recurrente.

---

## 🏆 Arquitectura Seleccionada

El pipeline productivo está implementado como **Agente Custom (Híbrido Python-LangChain)**, elegido por ser la arquitectura con mejor estabilidad, menor sobrecosto de orquestación y cobertura total en las 12 fuentes públicas del sector bananero ecuatoriano, manteniendo una variación de tiempo inferior al 1.4% entre condiciones nominal y perturbada.

---

## ⚙️ DAG del Job en Databricks

```
tarea_extraccion (1_Extraccion.ipynb)
      │
      ▼  (condición: hay_nuevos == "true")
tarea_transformacion (2_Transformacion.ipynb)
      │
      ▼  (condición: status == "success")
tarea_carga (3_Carga.ipynb)
```

La comunicación entre tareas del Job se gestiona mediante **Task Values** de Databricks:

| Task Value | Producido por | Consumido por | Propósito |
|:---|:---|:---|:---|
| `hay_nuevos` | `1_Extraccion` | `2_Transformacion` | Flag booleano de detección de archivos nuevos |
| `total_archivos` | `1_Extraccion` | `2_Transformacion` | Conteo de archivos descargados por hash MD5 |
| `status` | `2_Transformacion` | `3_Carga` | Confirmación de escritura exitosa en Unity Catalog |

---

## 📂 Notebooks de Producción

### 📥 1. `1_Extraccion.ipynb`
- Descarga automatizada de fuentes públicas (**ESPAC**, **SIPA**, **FAOSTAT**, **AEBE**).
- Verificación de integridad mediante hashes MD5 y tabla `control_descargas_fuentes`.
- Orquestado con **Llama 4 Maverick** (`databricks-llama-4-maverick`).

### 🔧 2. `2_Transformacion.ipynb`
- Mapeo híbrido de esquemas (reglas directas para AEBE/ESPAC conocidos + resolución LLM para dinámicos).
- Limpieza, normalización y funciones especializadas por fuente (`transformar_espac_t13_t26_mejorado_v3`, `transformar_sipa_temperatura`, `transformar_faostat`, etc.).
- Imputación KNN Inteligente supervisada con LLM y umbral del 60% para FAOSTAT.
- Limpieza de estado de error (`error_lectura: None`) al procesar PDFs de AEBE de forma exitosa.
- Carga a tablas Delta Lake en Unity Catalog Gold (`bd_banano_ec`).

### ☁️ 3. `3_Carga.ipynb`
- Deduplicación inteligente de registros de datos y métricas (`obtener_dataframe_deduplicado()`) antes de exportar a Excel/Pandas para evitar repetir filas entre años viejos y nuevos.
- Carga e integración con Google Drive API (`actualizar_archivo_drive()`) con auto-limpieza de archivos duplicados sobrantes en la carpeta destino.

---

## 📊 Marco de Métricas Aplicado ($M_1$–$M_5$)

| ID | Métrica | Unidad | Evaluación |
|:---:|:---|:---:|:---|
| **M1** | **Tiempo de ejecución** | Segundos ($s$) | Promedio por combinación de arquitectura y escenario |
| **M2** | **Calidad del dato** | Porcentaje ($\%$) | Evaluando Completitud, Validez y Unicidad: $M_2 = \frac{\text{reg. válidos}}{\text{total filas}} \times 100$ |
| **M3** | **Llamadas al LLM** | Llamadas / archivo | Invocaciones normalizadas: $M_3 = \frac{\sum \text{llamadas}}{n_{\text{archivos}}}$ |
| **M4** | **Resiliencia semántica** | Porcentaje ($0$–$100\%$) | Identificación de fuentes bajo perturbaciones en Escenario B |
| **M5** | **Recuperación ante fallo** | Reintentos / corrida | Promedio de reintentos HTTP en Escenario C |
