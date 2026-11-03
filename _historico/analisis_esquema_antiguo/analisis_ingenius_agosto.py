#!/usr/bin/env python3
"""
analisis_ingenius.py
====================
Reconstruye, a partir de los datos por archivo (hoja 7_Datos_Individuales),
las tablas que pide la revision de INGENIUS (obs. 2, 4, 5, 6, 11):

  1. Datos corregidos (LlamaIndex, escenario A) y registro de correcciones.
  2. Tabla por EJECUCION (unidad de analisis, n=10 por arquitectura x escenario).
  3. Estadistica descriptiva por celda: media, DE, min, max, IC95% (t de Student).
  4. M2 (calidad) por fuente, con dos definiciones: media simple de porcentajes
     por archivo (la del manuscrito) y ponderada por filas; mas sensibilidad
     sin el PDF de AEBE.
  5. M5 (reintentos) contados UNA VEZ POR FUENTE (el registro por archivo repite
     el contador de la fuente), con indicadores complementarios, y prueba de deriva
     temporal entre corridas (efecto de tablas sin vaciar / calentamiento).
  6. Comparaciones entre arquitecturas (Mann-Whitney, correccion de Holm,
     tamano de efecto rank-biserial). Son EXPLORATORIAS: las arquitecturas se
     ejecutaron en sesiones distintas y sin aleatorizar el orden.

Uso:
  python analisis_ingenius.py \
      --datos metricas_reformuladas_tesis.xlsx \
      --log-llamaindex experimento_llamaindex_20260807_083208.xlsx \
      --salida resultados_ingenius

Dependencias: pandas, numpy, scipy, openpyxl.
"""
import argparse
import itertools
import os

import numpy as np
import pandas as pd
from scipy import stats

HOJA = "7_Datos_Individuales"
CELDA = ["Arquitectura", "Escenario"]
EXITO = {"PROCESADO", "OK", "WARNING"}  # estados que NO son fallo de archivo


def fuente_extraccion(archivo):
    """Fuente (volumen) a la que pertenece el archivo. El contador de reintentos
    se lleva POR FUENTE en el agente de extraccion y luego se copia a cada
    archivo de esa fuente en el registro por archivo; hay que contarlo una vez."""
    u = str(archivo).upper()
    if "FAOSTAT" in u:
        return "FAOSTAT"
    if "BANANOTAS" in u:
        return "AEBE"
    if "SIPA" in u and "ESPAC_TAB" not in u:
        return "SIPA"
    return "ESPAC"


# --------------------------------------------------------------------------
# 1. Carga y correccion
# --------------------------------------------------------------------------
def cargar(path):
    d = pd.read_excel(path, sheet_name=HOJA)
    req = {"Arquitectura", "Escenario", "Corrida_ID", "Archivo", "Fuente",
           "M1_Tiempo_s", "M2_Calidad_Pct", "M3_LLM_Calls", "Reintentos",
           "Total_Filas", "Registros_Validos", "Status"}
    faltan = req - set(d.columns)
    if faltan:
        raise SystemExit(f"Faltan columnas en {HOJA}: {sorted(faltan)}")
    d["FuenteExtraccion"] = d.Archivo.map(fuente_extraccion)
    return d


def corregir_llamaindex_A(d, log_path):
    """Total_Filas de LlamaIndex A venia de Logs_Generales.total_filas, que
    es un conteo acumulado de la tabla destino (identico en las 10 corridas).
    Se sustituye por filas_entrada de Metricas_Transformacion (medido por
    archivo y por ejecucion). Reintentos (vacio) se completa desde
    Metricas_Extraccion solo si todas las filas de A registran 0."""
    cambios = []
    if not log_path:
        return d, pd.DataFrame(columns=["campo", "detalle"])
    x = pd.ExcelFile(log_path)
    tr = x.parse("Metricas_Transformacion")[["execution_id", "file_name", "filas_entrada"]]
    ex = x.parse("Metricas_Extraccion")
    mask = (d.Arquitectura == "LlamaIndex") & (d.Escenario == "A")
    sub = d[mask].merge(tr, left_on=["Corrida_ID", "Archivo"],
                        right_on=["execution_id", "file_name"], how="left")
    if sub.filas_entrada.isna().any():
        raise SystemExit("No todas las filas de LlamaIndex A cruzan con el log "
                         "(revisar Corrida_ID / nombre de archivo).")
    antes = d.loc[mask, "Total_Filas"].to_numpy()
    d.loc[mask, "Total_Filas"] = sub.filas_entrada.to_numpy()
    cambios.append(("Total_Filas",
                    f"LlamaIndex A: {int((antes != sub.filas_entrada.to_numpy()).sum())} "
                    f"de {mask.sum()} filas reemplazadas por filas_entrada del log original"))
    # chequeo: el porcentaje no cambia
    q = d.loc[mask, "Registros_Validos"] / d.loc[mask, "Total_Filas"] * 100
    dif = (q - d.loc[mask, "M2_Calidad_Pct"]).abs().max()
    cambios.append(("Chequeo M2", f"max |validos/filas_entrada*100 - M2| = {dif:.4f}"))
    # reintentos
    ea = ex[ex.execution_id.str.contains("_EA_")]
    if d.loc[mask, "Reintentos"].isna().all() and (ea.reintentos_realizados == 0).all():
        d.loc[mask, "Reintentos"] = 0
        cambios.append(("Reintentos",
                        f"LlamaIndex A: 0 (Metricas_Extraccion, {len(ea)} filas, todas 0)"))
    return d, pd.DataFrame(cambios, columns=["campo", "detalle"])


# --------------------------------------------------------------------------
# 2. Tabla por ejecucion
# --------------------------------------------------------------------------
def por_ejecucion(d):
    g = d.groupby(CELDA + ["Corrida_ID"])
    r = g.agg(archivos=("Archivo", "size"),
              tiempo_total_s=("M1_Tiempo_s", "sum"),
              calidad_media_archivos_pct=("M2_Calidad_Pct", "mean"),
              validos=("Registros_Validos", "sum"),
              filas=("Total_Filas", "sum"),
              llamadas_llm=("M3_LLM_Calls", "sum"),
              reintentos_sumados_por_archivo=("Reintentos", "sum")).reset_index()
    r["calidad_ponderada_pct"] = r.validos / r.filas * 100
    # M5 correcto: el contador es por fuente; se toma una vez por fuente y se suma
    por_fuente = (d.groupby(CELDA + ["Corrida_ID", "FuenteExtraccion"]).Reintentos
                  .max().reset_index())
    chk = d.groupby(CELDA + ["Corrida_ID", "FuenteExtraccion"]).Reintentos.nunique()
    if (chk > 1).any():
        print("AVISO: hay fuentes con valores de reintentos distintos entre sus archivos.")
    m5r = (por_fuente.groupby(CELDA + ["Corrida_ID"]).Reintentos.sum()
           .rename("reintentos").reset_index())
    fr = (por_fuente.assign(c=por_fuente.Reintentos.fillna(0) > 0)
          .groupby(CELDA + ["Corrida_ID"]).c.sum().rename("fuentes_con_reintento").reset_index())
    return r.merge(m5r, on=CELDA + ["Corrida_ID"]).merge(fr, on=CELDA + ["Corrida_ID"])


def descriptiva(r, columnas):
    filas = []
    for (a, e), t in r.groupby(CELDA):
        for c in columnas:
            v = t[c].astype(float)
            n = len(v)
            sd = v.std(ddof=1)
            h = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n) if n > 1 else np.nan
            filas.append(dict(Arquitectura=a, Escenario=e, metrica=c, n_ejecuciones=n,
                              media=v.mean(), DE=sd, minimo=v.min(), maximo=v.max(),
                              IC95_inf=v.mean() - h, IC95_sup=v.mean() + h))
    return pd.DataFrame(filas)


def fuente_verdad(archivo):
    """Fuente correcta segun el diseno: ambos archivos SIPA (temperatura y uso de
    suelo) pertenecen a SIPA-MAG, aunque el de uso de suelo cite a ESPAC en su cabecera."""
    f = fuente_extraccion(archivo)
    return {"ESPAC": "INEC_ESPAC", "SIPA": "SIPA_MAG", "FAOSTAT": "FAOSTAT", "AEBE": "AEBE_BANANOTAS"}[f]


def identificacion_fuente(d):
    """Proporcion de archivos con la fuente correcta (a nivel de archivo)."""
    t = d.assign(correcta=d.Fuente == d.Archivo.map(fuente_verdad))
    g = t.groupby(CELDA).agg(archivos=("Archivo", "size"),
                             correctos=("correcta", "sum")).reset_index()
    g["pct_correcto"] = g.correctos / g.archivos * 100
    return g


# --------------------------------------------------------------------------
# 3. M2 por fuente y sensibilidad
# --------------------------------------------------------------------------
def m2_por_fuente(d):
    g = d.groupby(CELDA + ["Fuente"])
    t = g.agg(archivos=("Archivo", "size"),
              M2_media_simple_pct=("M2_Calidad_Pct", "mean"),
              validos=("Registros_Validos", "sum"),
              filas=("Total_Filas", "sum")).reset_index()
    t["M2_ponderada_pct"] = t.validos / t.filas * 100
    t["registros_por_archivo"] = t.filas / t.archivos
    return t


def m2_sensibilidad(d):
    out = []
    for nombre, sub in [("Todos los archivos", d),
                        ("Sin PDF AEBE", d[~d.Fuente.str.contains("AEBE", case=False, na=False)])]:
        g = sub.groupby(CELDA + ["Corrida_ID"]).M2_Calidad_Pct.mean().reset_index()
        t = g.groupby(CELDA).M2_Calidad_Pct.agg(["mean", "std"]).reset_index()
        t.insert(0, "conjunto", nombre)
        out.append(t.rename(columns={"mean": "M2_media_pct", "std": "DE_entre_ejecuciones"}))
    return pd.concat(out, ignore_index=True)


# --------------------------------------------------------------------------
# 4. M5: reintentos e indicadores complementarios
# --------------------------------------------------------------------------
def m5(d):
    """Reintentos a nivel de FUENTE (una observacion por fuente y ejecucion)."""
    pf = (d.groupby(CELDA + ["Corrida_ID", "FuenteExtraccion"])
          .agg(reintentos=("Reintentos", "max"),
               todos_ok=("Status", lambda s: bool(s.isin(EXITO).all()))).reset_index())
    filas = []
    for (a, e), t in pf.groupby(CELDA):
        con = t[t.reintentos.fillna(0) > 0]
        rec = con[con.todos_ok]
        filas.append(dict(
            Arquitectura=a, Escenario=e, ejecuciones=t.Corrida_ID.nunique(),
            fuentes_con_reintento=len(con), observaciones_fuente=len(t),
            reintentos_totales=t.reintentos.sum(),
            reintentos_por_ejecucion=t.reintentos.sum() / t.Corrida_ID.nunique(),
            reintentos_por_fuente_afectada=(con.reintentos.mean() if len(con) else np.nan),
            max_reintentos_en_una_fuente=t.reintentos.max(),
            tasa_recuperacion_pct=(len(rec) / len(con) * 100 if len(con) else np.nan),
            fuentes_no_recuperadas=len(con) - len(rec)))
    return pd.DataFrame(filas)


def m5_por_fuente(d):
    pf = (d.groupby(CELDA + ["Corrida_ID", "FuenteExtraccion"]).Reintentos.max().reset_index())
    t = pf.groupby(CELDA + ["FuenteExtraccion"]).Reintentos.agg(["mean", "std", "max"]).reset_index()
    return t.rename(columns={"mean": "media_por_ejecucion", "std": "DE", "max": "maximo"})


def deriva(r, d):
    """Si las tablas de destino no se vaciaran entre corridas, esperariamos
    tiempos crecientes (rho > 0) o registros duplicados. Spearman entre el
    orden de la corrida (R01..R10) y el tiempo total por ejecucion."""
    r = r.copy()
    r["orden"] = r.Corrida_ID.str.extract(r"_R(\d+)")[0].astype(int)
    filas = []
    for (a, e), t in r.groupby(CELDA):
        rho, p = stats.spearmanr(t.orden, t.tiempo_total_s)
        filas.append(dict(Arquitectura=a, Escenario=e, n=len(t),
                          rho_Spearman=rho, p=p,
                          tiempo_medio_R01_R03=t[t.orden <= 3].tiempo_total_s.mean(),
                          tiempo_medio_R08_R10=t[t.orden >= 8].tiempo_total_s.mean()))
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# 5. Comparaciones (exploratorias)
# --------------------------------------------------------------------------
def holm(p):
    p = np.asarray(p, float)
    o = np.argsort(p)
    aj = np.empty_like(p)
    prev = 0.0
    for rank, i in enumerate(o):
        prev = max(prev, (len(p) - rank) * p[i])
        aj[i] = min(1.0, prev)
    return aj


def comparaciones(r, metricas):
    filas = []
    for m in metricas:
        for e, t in r.groupby("Escenario"):
            arqs = sorted(t.Arquitectura.unique())
            grupos = {a: t.loc[t.Arquitectura == a, m].astype(float).to_numpy() for a in arqs}
            todos = np.concatenate(list(grupos.values()))
            kw_p = stats.kruskal(*grupos.values()).pvalue if np.ptp(todos) > 0 else np.nan
            for a, b in itertools.combinations(arqs, 2):
                x, y = grupos[a], grupos[b]
                try:
                    u, p = stats.mannwhitneyu(x, y, alternative="two-sided")
                    rb = 2 * u / (len(x) * len(y)) - 1
                except ValueError:  # todos los valores iguales
                    u, p, rb = np.nan, 1.0, 0.0
                filas.append(dict(metrica=m, Escenario=e, A=a, B=b,
                                  mediana_A=np.median(x), mediana_B=np.median(y),
                                  U=u, p_sin_ajustar=p, rank_biserial=rb,
                                  Kruskal_p_escenario=kw_p))
    t = pd.DataFrame(filas)
    t["p_Holm"] = np.nan
    for m, idx in t.groupby("metrica").groups.items():  # Holm dentro de cada metrica
        t.loc[idx, "p_Holm"] = holm(t.loc[idx, "p_sin_ajustar"])
    return t


# --------------------------------------------------------------------------
# Salida
# --------------------------------------------------------------------------
def guardar(path_xlsx, hojas):
    from openpyxl.styles import Font
    with pd.ExcelWriter(path_xlsx, engine="openpyxl") as w:
        for nombre, df in hojas.items():
            df.to_excel(w, sheet_name=nombre[:31], index=False)
            ws = w.sheets[nombre[:31]]
            for c in ws[1]:
                c.font = Font(name="Arial", bold=True)
            for row in ws.iter_rows(min_row=2):
                for c in row:
                    c.font = Font(name="Arial")
                    if isinstance(c.value, float):
                        c.number_format = "0.00"
            for col in ws.columns:
                ancho = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(10, ancho + 2), 60)
            ws.freeze_panes = "A2"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", required=True, help="Excel con la hoja 7_Datos_Individuales")
    ap.add_argument("--log-llamaindex", default=None, help="Log original de LlamaIndex (correccion de A)")
    ap.add_argument("--salida", default="resultados_ingenius", help="Prefijo/carpeta de salida")
    a = ap.parse_args()

    os.makedirs(a.salida, exist_ok=True)
    d = cargar(a.datos)
    d, correcciones = corregir_llamaindex_A(d, a.log_llamaindex)
    r = por_ejecucion(d)

    metr = ["tiempo_total_s", "calidad_media_archivos_pct", "calidad_ponderada_pct",
            "llamadas_llm", "reintentos"]
    hojas = {
        "Correcciones": correcciones,
        "Por_ejecucion": r,
        "Descriptiva": descriptiva(r, metr),
        "M2_por_fuente": m2_por_fuente(d),
        "M2_sensibilidad": m2_sensibilidad(d),
        "M5_recuperacion": m5(d),
        "M5_por_fuente": m5_por_fuente(d),
        "Comparaciones": comparaciones(r, ["tiempo_total_s", "reintentos"]),
        "Deriva_tiempos": deriva(r, d),
        "Identificacion_fuente": identificacion_fuente(d),
        "Conteos": d.groupby(CELDA).agg(ejecuciones=("Corrida_ID", "nunique"),
                                        instancias_archivo=("Archivo", "size")).reset_index(),
    }
    guardar(os.path.join(a.salida, "tablas_ingenius.xlsx"), hojas)
    d.to_csv(os.path.join(a.salida, "datos_individuales_corregidos.csv"), index=False)
    print("Listo:", os.path.join(a.salida, "tablas_ingenius.xlsx"))
    print(correcciones.to_string(index=False))


if __name__ == "__main__":
    main()
