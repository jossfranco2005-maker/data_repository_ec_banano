# Reproducibilidad

## Estado de la verificación
- **Verificación estática realizada:** los seis notebooks compilan sin errores de sintaxis, no tienen salidas guardadas ni credenciales reales (solo valores de ejemplo) y no usan nombres sin definir salvo los propios de Databricks (`spark`, `dbutils`).
- **No se ejecutaron de nuevo:** el acceso al espacio de trabajo de Databricks no está disponible. Los resultados del manuscrito se respaldan con los registros originales de `resultados/logs/`, conciliados sin diferencias con las tablas (1,080 instancias).

## Requisitos
1. **Databricks Free Edition**, cómputo serverless (versión de entorno 5) y el endpoint `databricks-llama-4-maverick` (temperatura 0).
2. **Catálogo, esquema y volúmenes:** revise `CATALOG`, `SCHEMA` y `DB_NAME` en el Bloque 2 de cada notebook (el esquema de datos es `bd_banano_ec`) y ajústelos a su espacio de trabajo.
3. **FAOSTAT:** defina `FAOSTAT_USERNAME` y `FAOSTAT_PASSWORD` con su propia cuenta.
4. **Google Drive (opcional):** solo sirve para exportar a Tableau. Los notebooks originales construyen el cliente de Drive en el Bloque 2 sin manejo de errores, por lo que fallan con credenciales de ejemplo. Use las variantes `*_reproducible.ipynb` (mismo código; Drive opcional) o defina `SERVICE_ACCOUNT_INFO` y `FOLDER_OUTPUT_ID` reales.
5. **Paquetes:** `requirements_notebooks.txt` (versiones reportadas en el manuscrito). Los originales instalan sin fijar versiones; las variantes `*_reproducible.ipynb` las fijan. Se generan con `python analisis/crear_notebooks_reproducibles.py .`.

## Procedimiento
- **Bloques:** ejecutar en orden. El Bloque 0 vacía volúmenes y tablas de datos y debe ejecutarse **antes de cada corrida**: las tablas de destino se comparten entre frameworks (columna `pipeline_framework`) y, para el mismo framework, se agregan filas (`APPEND`), por lo que sin el reset se acumulan filas entre corridas.
- **Escenario:** variable `ESCENARIO` ("A", "B" o "C") en el Bloque 2.
- **Diez corridas por escenario:** el notebook de LlamaIndex las ejecuta con `ejecutar_escenario_a/b/c` y `CORRIDAS = 10`. Los de Agente Custom y LangGraph contienen las celdas de una corrida (extracción y ETL; en Custom, la celda `R08_REP` es el ejemplo completo con reset) pero no un bucle de diez corridas; cada ejecución se identifica con un `execution_id` con marca de tiempo y el sufijo del escenario.
- **Reconstrucción de resultados sin Databricks:** véanse `README.md` y `analisis/`.

## Lo que no se reproduce de forma exacta
- Las fuentes son públicas y cambian: SIPA y AEBE se descargan de sitios vivos y los archivos de entrada no están archivados en este repositorio (`resultados/anexos/`, hoja A4, da registros y tamaños de cada uno).
- FAOSTAT consulta `1990` al año de la ejecución (`datetime.now()`).
- El truncamiento del Escenario C usa un número aleatorio sin semilla: la proporción de fallos es reproducible en distribución, no archivo por archivo.
- Python no se registró durante los experimentos; las bibliotecas auxiliares (`openpyxl`, `xlrd`, etc.) se instalaron sin fijar versión.
- El escenario A de LlamaIndex se ejecutó con una versión anterior del notebook (véase `VERSIONES.md`).
