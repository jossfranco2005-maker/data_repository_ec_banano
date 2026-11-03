# Experimentos de comparación — tres implementaciones de agente ETL

Los tres notebooks de esta carpeta son los **oficiales** que respaldan el manuscrito revisado (INGENIUS #14226). Se guardan **sin salidas**; los resultados están en `../resultados/logs/finales/` (consolidado) y en `../resultados/tablas/`. Las versiones enviadas en agosto/octubre están en `../_historico/notebooks_comparacion_v1_enviado/` y son obsoletas.

| Carpeta | Implementación | Estructura |
|:--|:--|:--|
| `agente_custom/` | Agente híbrido en Python (LangChain solo para el LLM) | Clase `AgenteETL` con pasos sobre un diccionario de estado compartido |
| `langgraph/` | LangGraph | `StateGraph` con estado tipado y aristas condicionales |
| `llamaindex/` | LlamaIndex Workflows | Eventos y pasos asíncronos; funciona como notebook de referencia |

Modelo común: `databricks-llama-4-maverick` (Databricks Foundation Models). Mismo conjunto de 12 archivos por ejecución (anexo A4) y helpers de perturbación con la misma lógica en los tres notebooks (escenarios B y C).

## Qué es común y qué difiere
- **Común:** conjunto de archivos, modelo, escenarios y protocolo de perturbación, bucle de descarga con reintentos (máximo 3 intentos), esquema de logs y métricas.
- **Difiere:** el paso de descarga (el prefijo que Custom añade al nombre del archivo SIPA de uso del suelo), manejo de errores, estructura de orquestación y detalles de reintento. Ejemplo medido y explicado: Custom nombra el archivo SIPA de uso del suelo con prefijo `ESPAC_` al descargarlo (celda de descarga, `'SIPA': 'SIPA_' if 'USO' not in nombre else 'ESPAC_'`), por lo que `identificar_fuente` lo etiqueta INEC-ESPAC en A, B y C (110/120); LangGraph y LlamaIndex usan siempre `SIPA_` y lo etiquetan SIPA-MAG. No es efecto de la perturbación ni del LLM.
- Por tanto, **no se afirma equivalencia interna**: las conclusiones comparan soluciones completas, no la orquestación aislada.

**Dónde está el código de las perturbaciones, la configuración y las métricas:** dentro de los notebooks (no hay scripts independientes); ver [`MAPA_DE_CODIGO.md`](MAPA_DE_CODIGO.md), que indica la celda de cada elemento y las celdas que no forman parte del protocolo.

## Escenarios
- **A, nominal:** 12 archivos sin alteración.
- **B, variaciones:** 11 archivos con sufijo `_VAR` (8 ESPAC, 2 SIPA, 1 FAOSTAT) y el PDF de AEBE renombrado (`AEBE_BANANOTAS_<hash>.pdf` → `BANANOTAS_REPORTE_<hash>.pdf`). La evidencia consolidada confirma los nombres perturbados; las modificaciones internas se describen en el anexo A3 y en los helpers de perturbación de cada notebook.
- **C, fallos controlados:** en el primer intento de cada descarga se trunca el archivo con probabilidad 0,5 (`random.random() < 0.5`, **sin semilla**); máximo 3 intentos. Una recuperación es satisfactoria si la extracción termina con `archivos_error = 0`.

## Uso
Cada notebook es autocontenido; ejecutar los bloques en orden (0 → N). El Bloque 0 vacía volúmenes y tablas y debe ejecutarse antes de cada corrida. Variable `ESCENARIO` ("A", "B" o "C") en el Bloque 2. Defina `FAOSTAT_USERNAME`/`FAOSTAT_PASSWORD`, catálogo/esquema/volúmenes (las rutas de volúmenes de los notebooks usan, p. ej., `workspace` o `databricksbanano`; ajústelas a su espacio) y, si exporta a Drive, `SERVICE_ACCOUNT_INFO` y `FOLDER_OUTPUT_ID` (en el repo son marcadores `secret_IA`).

## Exportación de resultados (opcional)
Al final de cada notebook hay una sección «Exportación de resultados (opcional, posterior a la ejecución)» con las celdas que exportan las métricas a Excel. **No forman parte del protocolo experimental y no deben ejecutarse entre corridas.** Defina `RUTA_EXPORT` (marcador `/Volumes/<catalogo>/<esquema>/<volumen>/exports/`) antes de ejecutarla; no cambian tablas ni métricas. Nombres de hojas y columnas se mantienen porque `analisis/analisis_ingenius.py` depende de ellos. Detalle del cambio: las celdas se movieron sin modificar su lógica (solo se sustituyeron rutas por `RUTA_EXPORT`); en LlamaIndex una celda que mezclaba el helper de deduplicación con una exportación se dividió en dos. Observación: la celda «EXPORTAR MÉTRICAS ESCENARIO A» de LlamaIndex usa `archivo_salida`, que no se define en el notebook; se conserva tal cual y requiere definirla antes de ejecutarla.

## Resultados
No se duplican aquí; véase el [README principal](../README.md), `../resultados/tablas/validacion_reproducibilidad.md` y `../resultados/anexos/Anexos_INGENIUS.xlsx`.
