# Agentes de IA para automatización ETL en BI del sector bananero ecuatoriano

*Repositorio de investigación — Universidad Técnica de Machala. Material de reproducibilidad del manuscrito INGENIUS #14226 (versión revisada, noviembre de 2026).*

Datos: ESPAC (INEC) · SIPA (MAG) · FAOSTAT (FAO) · AEBE

## Autoras
Joselyn K. Franco · Camilly Y. Pacheco · Bertha E. Mazon · Maritza A. Pinta — Universidad Técnica de Machala, Ecuador.

## Qué contiene
Un pipeline ETL con agentes de IA (modelo `databricks-llama-4-maverick`) sobre Databricks, y un experimento que compara **tres implementaciones completas**: Agente híbrido Python (Custom), LangGraph y LlamaIndex Workflows. Las tres comparten helpers de perturbación y de métricas, pero **difieren** en identificación de fuentes, manejo de errores y reintentos (ver `experimentos_comparacion/README.md`). Las conclusiones se limitan a esas soluciones completas, no a la orquestación de forma aislada.

## Estructura
```
pipeline_produccion/            Notebooks de producción (1_Extraccion, 2_Transformacion, 3_Carga). No son del experimento.
experimentos_comparacion/       Los tres notebooks OFICIALES del experimento (sin salidas guardadas) + MAPA_DE_CODIGO.md
  agente_custom/ langgraph/ llamaindex/
analisis/
  analisis_ingenius.py          Reconstruye M1-M5, valida integridad y contrasta con las cifras del manuscrito
  generar_figuras.py            Genera las 5 figuras (300 DPI) desde el mismo consolidado
resultados/
  logs/finales/                 Consolidado oficial: experimentos_3frameworks_todas_corridas_20261103_B_actualizado.xlsx
  tablas/                       tablas_ingenius.xlsx, datos_ejecucion.csv (90 filas), validacion_reproducibilidad.md
  graficos/                     fig1 a fig5 (generadas por el script)
  anexos/Anexos_INGENIUS.xlsx   Anexos A1-A8 (variables, equivalencias, perturbaciones, fuentes, lotes, cronología, criterios, M2 por fuente)
_historico/                     Material de la versión enviada en agosto/octubre. OBSOLETO; ver _historico/README.md
REPRODUCIBILIDAD.md  VERSIONES.md  SHA256SUMS.txt
```

## Diseño experimental vigente
- 3 implementaciones × 3 escenarios (A nominal, B variaciones de esquema/nombre, C fallos de descarga) × 10 ejecuciones = **90 ejecuciones**; 12 archivos por ejecución = **1.080 instancias de archivo** (las instancias de una misma ejecución no son observaciones independientes; la unidad de análisis es la ejecución, n = 10 por combinación).
- A y C: lote `corrida_oficial_2nov` (2-nov-2026). B: lote `corrida_oficial_3nov` (3-nov-2026). El B del 2-nov se **descartó** porque no aplicó las perturbaciones (evidencia en el anexo A5 y en el consolidado, hoja `P9_Registro_Corridas`).
- Orden de ejecución **no aleatorizado**: cada combinación se ejecutó en un bloque de 10 corridas. En el escenario B, las ventanas de AgenteCustom y LlamaIndex se solapan en el tiempo (ver `REPRODUCIBILIDAD.md`).

## Métricas (definiciones operativas; detalle en anexo A1)
| ID | Métrica | Cálculo |
|:--|:--|:--|
| M1 | Tiempo | Media de `m1_tiempo_segundos` por archivo dentro de cada ejecución; resumen = media ± DE entre ejecuciones |
| M2 | Integridad/validez por reglas | Por archivo: `filas_salida / filas_entrada × 100`; resumen = media simple de los porcentajes por archivo. La ponderada por filas (2.374.200 / 2.721.420 = 87,24 %) se reporta aparte. **No mide exactitud semántica** |
| M3 | Llamadas al LLM | Llamadas por archivo (campo interno `m5_llamadas_api`) |
| M4 | Identificación de fuente | Fuente asignada vs. fuente esperada por nombre de archivo; se reporta por fuente (4) y por archivo (120 por framework y escenario) |
| M5 | Reintentos de descarga | Suma de `reintentos_realizados` de las 4 fuentes por ejecución. Mide el costo de recuperar, no la eficiencia |

## Resultados oficiales (reconstruidos desde el consolidado)
| | A | B | C |
|:--|:--:|:--:|:--:|
| M1 Custom (s/archivo) | 14,57 ± 1,25 | 14,12 ± 0,61 | 14,59 ± 1,25 |
| M1 LangGraph | 14,73 ± 0,79 | 12,27 ± 0,64 | 15,36 ± 1,73 |
| M1 LlamaIndex | 15,28 ± 0,60 | 14,99 ± 0,79 | 15,24 ± 0,36 |
| Kruskal-Wallis (p) | 0,01298 | 0,0000357 | 0,01183 |

- Mann-Whitney con corrección de Holm (3 pares por escenario): en A y C solo Custom–LlamaIndex es significativo; en B lo son los tres pares. No hay ganador global; LangGraph es el más rápido solo en B. Pruebas **exploratorias** (orden no aleatorizado, n = 10).
- M2: 98,635 % (media simple) en las tres implementaciones y escenarios, sin variación entre ejecuciones.
- M3: 0,9167 llamadas/archivo en A y C; 1,0000 en B, igual en las tres.
- M4 (B): Custom 3/4 fuentes (75 %) y 110/120 archivos (91,7 %); LangGraph y LlamaIndex 100 %. El error de Custom tiene causa conocida: en su paso de descarga antepone `ESPAC_` al archivo SIPA de uso del suelo (`ESPAC_SIPA_USO_SUELO*.xlsx`) y `identificar_fuente` (misma lógica en los tres notebooks; solo difieren comentarios) evalúa antes `startswith("ESPAC_")`, por lo que lo etiqueta INEC-ESPAC en vez de SIPA-MAG. Es determinista, aparece también en A y C (110/120) y no depende de la perturbación ni del LLM; el procesamiento y M2 no se afectan. El PDF de AEBE renombrado fue identificado por las tres.
- M5 (C): 5,3 ± 1,34 (Custom), 5,7 ± 2,36 (LangGraph), 6,6 ± 1,43 (LlamaIndex); Kruskal-Wallis p = 0,1866; recuperación final 100 % en las tres. No hay eventos de intento por archivo.
- 0 registros con `status = ERROR` en las 1.080 instancias; 80 `WARNING` (LangGraph: 20 en cada escenario A, B y C = 60; LlamaIndex: 20, solo en B) son advertencias de calidad, no fallos. AgenteCustom usa `PROCESADO`.

## Cómo reconstruir tablas y figuras
```bash
pip install -r requirements.txt
python analisis/analisis_ingenius.py --estricto     # 35 verificaciones de integridad + 25 contrastes con el manuscrito
python analisis/generar_figuras.py
```
Esto **reconstruye estadísticas desde los registros**; no ejecuta los notebooks ni consulta Databricks. La reproducción experimental completa requiere Databricks y está descrita (con sus límites) en [`REPRODUCIBILIDAD.md`](REPRODUCIBILIDAD.md).

## Datos y licencias
- FAOSTAT: CC BY 4.0 (atribución a la FAO). INEC-ESPAC: publica bajo Creative Commons. SIPA-MAG y AEBE: sin licencia de reutilización específica declarada; AEBE indica que el usuario es responsable de la utilización y verificación de la información.
- Todas las fuentes son públicas/institucionales; no se procesan datos personales. Los archivos de entrada no se redistribuyen aquí (el anexo A4 lista procedencia, formato, tamaño y registros).
- No se incluyen credenciales. Los notebooks contienen valores de marcador (`secret_IA`, `usuario@example.com`) que debe sustituir por los suyos.
- Revisión ética: este repositorio no declara ninguna aprobación. La declaración definitiva es la del manuscrito (pendiente de confirmar por las autoras; no se afirma una aprobación que no se haya realizado).

## Licencia
MIT. Véase [LICENSE](LICENSE).

## Contacto
Joselyn K. Franco — jfranco9@utmachala.edu.ec — Universidad Técnica de Machala, Ecuador.
