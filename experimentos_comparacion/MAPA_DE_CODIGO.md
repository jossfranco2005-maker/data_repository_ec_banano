# Mapa del código de los tres notebooks

Los generadores de perturbaciones, la configuración y el cálculo de las métricas **están dentro de los notebooks** (no hay scripts `.py` independientes para ellos). Este mapa indica en qué celda está cada elemento para que pueda localizarse y auditarse. Los índices son los de `nbformat` (empiezan en 0; en Databricks/Jupyter, la celda número `i+1` contando todas las celdas).

Verificado sobre los notebooks publicados en esta carpeta (sin salidas):

- `aplicar_variacion_esquema` (perturbaciones del escenario B): **código idéntico** en los tres notebooks (misma lógica, comparada sin comentarios).
- `aplicar_fallo_controlado` (fallo del escenario C): **misma lógica** en los tres (primer intento, `random.random() < 0.5`, trunca a la mitad de los bytes; sin semilla). AgenteCustom difiere solo en el texto del mensaje impreso y en el estilo de una línea.
- `identificar_fuente`: **misma lógica** en los tres (solo difieren comentarios). La diferencia que afecta a M4 no está aquí, sino en el paso de descarga de AgenteCustom (ver abajo).

## Dónde está cada elemento

| Elemento | AgenteCustom | LangGraph | LlamaIndex |
|:--|:--:|:--:|:--:|
| Instalación de paquetes (`%pip install`, sin versiones fijas) | 5 | 6 | 6 |
| Configuración: `ESCENARIO`, catálogo/esquema/volúmenes, `FAOSTAT_*`, modelo | 8 | 8 | 8 |
| Perturbaciones: `aplicar_variacion_esquema` (B) y `aplicar_fallo_controlado` (C) | 12 | 10 | 11 |
| Registro de métricas / logs (`registrar…`, tabla `control_logs_etl`) | 8, 15 | 50 | 15, 68 |
| Paso de descarga con reintentos (máx. 3 intentos) | 17 (`paso_descargar_archivos`) | 13–15 | 15 |
| `identificar_fuente` (regla de etiquetado de fuente, M4) | 27 | 25 | 22 |
| Prefijo de archivo en la descarga (origen del etiquetado de Custom, ver abajo) | 17 | 14 | 15 |
| Transformaciones por fuente y validación de calidad (M2) | 11, 25–36 | 21–36 | 21–32 |
| Estado y orquestación del agente | 39–46 | 40–46 | 34–41 |
| Ejecutores de escenario A / B / C (10 corridas cada uno) | 54 / 56 / 58 | 52 / 54 / 56 | 43–46 (ver aviso) |
| Orquestador del experimento completo (3 × 10) | 62 | 58 | 49 |
| Métricas M1–M5 consultadas desde las tablas Delta | 65–73 | 63–71 | 53–58 |
| Exportación de resultados a Excel (opcional, posterior a la ejecución; `RUTA_EXPORT`) | 90–94 | 88–91 | 71–77 |
| Exportación a Google Drive (agente de exportación, opcional) | 78–88 | 74–85 | 59–69 |

## La diferencia concreta que afecta a M4 (AgenteCustom)

En la celda de descarga de AgenteCustom el prefijo se asigna así: `'SIPA': 'SIPA_' if 'USO' not in nombre_original.upper() else 'ESPAC_'`. El archivo SIPA de uso del suelo se guarda por tanto como `ESPAC_SIPA_USO_SUELO[_VAR].xlsx`, y `identificar_fuente`, que evalúa primero `startswith("ESPAC_")`, lo etiqueta `INEC_ESPAC`. LangGraph y LlamaIndex usan siempre `SIPA_`. Es determinista, no interviene el LLM y ocurre en A, B y C (110/120 archivos correctos), por lo que no depende de la perturbación. El procesamiento posterior y M2 no se afectan.

## Celdas que no forman parte del protocolo experimental

Se conservan sin modificar por trazabilidad; **no se ejecutaron en el lote oficial** (el consolidado solo contiene los 90 `execution_id` oficiales `…_E{A|B|C}_R01…R10`, sin sufijos `_REP` ni `_TEST`):

- **LlamaIndex, celdas 43 y 44:** ejecutores de prueba de una corrida (escenarios A y B).
- **LlamaIndex, celda 45:** «prueba dirigida» de recuperación de FAOSTAT en el escenario C (instrumenta temporalmente `requests.get` y `random.random`, y ejecuta `DELETE` en `control_descargas_fuentes`). No ejecutar entre corridas del experimento.
- **AgenteCustom, celda 48 (`R08_REP`):** corrida de reemplazo de una R08 de agosto de 2026 (`20260804_202652_EA_R08`); pertenece al experimento anterior, no al lote de noviembre.
- **Bloque 0 (celdas de reset):** vacían tablas y volúmenes; deben ejecutarse **antes de cada corrida**, no durante el análisis.
- **Exportación a Drive y a Excel:** posteriores a la ejecución; no afectan métricas.

## Limitaciones de este mapa

- No describe líneas de código una por una; solo ubica las piezas que pide la revisión (perturbaciones, configuración, métricas).
- Los números de celda cambiarán si se edita el notebook; el código de referencia es el publicado aquí (sumas SHA-256 en `../SHA256SUMS.txt`).
