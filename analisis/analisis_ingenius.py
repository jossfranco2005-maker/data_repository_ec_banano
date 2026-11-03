#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analisis_ingenius.py
====================
Reconstruye, SOLO a partir del consolidado oficial de noviembre de 2026, las
estadisticas del manuscrito (M1-M5), valida su integridad y exporta tablas.

Entrada (por defecto):
    resultados/logs/finales/experimentos_3frameworks_todas_corridas_20261103_B_actualizado.xlsx

Hojas que lee:
    Logs_TODAS_1080, Extraccion_TODAS_360, Transformacion_TODAS_1080,
    Carga_TODAS_1080, Evidencia_por_Archivo_1080, P6_Archivos_Escenario_B,
    P8_Resumen_Reintentos, P9_Registro_Corridas, P10_Entorno_Corridas

Salidas (por defecto en resultados/tablas/):
    tablas_ingenius.xlsx            todas las tablas (una hoja por tabla)
    datos_ejecucion.csv             1 fila por ejecucion (90) con M1, M2, M3 y M5
    validacion_reproducibilidad.md  reporte de validacion en texto

Alcance: esto es RECONSTRUCCION DE ESTADISTICAS desde los registros. No ejecuta los
notebooks ni consulta Databricks. Si una cifra no se puede reproducir desde el
consolidado, el reporte lo indica (columna `ok` = False o seccion "no reproducible").

Definiciones operativas (alineadas con el anexo A1):
    M1  media de m1_tiempo_segundos por archivo dentro de cada ejecucion (n = 10 por
        framework y escenario); resumen = media y DE (ddof = 1) entre ejecuciones.
    M2  por archivo: filas_salida / filas_entrada x 100 (hoja Transformacion). Resumen
        principal = promedio SIMPLE de los porcentajes por archivo. El promedio
        ponderado por filas (suma salida / suma entrada) se reporta aparte.
    M3  llamadas al LLM por archivo (campo interno m5_llamadas_api de Logs).
    M4  identificacion de fuente: fuente asignada vs fuente esperada segun el nombre del
        archivo (regla en `fuente_esperada`). Se reporta por fuente y por archivo.
    M5  reintentos de descarga por ejecucion: suma de reintentos_realizados de las 4
        fuentes en Extraccion_TODAS_360 (una vez por fuente y ejecucion; no existen
        eventos de intento por archivo).
Pruebas: Kruskal-Wallis entre frameworks (por escenario) y Mann-Whitney bilateral por
pares con correccion de Holm. Familia de Holm = las 3 comparaciones por pares de cada
escenario (se agrega tambien el Holm sobre las 9 comparaciones de M1 como sensibilidad).
Los efectos de orden de ejecucion se reportan como diagnostico post hoc (Spearman entre
numero de corrida y M1; Holm sobre las 9 correlaciones).
"""
import argparse
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

RAIZ = Path(__file__).resolve().parent.parent
CONSOLIDADO = RAIZ / "resultados" / "logs" / "finales" / \
    "experimentos_3frameworks_todas_corridas_20261103_B_actualizado.xlsx"
SALIDA = RAIZ / "resultados" / "tablas"

FRAMEWORKS = ["AgenteCustom", "LangGraph", "LlamaIndex"]
ESCENARIOS = ["A", "B", "C"]
FUENTES = ["AEBE_BANANOTAS", "FAOSTAT", "INEC_ESPAC", "SIPA_MAG"]
HOJAS = ["Logs_TODAS_1080", "Extraccion_TODAS_360", "Transformacion_TODAS_1080",
         "Carga_TODAS_1080", "Evidencia_por_Archivo_1080", "P6_Archivos_Escenario_B",
         "P8_Resumen_Reintentos", "P9_Registro_Corridas", "P10_Entorno_Corridas"]

# Cifras oficiales del manuscrito (solo para CONTRASTE; los resultados se calculan de los datos)
OFICIAL_M1 = {("A", "AgenteCustom"): (14.57, 1.25), ("A", "LangGraph"): (14.73, 0.79),
              ("A", "LlamaIndex"): (15.28, 0.60), ("B", "AgenteCustom"): (14.12, 0.61),
              ("B", "LangGraph"): (12.27, 0.64), ("B", "LlamaIndex"): (14.99, 0.79),
              ("C", "AgenteCustom"): (14.59, 1.25), ("C", "LangGraph"): (15.36, 1.73),
              ("C", "LlamaIndex"): (15.24, 0.36)}
OFICIAL_KW_M1 = {"A": 0.01298, "B": 0.0000357, "C": 0.01183}
OFICIAL_M3 = {"A": 0.9167, "B": 1.0, "C": 0.9167}
OFICIAL_M4 = {"AgenteCustom": (75.0, 91.7), "LangGraph": (100.0, 100.0), "LlamaIndex": (100.0, 100.0)}
OFICIAL_M5 = {"AgenteCustom": (5.3, 1.34), "LangGraph": (5.7, 2.36), "LlamaIndex": (6.6, 1.43)}
OFICIAL_KW_M5 = 0.1866
OFICIAL_M2_SIMPLE = 98.635
OFICIAL_M2_POND = 87.2412


# --------------------------------------------------------------------------- utilidades
def holm(pvalores):
    """Correccion de Holm-Bonferroni (valores p ajustados, monotonos, tope 1)."""
    p = np.asarray(pvalores, dtype=float)
    orden = np.argsort(p)
    m = len(p)
    ajustado = np.empty(m)
    maximo = 0.0
    for k, i in enumerate(orden):
        maximo = max(maximo, (m - k) * p[i])
        ajustado[i] = min(1.0, maximo)
    return ajustado


def fuente_esperada(nombre_archivo):
    """Fuente institucional esperada segun el nombre del archivo (inventario de A4/P6).

    El orden importa: ESPAC_SIPA_USO_SUELO*.xlsx es de SIPA-MAG aunque lleve el prefijo ESPAC.
    El PDF renombrado (BANANOTAS_REPORTE_*) corresponde a AEBE.
    """
    u = str(nombre_archivo).upper()
    if "BANANOTAS" in u or u.startswith("AEBE"):
        return "AEBE_BANANOTAS"
    if "FAOSTAT" in u:
        return "FAOSTAT"
    if "SIPA" in u:
        return "SIPA_MAG"
    if "ESPAC" in u:
        return "INEC_ESPAC"
    return "DESCONOCIDA"


def cargar(ruta):
    """Lee las hojas necesarias del consolidado. Termina con un mensaje claro si falta alguna."""
    ruta = Path(ruta)
    if not ruta.exists():
        sys.exit("No se encuentra el consolidado: %s" % ruta)
    xl = pd.ExcelFile(ruta)
    faltan = [h for h in HOJAS if h not in xl.sheet_names]
    if faltan:
        sys.exit("Faltan hojas en el consolidado: %s" % ", ".join(faltan))
    d = {h: xl.parse(h) for h in HOJAS}
    for h in ["Logs_TODAS_1080", "Transformacion_TODAS_1080", "Carga_TODAS_1080",
              "Evidencia_por_Archivo_1080", "Extraccion_TODAS_360"]:
        d[h]["corrida"] = d[h]["execution_id"].str.extract(r"_R(\d+)")[0].astype(float)
    return d


# --------------------------------------------------------------------------- validacion
def validar(d):
    L, X = d["Logs_TODAS_1080"], d["Extraccion_TODAS_360"]
    T, C = d["Transformacion_TODAS_1080"], d["Carga_TODAS_1080"]
    E, P6 = d["Evidencia_por_Archivo_1080"], d["P6_Archivos_Escenario_B"]
    P9 = d["P9_Registro_Corridas"]
    filas = []

    def chk(nombre, esperado, obtenido, nota=""):
        filas.append({"verificacion": nombre, "esperado": esperado, "obtenido": obtenido,
                      "ok": bool(esperado == obtenido), "nota": nota})

    for nombre, df, n in [("Logs", L, 1080), ("Transformacion", T, 1080), ("Carga", C, 1080),
                          ("Evidencia_por_Archivo", E, 1080), ("Extraccion", X, 360)]:
        chk("Filas en %s" % nombre, n, len(df))
    for nombre, df in [("Logs", L), ("Extraccion", X), ("Transformacion", T), ("Carga", C)]:
        chk("execution_id faltantes en %s" % nombre, 0, int(df["execution_id"].isna().sum()))
    for nombre, df in [("Logs", L), ("Transformacion", T), ("Carga", C), ("Evidencia", E)]:
        chk("Duplicados (execution_id, file_name) en %s" % nombre, 0,
            int(df.duplicated(["execution_id", "file_name"]).sum()))
    chk("Duplicados (execution_id, fuente) en Extraccion", 0,
        int(X.duplicated(["execution_id", "fuente"]).sum()))
    chk("Ejecuciones distintas (Logs)", 90, L["execution_id"].nunique())
    por = L.groupby(["framework", "escenario"])["execution_id"].nunique()
    chk("10 ejecuciones por framework x escenario (9 combinaciones)", True,
        bool((por == 10).all() and len(por) == 9))
    chk("12 archivos por ejecucion", True, bool((L.groupby("execution_id").size() == 12).all()))
    chk("4 fuentes por ejecucion en Extraccion", True, bool((X.groupby("execution_id").size() == 4).all()))

    # Conciliacion entre hojas por llave (execution_id, file_name)
    def llave(df):
        return set(zip(df["execution_id"], df["file_name"]))
    chk("Mismas llaves Logs = Transformacion", True, llave(L) == llave(T))
    chk("Mismas llaves Logs = Carga", True, llave(L) == llave(C))
    chk("Mismas llaves Logs = Evidencia", True, llave(L) == llave(E))
    chk("Mismas ejecuciones Logs = Extraccion", True, set(L["execution_id"]) == set(X["execution_id"]))
    m = T.merge(E, on=["execution_id", "file_name"], suffixes=("", "_e"))
    chk("filas_entrada y filas_salida: Transformacion = Evidencia", True,
        bool((m["filas_entrada"] == m["filas_entrada_e"]).all()
             and (m["filas_salida"] == m["filas_salida_e"]).all()))
    m = T.merge(C, on=["execution_id", "file_name"], suffixes=("", "_c"))
    chk("registros_insertados (Carga) = filas_salida (Transformacion)", True,
        bool((m["filas_salida"] == m["registros_insertados"]).all()))
    chk("Escenario del execution_id coincide con la columna escenario", True,
        bool((L["execution_id"].str.extract(r"_E([ABC])_")[0] == L["escenario"]).all()))

    # Estado y errores
    chk("Filas con status ERROR (Logs)", 0, int((L["status"].astype(str).str.upper() == "ERROR").sum()))
    chk("Filas con error_message (Logs)", 0, int(L["error_message"].notna().sum()))
    w = L[L["status"] == "WARNING"].groupby(["framework", "escenario"]).size()
    chk("WARNING totales (Logs)", 80, int((L["status"] == "WARNING").sum()),
        nota="Distribucion observada: " + "; ".join("%s-%s=%d" % (f, e, n) for (f, e), n in w.items())
             + ". WARNING = advertencia de calidad, no ERROR.")

    # Lotes
    lot = L.groupby("escenario")["lote"].unique().apply(sorted)
    chk("Lote: A y C = corrida_oficial_2nov; B = corrida_oficial_3nov", True,
        bool(lot["A"] == ["corrida_oficial_2nov"] and lot["C"] == ["corrida_oficial_2nov"]
             and lot["B"] == ["corrida_oficial_3nov"]))
    chk("P9 registra el B del 2-nov como descartado", True,
        bool(P9["estado"].astype(str).str.contains("DESCARTADO").any()))

    # total_filas vs filas_entrada
    mm = L.merge(T[["execution_id", "file_name", "filas_entrada"]], on=["execution_id", "file_name"])
    disc = mm[mm["total_filas"] != mm["filas_entrada"]]
    solo_li = bool(len(disc) > 0 and set(disc["framework"]) == {"LlamaIndex"}
                   and set(disc["escenario"]) <= {"A", "C"})
    chk("Discrepancias total_filas (Logs) vs filas_entrada", 225, len(disc),
        nota="Todas en LlamaIndex A/C: %s. Para M2 se usan filas_entrada y filas_salida." % solo_li)

    # Extraccion y P6
    chk("archivos_error total en Extraccion", 0, int(X["archivos_error"].sum()))
    chk("P6: filas (12 archivos x 3 frameworks)", 36, len(P6))
    chk("P6: 10 corridas por archivo", True, bool((P6["corridas"] == 10).all()))
    chk("P6: 12 archivos por framework", True, bool(P6.groupby("framework").size().eq(12).all()))
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------- metricas
def resumen_vec(s):
    s = np.asarray(s, dtype=float)
    n = len(s)
    media = float(np.mean(s))
    de = float(np.std(s, ddof=1)) if n > 1 else float("nan")
    ic = float(stats.t.ppf(0.975, n - 1) * de / np.sqrt(n)) if n > 1 else float("nan")
    return pd.Series({"n": n, "media": media, "de": de, "mediana": float(np.median(s)),
                      "min": float(np.min(s)), "max": float(np.max(s)),
                      "ic95_inf": media - ic, "ic95_sup": media + ic})


def resumir(df, col):
    filas = []
    for (e, f), g in df.groupby(["escenario", "framework"]):
        r = resumen_vec(g[col].values)
        r["escenario"], r["framework"] = e, f
        filas.append(r)
    out = pd.DataFrame(filas)
    cols = ["escenario", "framework"] + [c for c in out.columns if c not in ("escenario", "framework")]
    return out[cols].reset_index(drop=True)


def pruebas_por_escenario(df, col, escenarios=None):
    """Kruskal-Wallis por escenario y Mann-Whitney por pares con Holm (familia = 3 pares)."""
    kw, pares = [], []
    for e in (escenarios or ESCENARIOS):
        g = [df[(df["escenario"] == e) & (df["framework"] == f)][col].values for f in FRAMEWORKS]
        if all(len(x) > 0 for x in g) and len(np.unique(np.concatenate(g))) > 1:
            h = stats.kruskal(*g)
            kw.append({"escenario": e, "H": h.statistic, "gl": 2, "p": h.pvalue})
        else:
            kw.append({"escenario": e, "H": np.nan, "gl": 2, "p": np.nan})
        fila = []
        for a, b in combinations(FRAMEWORKS, 2):
            x = df[(df["escenario"] == e) & (df["framework"] == a)][col].values
            y = df[(df["escenario"] == e) & (df["framework"] == b)][col].values
            if len(np.unique(np.concatenate([x, y]))) > 1:
                u = stats.mannwhitneyu(x, y, alternative="two-sided")
                p, U = float(u.pvalue), float(u.statistic)
            else:
                p, U = np.nan, np.nan
            fila.append({"escenario": e, "comparacion": "%s vs %s" % (a, b), "U": U, "p": p,
                         "dif_medias": float(np.mean(x) - np.mean(y)),
                         "menor_media": a if np.mean(x) < np.mean(y) else b})
        pv = np.array([f["p"] for f in fila])
        if not np.isnan(pv).any():
            for f, a_ in zip(fila, holm(pv)):
                f["p_holm_escenario"] = float(a_)
        pares.extend(fila)
    pares = pd.DataFrame(pares)
    if "p_holm_escenario" in pares.columns and not pares["p"].isna().any():
        pares["signif_holm_escenario_0.05"] = pares["p_holm_escenario"] < 0.05
    return pd.DataFrame(kw), pares


def calcular(d):
    L, X = d["Logs_TODAS_1080"].copy(), d["Extraccion_TODAS_360"]
    T, P10 = d["Transformacion_TODAS_1080"].copy(), d["P10_Entorno_Corridas"]
    P8 = d["P8_Resumen_Reintentos"]
    R = {}

    # ---- M1
    m1 = (L.groupby(["escenario", "framework", "execution_id", "corrida"])["m1_tiempo_segundos"]
          .mean().rename("m1_s_por_archivo").reset_index())
    R["M1_por_ejecucion"] = m1
    R["M1_resumen"] = resumir(m1, "m1_s_por_archivo")
    kw, pares = pruebas_por_escenario(m1, "m1_s_por_archivo")
    R["M1_kruskal"] = kw
    pares["p_holm_global_9"] = holm(pares["p"].values)   # sensibilidad: Holm sobre las 9 comparaciones
    R["M1_pares_holm"] = pares

    # ---- Efecto de orden (diagnostico post hoc)
    fil = []
    for (e, f), g in m1.groupby(["escenario", "framework"]):
        s = stats.spearmanr(g["corrida"], g["m1_s_por_archivo"])
        g = g.sort_values("corrida")
        fil.append({"escenario": e, "framework": f, "rho_spearman": float(s.statistic),
                    "p": float(s.pvalue),
                    "media_primeras_3": float(g["m1_s_por_archivo"].head(3).mean()),
                    "media_ultimas_3": float(g["m1_s_por_archivo"].tail(3).mean())})
    orden = pd.DataFrame(fil)
    orden["p_holm_9"] = holm(orden["p"].values)
    orden["signif_holm_0.05"] = orden["p_holm_9"] < 0.05
    R["M1_efecto_orden"] = orden

    # ---- Cronologia y solapamiento temporal
    L["ts"] = pd.to_datetime(L["execution_timestamp"])
    ven = (L.groupby(["escenario", "framework", "lote"])["ts"].agg(["min", "max"]).reset_index()
           .rename(columns={"min": "inicio", "max": "fin"}))
    ven["duracion_min"] = (ven["fin"] - ven["inicio"]).dt.total_seconds() / 60.0
    solapa = []
    for _, r in ven.iterrows():
        otros = ven[(ven["escenario"] == r["escenario"]) & (ven["framework"] != r["framework"])]
        s = [o["framework"] for _, o in otros.iterrows()
             if r["inicio"] < o["fin"] and o["inicio"] < r["fin"]]
        solapa.append(", ".join(s) if s else "no")
    ven["solapa_con"] = solapa
    R["Cronologia_ventanas"] = ven

    # ---- M2
    T["m2_pct_archivo"] = T["filas_salida"] / T["filas_entrada"] * 100.0
    m2_ej = (T.groupby(["escenario", "framework", "execution_id"])["m2_pct_archivo"].mean()
             .rename("m2_media_simple").reset_index())
    R["M2_por_ejecucion"] = m2_ej
    g = T.groupby(["escenario", "framework"])
    m2 = g["m2_pct_archivo"].mean().rename("m2_media_simple_pct").to_frame()
    m2["m2_de_entre_ejecuciones"] = m2_ej.groupby(["escenario", "framework"])["m2_media_simple"].std(ddof=1)
    m2["filas_entrada"] = g["filas_entrada"].sum()
    m2["filas_salida"] = g["filas_salida"].sum()
    m2["m2_ponderada_pct"] = m2["filas_salida"] / m2["filas_entrada"] * 100.0
    R["M2_resumen"] = m2.reset_index()
    gs = T.groupby(["framework", "escenario", "fuente"])
    m2f = gs["m2_pct_archivo"].mean().rename("m2_media_simple_pct").to_frame()
    m2f["archivos"] = gs.size()
    m2f["filas_entrada"] = gs["filas_entrada"].sum()
    m2f["filas_salida"] = gs["filas_salida"].sum()
    m2f["m2_ponderada_pct"] = m2f["filas_salida"] / m2f["filas_entrada"] * 100.0
    R["M2_por_fuente"] = m2f.reset_index()
    R["M2_global"] = pd.DataFrame([{
        "m2_media_simple_pct": float(T["m2_pct_archivo"].mean()),
        "m2_ponderada_pct": float(T["filas_salida"].sum() / T["filas_entrada"].sum() * 100.0),
        "nota": "Media simple = indicador principal (promedio de porcentajes por archivo). "
                "La ponderada por filas es una sensibilidad y no debe mezclarse con la simple."}])

    # ---- M3
    m3_ej = (L.groupby(["escenario", "framework", "execution_id"])["m5_llamadas_api"].mean()
             .rename("m3_llamadas_por_archivo").reset_index())
    R["M3_por_ejecucion"] = m3_ej
    m3 = L.groupby(["escenario", "framework"])["m5_llamadas_api"].mean().rename("m3_llamadas_por_archivo").to_frame()
    m3["de_entre_ejecuciones"] = m3_ej.groupby(["escenario", "framework"])["m3_llamadas_por_archivo"].std(ddof=1)
    R["M3_resumen"] = m3.reset_index()

    # ---- M4
    L["fuente_esperada"] = L["file_name"].map(fuente_esperada)
    L["correcta"] = L["fuente_esperada"] == L["fuente"]
    fil = []
    for (e, f), g in L.groupby(["escenario", "framework"]):
        por_fuente = g.groupby("fuente_esperada")["correcta"].all()
        fil.append({"escenario": e, "framework": f,
                    "fuentes_correctas": int(por_fuente.sum()), "fuentes_total": int(len(por_fuente)),
                    "m4_pct_por_fuente": float(por_fuente.mean() * 100.0),
                    "archivos_correctos": int(g["correcta"].sum()), "archivos_total": int(len(g)),
                    "m4_pct_por_archivo": float(g["correcta"].mean() * 100.0)})
    R["M4_resumen"] = pd.DataFrame(fil)
    pf = (L.groupby(["escenario", "framework", "fuente_esperada"])["correcta"].agg(["sum", "count"])
          .rename(columns={"sum": "archivos_correctos", "count": "archivos"}).reset_index())
    pf["fuente_correcta"] = pf["archivos_correctos"] == pf["archivos"]
    R["M4_por_fuente"] = pf
    R["M4_errores_detalle"] = (L[~L["correcta"]].groupby(
        ["escenario", "framework", "file_name", "fuente_esperada", "fuente"])
        .size().rename("ejecuciones").reset_index())
    aebe = L[L["fuente_esperada"] == "AEBE_BANANOTAS"]
    R["M4_AEBE_identificado"] = (aebe.groupby(["escenario", "framework", "file_name"])["correcta"]
                                 .agg(["sum", "count"]).rename(columns={"sum": "ok", "count": "ejecuciones"})
                                 .reset_index())
    R["regla_fuente_esperada"] = pd.DataFrame([
        ("1. nombre contiene BANANOTAS o empieza por AEBE", "AEBE_BANANOTAS"),
        ("2. nombre contiene FAOSTAT", "FAOSTAT"),
        ("3. nombre contiene SIPA (incluye ESPAC_SIPA_USO_SUELO*)", "SIPA_MAG"),
        ("4. nombre contiene ESPAC (resto)", "INEC_ESPAC")], columns=["regla (en este orden)", "fuente esperada"])

    # ---- M5
    m5 = (X.groupby(["escenario", "framework", "execution_id", "corrida"])["reintentos_realizados"].sum()
          .rename("m5_reintentos_por_ejecucion").reset_index())
    R["M5_por_ejecucion"] = m5
    R["M5_resumen"] = resumir(m5, "m5_reintentos_por_ejecucion")
    kw5, par5 = pruebas_por_escenario(m5, "m5_reintentos_por_ejecucion", escenarios=["C"])
    R["M5_kruskal_C"], R["M5_pares_holm_C"] = kw5, par5
    rec = []
    for (e, f), g in X.groupby(["escenario", "framework"]):
        rec.append({"escenario": e, "framework": f, "registros_fuente_ejecucion": len(g),
                    "con_reintentos": int((g["reintentos_realizados"] > 0).sum()),
                    "proporcion_con_reintento": float((g["reintentos_realizados"] > 0).mean()),
                    "reintentos_totales": int(g["reintentos_realizados"].sum()),
                    "archivos_error": int(g["archivos_error"].sum()),
                    "recuperacion_final_pct": float((g["archivos_error"] == 0).mean() * 100.0)})
    rec = pd.DataFrame(rec)
    p8 = P8[["framework", "escenario", "con_reintentos"]].rename(columns={"con_reintentos": "con_reintentos_P8"})
    rec = rec.merge(p8, on=["framework", "escenario"], how="left")
    rec["coincide_con_P8_Resumen"] = rec["con_reintentos"] == rec["con_reintentos_P8"]
    R["M5_recuperacion"] = rec.drop(columns=["con_reintentos_P8"])
    ext = (X.groupby(["escenario", "framework", "execution_id"])["tiempo_segundos"].sum()
           .rename("extraccion_s_por_ejecucion").reset_index())
    R["Extraccion_tiempo_aux"] = resumir(ext, "extraccion_s_por_ejecucion")

    # ---- Entorno
    kv = dict(zip(P10["campo"].astype(str), P10["valor"]))
    freeze = P10.loc[P10["campo"] == "pip freeze", "valor"].astype(str)
    versiones = {}
    for linea in freeze:
        if "==" in linea:
            n, v = linea.split("==", 1)
            versiones[n.strip().lower()] = v.strip()
    inst = {}   # versiones de la salida de instalacion de cada notebook (filas "Versiones instaladas ...")
    for campo, valor in zip(P10["campo"].astype(str), P10["valor"].astype(str)):
        if campo.startswith("Versiones instaladas"):
            for it in valor.split(";"):
                if "==" in it:
                    n, v = it.split("==", 1)
                    inst.setdefault(n.strip().lower(), v.strip())
    ent = [("Python", kv.get("Python", ""), "verificado" if kv.get("Python") else "no registrado"),
           ("Plataforma", kv.get("Plataforma", ""), "verificado"),
           ("Databricks Runtime", kv.get("Databricks Runtime", ""), "verificado"),
           ("Spark", kv.get("Spark", ""), "verificado"),
           ("LLM", kv.get("LLM", ""), "verificado")]
    for p in ["langgraph", "langchain", "langchain-core", "langchain-databricks", "pandas", "openpyxl",
              "xlrd", "pdfplumber", "numpy", "scikit-learn", "pyspark", "delta-spark",
              "databricks-sdk", "databricks-connect"]:
        ent.append((p, versiones.get(p, ""), "verificado (pip freeze)" if p in versiones else "NO registrado"))
    ll = sorted(n for n in versiones if n.startswith("llama"))
    if ll:
        for n in ll:
            ent.append((n, versiones[n], "verificado (pip freeze)"))
    else:
        ll_inst = sorted(n for n in inst if n.startswith("llama"))
        if ll_inst:
            for n in ll_inst:
                ent.append((n, inst[n], "registrado (instalacion del notebook, no pip freeze)"))
        else:
            for n in ["llama-index", "llama-index-core", "llama-index-workflows"]:
                ent.append((n, "", "NO VERIFICADA: ausente del pip freeze capturado; no inferir la version"))
    R["Entorno_versiones"] = pd.DataFrame(ent, columns=["componente", "version", "estado"])
    claves = [("Fecha de captura", "Fecha de captura"), ("Nota sobre el compute", "Nota sobre el compute")]
    claves += [(c, c) for c in kv if str(c).startswith("Instal")]
    R["Entorno_notas"] = pd.DataFrame([(a, str(kv.get(b, ""))) for a, b in claves], columns=["campo", "valor"])
    R["Registro_corridas_P9"] = d["P9_Registro_Corridas"]

    # ---- Datos por ejecucion (verificacion externa)
    de = (m1.merge(m2_ej, on=["escenario", "framework", "execution_id"])
          .merge(m3_ej, on=["escenario", "framework", "execution_id"])
          .merge(m5[["escenario", "framework", "execution_id", "m5_reintentos_por_ejecucion"]],
                 on=["escenario", "framework", "execution_id"]))
    de["lote"] = de["execution_id"].map(L.drop_duplicates("execution_id").set_index("execution_id")["lote"])
    R["datos_ejecucion"] = de.sort_values(["escenario", "framework", "corrida"]).reset_index(drop=True)
    return R


def contrastar(R):
    """Contrasta lo calculado con las cifras del manuscrito (`ok` = coincide al redondeo publicado)."""
    f = []

    def add(m, detalle, oficial, calculado, ok):
        f.append({"metrica": m, "detalle": detalle, "oficial": oficial, "calculado": calculado, "ok": bool(ok)})

    r1 = R["M1_resumen"].set_index(["escenario", "framework"])
    for (e, fw), (mu, de) in OFICIAL_M1.items():
        a, b = r1.loc[(e, fw), "media"], r1.loc[(e, fw), "de"]
        add("M1", "%s %s media +- DE" % (e, fw), "%.2f +- %.2f" % (mu, de), "%.2f +- %.2f" % (a, b),
            round(a, 2) == mu and round(b, 2) == de)
    for _, r in R["M1_kruskal"].iterrows():
        o = OFICIAL_KW_M1[r["escenario"]]
        add("M1", "Kruskal-Wallis %s (p)" % r["escenario"], o, "%.7g" % r["p"],
            abs(r["p"] - o) <= max(1e-5, 0.01 * o))
    m2 = R["M2_global"].iloc[0]
    add("M2", "media simple", OFICIAL_M2_SIMPLE, "%.4f" % m2["m2_media_simple_pct"],
        round(m2["m2_media_simple_pct"], 3) == OFICIAL_M2_SIMPLE)
    add("M2", "promedio ponderado por filas", OFICIAL_M2_POND, "%.4f" % m2["m2_ponderada_pct"],
        round(m2["m2_ponderada_pct"], 4) == OFICIAL_M2_POND)
    r3 = R["M3_resumen"]
    for e, o in OFICIAL_M3.items():
        v = r3[r3["escenario"] == e]["m3_llamadas_por_archivo"]
        add("M3", "escenario %s (3 frameworks)" % e, o, "%.4f" % v.mean(), bool((v.round(4) == o).all()))
    r4 = R["M4_resumen"]
    for fw, (pf, pa) in OFICIAL_M4.items():
        x = r4[(r4["escenario"] == "B") & (r4["framework"] == fw)].iloc[0]
        add("M4", "%s en B (fuente / archivo)" % fw, "%.1f / %.1f" % (pf, pa),
            "%.1f / %.1f" % (x["m4_pct_por_fuente"], x["m4_pct_por_archivo"]),
            round(x["m4_pct_por_fuente"], 1) == pf and round(x["m4_pct_por_archivo"], 1) == pa)
    r5 = R["M5_resumen"].set_index(["escenario", "framework"])
    for fw, (mu, de) in OFICIAL_M5.items():
        a, b = r5.loc[("C", fw), "media"], r5.loc[("C", fw), "de"]
        add("M5", "%s en C media +- DE" % fw, "%.1f +- %.2f" % (mu, de), "%.1f +- %.2f" % (a, b),
            round(a, 1) == mu and round(b, 2) == de)
    p5 = float(R["M5_kruskal_C"]["p"].iloc[0])
    add("M5", "Kruskal-Wallis C (p)", OFICIAL_KW_M5, "%.4f" % p5, round(p5, 4) == OFICIAL_KW_M5)
    rec = R["M5_recuperacion"]
    rc = rec[rec["escenario"] == "C"]["recuperacion_final_pct"]
    add("M5", "Recuperacion final en C (3 frameworks)", "100 %", "%.1f %%" % rc.min(), bool((rc == 100).all()))
    return pd.DataFrame(f)


def llama_en_freeze(R):
    """Versiones llama-index* registradas en P10 ('nombre==version'); vacia si no hay. Ver fuente en 'estado'."""
    ev = R["Entorno_versiones"]
    sel = ev[ev["componente"].astype(str).str.startswith("llama") & (ev["version"].astype(str) != "")]
    return ["%s==%s" % (r["componente"], r["version"]) for _, r in sel.iterrows()]


def llama_fuente(R):
    ev = R["Entorno_versiones"]
    sel = ev[ev["componente"].astype(str).str.startswith("llama") & (ev["version"].astype(str) != "")]
    return "pip freeze del compute" if sel["estado"].astype(str).str.startswith("verificado (pip freeze").all() else \
        "salida de instalacion del notebook (no pip freeze)"


def limitaciones(R):
    o = R["M1_efecto_orden"].set_index(["escenario", "framework"])
    ven = R["Cronologia_ventanas"]
    sol = ven[ven["solapa_con"] != "no"]
    txt_sol = "; ".join("%s-%s solapa con %s" % (r["escenario"], r["framework"], r["solapa_con"])
                        for _, r in sol.iterrows()) or "ninguna ventana se solapa"
    sig = o[o["signif_holm_0.05"]]
    txt_sig = ", ".join("%s-%s (rho=%.2f, p_Holm=%.4f)" % (e, f, r["rho_spearman"], r["p_holm_9"])
                        for (e, f), r in sig.iterrows()) or "ninguno"
    filas = [
        ("L1", "Orden de ejecucion no aleatorizado",
         "Cada framework x escenario se ejecuto en un bloque de 10 corridas sin intercalar. Diagnostico post hoc "
         "(Spearman corrida vs M1, Holm sobre 9): efecto de orden significativo en %s. En esos casos M1 baja con el "
         "numero de corrida, por lo que las diferencias en A pueden mezclar arquitectura y orden." % txt_sig,
         "M1_efecto_orden"),
        ("L2", "Ejecuciones solapadas en el tiempo",
         "Ventanas temporales de las corridas (execution_timestamp): %s. Si dos frameworks se ejecutaron en paralelo "
         "comparten infraestructura." % txt_sol, "Cronologia_ventanas"),
        ("L3", "Compute no vinculado a cada execution_id",
         "Las tablas de metricas no registran el cluster/compute de cada corrida. El pip freeze de P10 corresponde al "
         "compute del workspace en el momento de captura (3-nov-2026), no a cada ejecucion. No se puede reconstruir "
         "esta trazabilidad desde el consolidado.", "Entorno_notas"),
        (("L4", "Versiones de LlamaIndex registradas en P10",
          "P10 registra: %s. Fuente: %s. No corresponden a una captura por ejecucion ni a un freeze por corrida (ver L3)."
          % (", ".join(llama_en_freeze(R)), llama_fuente(R)),
          "Entorno_versiones")
         if llama_en_freeze(R) else
         ("L4", "Version de LlamaIndex no verificada en el consolidado",
          "Ni llama-index ni llama-index-workflows figuran en P10 (ni en el pip freeze ni en las filas de instalacion). "
          "No se infiere la version desde el script.",
          "Entorno_versiones")),
        ("L5", "Reintentos contados por fuente y ejecucion",
         "No hay eventos de intento por archivo; M5 se agrega por ejecucion (suma de las 4 fuentes). No se reporta una "
         "tasa de reintentos por archivo. M5 mide costo de recuperacion, no eficiencia.", "M5_recuperacion"),
        ("L6", "Fallo controlado sin semilla",
         "El truncamiento de C usa random.random() < 0.5 sin semilla en los tres notebooks: la proporcion de fallos es "
         "reproducible en distribucion, no archivo por archivo. No se puede reconstruir desde el consolidado que "
         "descargas se truncaron.", "(notebooks)"),
        ("L7", "M2 mide integridad/validez por reglas, no exactitud semantica",
         "M2 = filas_salida / filas_entrada. No contrasta contra una fuente de verdad independiente. La DE de M2 entre "
         "ejecuciones es 0, por lo que no se aplican pruebas de hipotesis.", "M2_resumen"),
        ("L8", "Filas de LlamaIndex A/C con total_filas distinto de filas_entrada",
         "225 registros del log; para M2 se usan filas_entrada y filas_salida de Transformacion.", "(Validacion)"),
        ("L9", "Implementaciones completas, no solo arquitecturas",
         "Las tres soluciones comparten los helpers de perturbacion pero difieren en identificacion de fuentes, manejo "
         "de errores y reintentos. Ejemplo verificado: Custom antepone 'ESPAC_' al archivo SIPA de uso del suelo en la descarga, por lo que "
         "identificar_fuente (misma logica en los tres) lo etiqueta INEC_ESPAC en A, B y C. Las conclusiones se limitan a las soluciones completas evaluadas.", "(notebooks)"),
        ("L10", "Estadisticos exploratorios",
         "n = 10 ejecuciones por combinacion; los 12 archivos de una ejecucion no son observaciones independientes. "
         "Kruskal-Wallis y Mann-Whitney con Holm son exploratorios.", "M1_pares_holm"),
    ]
    return pd.DataFrame(filas, columns=["id", "limitacion", "detalle", "hoja_relacionada"])


# --------------------------------------------------------------------------- exportacion
def md_tabla(df, cols=None, fmt=None):
    cols = cols or list(df.columns)
    fmt = fmt or {}
    lineas = ["| " + " | ".join(cols) + " |", "|" + "|".join([":---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        cel = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                v = (fmt.get(c, "%.4g") % v) if not pd.isna(v) else ""
            cel.append(str(v).replace("|", "/").replace("\n", " "))
        lineas.append("| " + " | ".join(cel) + " |")
    return "\n".join(lineas)


def escribir_excel(R, ruta):
    from openpyxl.styles import Alignment, Font
    with pd.ExcelWriter(ruta, engine="openpyxl") as w:
        for nombre, df in R.items():
            if nombre == "datos_ejecucion":
                continue
            df.to_excel(w, sheet_name=nombre[:31], index=False)
        for ws in w.book.worksheets:
            ws.freeze_panes = "A2"
            for c in ws[1]:
                c.font = Font(name="Arial", bold=True, size=10)
                c.alignment = Alignment(wrap_text=True, vertical="top")
            for fila in ws.iter_rows(min_row=2):
                for c in fila:
                    c.font = Font(name="Arial", size=10)
            for col in ws.columns:
                n = max(len(str(c.value)) if c.value is not None else 0 for c in col[:60])
                ws.column_dimensions[col[0].column_letter].width = min(max(10, n + 2), 70)


def escribir_reporte(R, ruta, consolidado):
    val, con = R["Validacion"], R["Comparacion_oficial"]
    out = ["# Reporte de validacion y reproducibilidad estadistica\n",
           "Archivo analizado: `%s`\n" % Path(consolidado).name,
           "**Nivel de reproducibilidad demostrado:** reconstruccion de las estadisticas a partir de los registros del "
           "consolidado. **No** se ejecutaron los notebooks ni se accedio a Databricks; la reproduccion experimental "
           "real queda pendiente (ver `REPRODUCIBILIDAD.md`).\n",
           "## 1. Verificaciones de integridad: %d/%d correctas\n" % (int(val["ok"].sum()), len(val)),
           md_tabla(val, ["verificacion", "esperado", "obtenido", "ok", "nota"]),
           "\n## 2. Contraste con las cifras oficiales del manuscrito: %d/%d coinciden\n" % (int(con["ok"].sum()), len(con)),
           md_tabla(con, ["metrica", "detalle", "oficial", "calculado", "ok"]),
           "\n## 3. Pruebas estadisticas (M1)\n",
           md_tabla(R["M1_kruskal"], ["escenario", "H", "gl", "p"], {"p": "%.7g", "H": "%.4f"}),
           "\nPares (Mann-Whitney bilateral; Holm por escenario = 3 comparaciones):\n",
           md_tabla(R["M1_pares_holm"], ["escenario", "comparacion", "p", "p_holm_escenario", "p_holm_global_9",
                                         "menor_media"], {"p": "%.5f", "p_holm_escenario": "%.5f",
                                                          "p_holm_global_9": "%.5f"}),
           "\n## 4. Efecto de orden de ejecucion (diagnostico post hoc)\n",
           md_tabla(R["M1_efecto_orden"], ["escenario", "framework", "rho_spearman", "p", "p_holm_9",
                                           "signif_holm_0.05"], {"rho_spearman": "%.3f", "p": "%.4f", "p_holm_9": "%.4f"}),
           "\n## 5. Limitaciones documentadas por el script\n",
           md_tabla(R["Limitaciones"], ["id", "limitacion", "detalle"]),
           "\n## 6. Lo que NO se puede reproducir desde el consolidado\n",
           "- Que descarga concreta se trunco en C (sin semilla ni evento por archivo).\n"
           "- Compute/cluster de cada ejecucion (no esta vinculado a execution_id).\n"
           + ("" if llama_en_freeze(R) else
              "- Version de LlamaIndex a partir del consolidado: no figura en su pip freeze "
              "(las versiones declaradas por notebook estan en VERSIONES.md).\n")
           + "- Tiempo de recuperacion e intentos por archivo (no se registraron eventos individuales).\n"
           "- Exactitud semantica de los datos transformados (M2 solo mide integridad/validez por reglas).\n"]
    Path(ruta).write_text("\n".join(out), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Reconstruye M1-M5 desde el consolidado oficial de noviembre de 2026.")
    ap.add_argument("--consolidado", default=str(CONSOLIDADO), help="ruta del consolidado oficial (.xlsx)")
    ap.add_argument("--salida", default=str(SALIDA), help="carpeta de salida de las tablas")
    ap.add_argument("--estricto", action="store_true",
                    help="termina con codigo 1 si falla alguna verificacion o contraste")
    a = ap.parse_args(argv)

    d = cargar(a.consolidado)
    R = calcular(d)
    R["Validacion"] = validar(d)
    R["Comparacion_oficial"] = contrastar(R)
    R["Limitaciones"] = limitaciones(R)
    orden = ["Validacion", "Comparacion_oficial", "M1_resumen", "M1_kruskal", "M1_pares_holm",
             "M1_efecto_orden", "Cronologia_ventanas", "M2_resumen", "M2_global", "M2_por_fuente",
             "M3_resumen", "M4_resumen", "M4_por_fuente", "M4_errores_detalle", "M4_AEBE_identificado",
             "regla_fuente_esperada", "M5_resumen", "M5_kruskal_C", "M5_pares_holm_C", "M5_recuperacion",
             "Extraccion_tiempo_aux", "M1_por_ejecucion", "M2_por_ejecucion", "M3_por_ejecucion",
             "M5_por_ejecucion", "Entorno_versiones", "Entorno_notas", "Registro_corridas_P9",
             "Limitaciones", "datos_ejecucion"]
    Ro = {k: R[k] for k in orden}

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    escribir_excel(Ro, salida / "tablas_ingenius.xlsx")
    Ro["datos_ejecucion"].to_csv(salida / "datos_ejecucion.csv", index=False, encoding="utf-8")
    escribir_reporte(Ro, salida / "validacion_reproducibilidad.md", a.consolidado)

    val, con = Ro["Validacion"], Ro["Comparacion_oficial"]
    print("Verificaciones de integridad: %d/%d OK" % (val["ok"].sum(), len(val)))
    print("Contraste con cifras oficiales: %d/%d coinciden" % (con["ok"].sum(), len(con)))
    for _, r in val[~val["ok"]].iterrows():
        print("  FALLA integridad:", r["verificacion"], "| esperado", r["esperado"], "| obtenido", r["obtenido"])
    for _, r in con[~con["ok"]].iterrows():
        print("  NO COINCIDE:", r["metrica"], r["detalle"], "| oficial", r["oficial"], "| calculado", r["calculado"])
    print("Salidas en:", salida)
    if a.estricto and (not val["ok"].all() or not con["ok"].all()):
        sys.exit(1)
    return Ro


if __name__ == "__main__":
    main()
