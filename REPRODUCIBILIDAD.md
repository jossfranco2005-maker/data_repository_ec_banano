# Reproducibilidad

## Nivel demostrado
- **Reconstrucción estadística (verificada):** `python analisis/analisis_ingenius.py --estricto` recalcula M1–M5 solo desde el consolidado. Resultado actual: **35/35 verificaciones de integridad** y **25/25 contrastes** con las cifras del manuscrito. Detalle en `resultados/tablas/validacion_reproducibilidad.md`.
- **Figuras:** `python analisis/generar_figuras.py` (sin cifras escritas a mano).
- **Reproducción experimental (NO realizada de nuevo):** no se ejecutaron otra vez los notebooks ni se accedió a Databricks al preparar este repositorio.

## Requisitos de la reproducción experimental
1. Databricks Free Edition, serverless, y el endpoint `databricks-llama-4-maverick` (ver `VERSIONES.md`).
2. Catálogo, esquema y volúmenes ajustados a su espacio (Bloque 2 de cada notebook).
3. Credenciales propias de FAOSTAT (`FAOSTAT_USERNAME`, `FAOSTAT_PASSWORD`). Google Drive es opcional (solo exportación); los notebooks contienen marcadores `secret_IA` que no funcionan.
4. Paquetes: `requirements_notebooks.txt` (los notebooks instalan con `%pip` sin fijar versiones).

## Procedimiento por escenario
- Variable `ESCENARIO` ("A", "B", "C"); ejecutar los bloques en orden. El Bloque 0 vacía volúmenes y tablas y debe correr **antes de cada corrida**.
- 10 corridas por combinación; cada una con `execution_id` (marca de tiempo + `_E{A|B|C}_R{nn}`).
- Perturbaciones y fallos: ver `experimentos_comparacion/README.md` y anexo A3.

## Qué no se puede reproducir exactamente
- Las fuentes SIPA y AEBE se descargan de sitios vivos y cambian; los insumos no están archivados aquí (anexo A4: nombres, formatos, filas).
- FAOSTAT consulta hasta el año de la ejecución.
- **Truncamiento del escenario C sin semilla** (`random.random() < 0.5`): la proporción de fallos es reproducible en distribución, no archivo por archivo; no se sabe qué descargas se truncaron.
- Compute/cluster por corrida no registrado. Las versiones por framework (incluida LlamaIndex 0.14.25) provienen de la instalación de cada notebook, no de un `pip freeze` por ejecución (ver `VERSIONES.md`).
- Sin eventos de intento por archivo: no hay tasa de reintentos por archivo ni tiempo de recuperación.
- Tiempos medidos en Databricks Free, con orden no aleatorizado y efecto de orden en A (LangGraph ρ = −0,94, p_Holm = 0,0005; LlamaIndex ρ = −0,84, p_Holm = 0,018).
- La etiqueta de fuente incorrecta de Custom para el archivo SIPA de uso del suelo (M4) proviene del prefijo `ESPAC_` de su paso de descarga; corregirla exige re-ejecutar.
- M2 mide integridad/validez por reglas; no contrasta con una fuente de verdad independiente.

## Limitaciones documentadas por el script (L1–L10)
Ver hoja `Limitaciones` de `resultados/tablas/tablas_ingenius.xlsx`.

## Seguridad
Se revisaron los notebooks: sin salidas guardadas, sin credenciales reales (solo marcadores) y con correos/rutas de usuario normalizados. Verifique de nuevo antes de publicar y no suba credenciales.
