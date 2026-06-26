# Pipeline de Producción — ETL Banano Ecuador

Contiene los **3 notebooks de producción** que forman el DAG del Databricks Job.  
Son la versión limpia y desacoplada del pipeline, seleccionada para producción tras el estudio comparativo de arquitecturas, y lista para ejecutarse de forma autónoma y recurrente.

---

## Arquitectura seleccionada

El pipeline productivo está implementado como **Agente Custom** (Python puro, sin frameworks de orquestación externos), elegido por ser la única arquitectura que mantuvo cobertura completa de las 12 fuentes en los tres escenarios del estudio comparativo con variación de tiempo inferior al 1,4 % entre condiciones nominal y perturbada.

---

## DAG del Job

```
tarea_extraccion
      │
      ▼  (si hay_nuevos == "true")
tarea_transformacion
      │
      ▼  (si status == "success")
tarea_carga
```

La condición entre tareas se pasa mediante **Task Values** de Databricks:

| Task Value | Producido por | Consumido por |
|------------|---------------|---------------|
| `hay_nuevos` | `1_Extraccion` | `2_Transformacion` |
| `total_archivos` | `1_Extraccion` | (log / referencia) |
| `status` | `2_Transformacion` | `3_Carga` |

> El Job se programa con una expresión cron semanal (cada lunes a las 10:00, zona horaria `America/Guayaquil`). Si no hay archivos nuevos en ninguna fuente, el pipeline se detiene tras la Tarea 1 sin reportar error, evitando consumo de cómputo innecesario.

---

## Notebooks

### 📥 `1_Extraccion.ipynb`

**Tarea del Job:** `tarea_extraccion`

Descarga los archivos de las 4 fuentes públicas del sector bananero ecuatoriano usando un agente personalizado en Python puro con **Llama 4 Maverick** como LLM de decisión.

- **Fuentes:** ESPAC · SIPA · FAOSTAT · AEBE
- **Control de duplicados:** hash MD5 por archivo — solo descarga si el archivo cambió respecto a la ejecución anterior
- **Salidas:**
  - Archivos crudos en `/Volumes/workspace/default/raw_*`
  - Tabla `bd_banano_ec.control_descargas_fuentes`
- **Task Values exportados:** `hay_nuevos`, `total_archivos`

---

### ⚙️ `2_Transformacion.ipynb`

**Tarea del Job:** `tarea_transformacion`  
**Condición de ejecución:** `hay_nuevos == "true"`

Lee los archivos crudos, aplica transformaciones especializadas por fuente y carga los datos limpios en las tablas Delta de `bd_banano_ec`.

- **Tablas dimensionales:** `dim_regiones`, `dim_provincias`
- **Tablas de datos:**
  - `espac_banano_platano_provincia`
  - `espac_uso_del_suelo`
  - `sipa_temperatura_precipitacion`
  - `faostat_produccion_banano_platano`
- **LLM usado para:** mapeo archivo → tabla destino, decisión KNN de imputación
- **Task Values exportados:** `status`

---

### 💾 `3_Carga.ipynb`

**Tarea del Job:** `tarea_carga`  
**Condición de ejecución:** `status == "success"`

Lee las 5 tablas Delta limpias y las exporta a **Google Drive** como archivos `.xlsx` usando una cuenta de servicio, para su consumo posterior en Tableau Public.

- **Autenticación:** Google Service Account (JSON en variable `SERVICE_ACCOUNT_INFO`)
- **Destino:** carpeta de Drive configurada en `FOLDER_OUTPUT_ID`
- **No exporta Task Values** (es la última tarea del DAG)

---

## Librerías requeridas

```bash
# 1_Extraccion
%pip install langchain langchain-databricks beautifulsoup4 openpyxl xlrd

# 2_Transformacion
%pip install langchain langchain-databricks openpyxl xlrd numpy scikit-learn pdfplumber

# 3_Carga
%pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib openpyxl
```

> ⚠️ Cada notebook instala sus dependencias en la celda 1 (Bloque 1). Ejecutar **solo esa celda primero** y esperar el reinicio del kernel antes de continuar.

---

## Configuración mínima antes de ejecutar

> ⚠️ **Completa estos valores antes de ejecutar cualquier celda.** Los notebooks contienen marcadores `# SECRETO` y `# CONFIGURAR` en las primeras celdas. Si los ejecutas sin rellenarlos, fallarán o escribirán en rutas incorrectas de otro workspace.

| Variable | Notebook | Descripción |
|----------|----------|-------------|
| `SERVICE_ACCOUNT_INFO` | `3_Carga` | JSON completo de tu cuenta de servicio de Google (obtenido desde Google Cloud Console) |
| `FOLDER_OUTPUT_ID` | `3_Carga` | ID de la carpeta destino en tu Google Drive |
| `DB_NAME` | todos | Nombre de tu base de datos Delta en Unity Catalog |
| Rutas `/Volumes/` | `1_Extraccion`, `2_Transformacion` | Ajusta al esquema de volumen de tu workspace de Databricks |

