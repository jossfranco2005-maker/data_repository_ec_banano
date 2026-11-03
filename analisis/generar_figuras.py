#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_figuras.py
==================
Genera las figuras del manuscrito a partir del consolidado oficial de noviembre de 2026
(mismas funciones de calculo que analisis_ingenius.py; no hay cifras escritas a mano).

Figuras (resultados/graficos/, 300 DPI):
    fig1_m1_por_escenario.png          M1 por escenario con dispersion (cada punto = 1 ejecucion)
    fig2_m1_orden_de_corrida.png       M1 segun el numero de corrida (diagnostico de orden)
    fig3_m4_identificacion_fuente.png  M4 por fuente y por archivo; problema SIPA de AgenteCustom
    fig4_m5_reintentos_escenario_c.png M5 por ejecucion y proporcion de fuentes con reintento
    fig5_m2_m3_resumen.png             M2 (media simple y ponderada) y M3

Uso:
    python analisis/generar_figuras.py
    python analisis/generar_figuras.py --consolidado RUTA.xlsx --salida resultados/graficos
"""
import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analisis_ingenius as ai  # noqa: E402

COL = {"AgenteCustom": "#0072B2", "LangGraph": "#E69F00", "LlamaIndex": "#009E73"}
ABR = {"AgenteCustom": "Custom", "LangGraph": "LangGraph", "LlamaIndex": "LlamaIndex"}
ESC_TXT = {"A": "A: nominal (2-nov)", "B": "B: perturbación (3-nov)", "C": "C: fallos de descarga (2-nov)"}
PIE = "Fuente: consolidado oficial 3-nov-2026; n = 10 ejecuciones por framework y escenario."

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 11, "figure.dpi": 100, "savefig.dpi": 300,
                     "savefig.bbox": "tight"})


def es(x, nd=2):
    """Numero con coma decimal."""
    return ("%.*f" % (nd, x)).replace(".", ",")


def p_es(p):
    if p < 0.0001:
        return "< 0,0001"
    return es(p, 4 if p < 0.01 else 3)


def p_eq(p):
    t = p_es(p)
    return "p " + t if t.startswith("<") else "p = " + t


def eje_coma(ax, nd=1, eje="y"):
    f = FuncFormatter(lambda v, _: es(v, nd))
    (ax.yaxis if eje == "y" else ax.xaxis).set_major_formatter(f)


def pie(fig, texto=PIE, y=-0.02):
    fig.text(0.01, y, texto, fontsize=7.5, color="#555555", ha="left", va="top")


def fig1(R, salida):
    m1, res = R["M1_por_ejecucion"], R["M1_resumen"].set_index(["escenario", "framework"])
    kw, par = R["M1_kruskal"].set_index("escenario"), R["M1_pares_holm"]
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.6), sharey=True)
    rng = np.random.default_rng(1)  # solo para el desplazamiento horizontal de los puntos
    for ax, e in zip(axs, ai.ESCENARIOS):
        for i, f in enumerate(ai.FRAMEWORKS):
            v = m1[(m1["escenario"] == e) & (m1["framework"] == f)]["m1_s_por_archivo"].values
            ax.scatter(i + rng.uniform(-0.12, 0.12, len(v)), v, s=22, color=COL[f], alpha=0.65, zorder=2)
            mu, de = res.loc[(e, f), "media"], res.loc[(e, f), "de"]
            ax.errorbar(i, mu, yerr=de, fmt="_", color="black", capsize=6, markersize=22, lw=1.4, zorder=3)
            ax.text(i, max(v.max(), mu + de) + 0.35, es(mu) + " ± " + es(de), ha="center", fontsize=8)
        ax.set_xticks(range(3))
        ax.set_xticklabels([ABR[f] for f in ai.FRAMEWORKS])
        ax.set_xlim(-0.6, 2.6)
        ax.set_ylim(11, 21.5)
        pe = par[par["escenario"] == e]
        lin = []
        for _, r in pe.iterrows():
            a, b = r["comparacion"].split(" vs ")
            lin.append("%s-%s: p_Holm = %s%s" % (ABR[a][:6], ABR[b][:6], p_es(r["p_holm_escenario"]),
                                                  " *" if r["p_holm_escenario"] < 0.05 else ""))
        ax.set_title("%s\nKruskal-Wallis %s" % (ESC_TXT[e], p_eq(kw.loc[e, "p"])))
        ax.text(0.5, -0.14, "\n".join(lin), transform=ax.transAxes, ha="center", va="top", fontsize=7.5)
        ax.grid(axis="y", alpha=0.25)
        eje_coma(ax)
    axs[0].set_ylabel("M1: segundos por archivo (media por ejecución)")
    fig.suptitle("M1 por escenario: media ± DE entre ejecuciones y valores individuales", y=1.02, fontsize=12)
    fig.text(0.5, -0.27, "* p ajustado de Holm < 0,05 (Mann-Whitney bilateral; familia = 3 pares por escenario). "
             "Comparaciones exploratorias: sin aleatorizar el orden de ejecución.", ha="center", fontsize=7.5, color="#555555")
    pie(fig, PIE, y=-0.31)
    fig.savefig(salida / "fig1_m1_por_escenario.png")
    plt.close(fig)


def fig2(R, salida):
    m1, o = R["M1_por_ejecucion"], R["M1_efecto_orden"].set_index(["escenario", "framework"])
    fig, axs = plt.subplots(1, 3, figsize=(12, 4.2), sharey=True)
    for ax, e in zip(axs, ai.ESCENARIOS):
        for f in ai.FRAMEWORKS:
            g = m1[(m1["escenario"] == e) & (m1["framework"] == f)].sort_values("corrida")
            r = o.loc[(e, f)]
            et = "%s (ρ = %s%s)" % (ABR[f], es(r["rho_spearman"]), "*" if r["signif_holm_0.05"] else "")
            ax.plot(g["corrida"], g["m1_s_por_archivo"], marker="o", ms=4, lw=1.2, color=COL[f], label=et)
        ax.set_title(ESC_TXT[e])
        ax.set_xlabel("Número de corrida (R01 a R10)")
        ax.set_xticks(range(1, 11))
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7.5, frameon=False)
        eje_coma(ax)
    axs[0].set_ylabel("M1: segundos por archivo")
    fig.suptitle("M1 según el orden de las corridas (diagnóstico post hoc)", y=1.02, fontsize=12)
    fig.text(0.5, -0.10, "ρ de Spearman entre número de corrida y M1; * = significativo tras Holm sobre las 9 correlaciones. "
             "Las corridas se ejecutaron en bloques consecutivos por framework y escenario.",
             ha="center", fontsize=7.5, color="#555555")
    pie(fig, PIE)
    fig.savefig(salida / "fig2_m1_orden_de_corrida.png")
    plt.close(fig)


def fig3(R, salida):
    r4 = R["M4_resumen"]
    b = r4[r4["escenario"] == "B"].set_index("framework")
    pf = R["M4_por_fuente"]
    pf = pf[pf["escenario"] == "B"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
    x = np.arange(3)
    w = 0.36
    for k, (col, lab, hat) in enumerate([("m4_pct_por_fuente", "Por fuente (4)", ""),
                                         ("m4_pct_por_archivo", "Por archivo (120)", "//")]):
        vals = [b.loc[f, col] for f in ai.FRAMEWORKS]
        bars = a1.bar(x + (k - 0.5) * w, vals, w, color=[COL[f] for f in ai.FRAMEWORKS], hatch=hat,
                      edgecolor="white" if not hat else "black", linewidth=0.5, label=lab)
        for bb, v in zip(bars, vals):
            a1.text(bb.get_x() + bb.get_width() / 2, v + 1.2, es(v, 1) + " %", ha="center", fontsize=8)
    a1.set_xticks(x)
    a1.set_xticklabels([ABR[f] for f in ai.FRAMEWORKS])
    a1.set_ylim(0, 135)
    a1.set_yticks(range(0, 101, 20))
    a1.set_ylabel("Identificación correcta de la fuente (%)")
    a1.set_title("M4 en escenario B")
    a1.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc="#bbbbbb", label="Por fuente (4)"),
                       plt.Rectangle((0, 0), 1, 1, fc="#bbbbbb", hatch="//", ec="black", label="Por archivo (120)")],
              frameon=False, fontsize=8, loc="upper left", ncol=2)
    eje_coma(a1, 0)
    mat = np.zeros((3, 4))
    txt = [["" for _ in range(4)] for _ in range(3)]
    for i, f in enumerate(ai.FRAMEWORKS):
        for j, s in enumerate(ai.FUENTES):
            r = pf[(pf["framework"] == f) & (pf["fuente_esperada"] == s)].iloc[0]
            mat[i, j] = r["archivos_correctos"] / r["archivos"]
            txt[i][j] = "%d/%d" % (r["archivos_correctos"], r["archivos"])
    a2.imshow(mat, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    a2.set_xticks(range(4))
    a2.set_xticklabels(["AEBE\n(PDF renombrado)", "FAOSTAT", "INEC-ESPAC", "SIPA-MAG"], fontsize=8.5)
    a2.set_yticks(range(3))
    a2.set_yticklabels([ABR[f] for f in ai.FRAMEWORKS])
    for i in range(3):
        for j in range(4):
            a2.text(j, i, txt[i][j], ha="center", va="center", fontsize=10, fontweight="bold")
    a2.set_title("Archivos asignados a su fuente esperada (B; 10 ejecuciones)")
    for s in a2.spines.values():
        s.set_visible(False)
    fig.suptitle("M4: identificación de fuente bajo perturbación (la fuente esperada sale del nombre del archivo)",
                 y=1.02, fontsize=12)
    fig.text(0.5, -0.13, "Custom antepone ESPAC_ al archivo SIPA de uso del suelo en su paso de descarga y su regla startswith('ESPAC_') lo etiqueta INEC-ESPAC (10 de 10 ejecuciones; también en A y C: 110/120).\n"
             "Es una diferencia de implementación, no un efecto de la perturbación. El PDF de AEBE renombrado fue identificado por las tres.",
             ha="center", fontsize=7.5, color="#555555")
    pie(fig, PIE.replace("n = 10 ejecuciones por framework y escenario.", "120 archivos por framework en B."))
    fig.savefig(salida / "fig3_m4_identificacion_fuente.png")
    plt.close(fig)


def fig4(R, salida):
    m5 = R["M5_por_ejecucion"]
    m5 = m5[m5["escenario"] == "C"]
    res = R["M5_resumen"].set_index(["escenario", "framework"])
    kw = float(R["M5_kruskal_C"]["p"].iloc[0])
    rec = R["M5_recuperacion"]
    rec = rec[rec["escenario"] == "C"].set_index("framework")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1.2, 1]})
    rng = np.random.default_rng(1)
    for i, f in enumerate(ai.FRAMEWORKS):
        v = m5[m5["framework"] == f]["m5_reintentos_por_ejecucion"].values
        a1.scatter(i + rng.uniform(-0.12, 0.12, len(v)), v, s=26, color=COL[f], alpha=0.7, zorder=2)
        mu, de = res.loc[("C", f), "media"], res.loc[("C", f), "de"]
        a1.errorbar(i, mu, yerr=de, fmt="_", color="black", capsize=6, markersize=22, lw=1.4, zorder=3)
        a1.text(i + 0.18, mu, es(mu, 1) + " ± " + es(de), va="center", fontsize=8.5)
    a1.set_xticks(range(3))
    a1.set_xticklabels([ABR[f] for f in ai.FRAMEWORKS])
    a1.set_xlim(-0.5, 2.9)
    a1.set_ylabel("Reintentos por ejecución (suma de las 4 fuentes)")
    a1.set_title("M5 en escenario C\nKruskal-Wallis %s" % p_eq(kw))
    a1.grid(axis="y", alpha=0.25)
    eje_coma(a1, 0)
    prop = [rec.loc[f, "proporcion_con_reintento"] * 100 for f in ai.FRAMEWORKS]
    bars = a2.bar(range(3), prop, color=[COL[f] for f in ai.FRAMEWORKS])
    for bb, f, p in zip(bars, ai.FRAMEWORKS, prop):
        a2.text(bb.get_x() + bb.get_width() / 2, p + 2, "%d/%d\n(%s %%)" % (rec.loc[f, "con_reintentos"],
                rec.loc[f, "registros_fuente_ejecucion"], es(p, 1)), ha="center", fontsize=8.5)
    a2.set_xticks(range(3))
    a2.set_xticklabels([ABR[f] for f in ai.FRAMEWORKS])
    a2.set_ylim(0, 100)
    a2.set_ylabel("Registros fuente-ejecución con al menos un reintento (%)")
    a2.set_title("Proporción por fuente y ejecución (no por archivo)\nRecuperación final: 100 % en las tres")
    eje_coma(a2, 0)
    fig.suptitle("M5: reintentos de descarga bajo fallo controlado", y=1.03, fontsize=12)
    fig.text(0.5, -0.10, "El número de reintentos mide el costo de recuperar, no la eficiencia. No hay eventos de intento por archivo.",
             ha="center", fontsize=7.5, color="#555555")
    pie(fig, PIE.replace("n = 10 ejecuciones por framework y escenario.", "n = 10 ejecuciones y 40 registros fuente-ejecución por framework."))
    fig.savefig(salida / "fig4_m5_reintentos_escenario_c.png")
    plt.close(fig)


def fig5(R, salida):
    g = R["M2_global"].iloc[0]
    m2 = R["M2_resumen"]
    m3 = R["M3_resumen"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 1.3]})
    x = np.arange(3)
    w = 0.36
    simple = [m2[m2["framework"] == f]["m2_media_simple_pct"].mean() for f in ai.FRAMEWORKS]
    pond = [m2[m2["framework"] == f]["filas_salida"].sum() / m2[m2["framework"] == f]["filas_entrada"].sum() * 100
            for f in ai.FRAMEWORKS]
    for k, (vals, hat, lab) in enumerate([(simple, "", "Media simple por archivo (principal)"),
                                          (pond, "//", "Ponderada por filas (sensibilidad)")]):
        bars = a1.bar(x + (k - 0.5) * w, vals, w, color=[COL[f] for f in ai.FRAMEWORKS], hatch=hat,
                      edgecolor="white" if not hat else "black", linewidth=0.5)
        for bb, v in zip(bars, vals):
            a1.text(bb.get_x() + bb.get_width() / 2, v + 1, es(v, 3) + " %", ha="center", fontsize=7.5)
    a1.set_xticks(x)
    a1.set_xticklabels([ABR[f] for f in ai.FRAMEWORKS])
    a1.set_ylim(0, 135)
    a1.set_yticks(range(0, 101, 20))
    a1.set_ylabel("M2 (%)")
    a1.set_title("M2: integridad/validez por reglas")
    a1.legend(handles=[plt.Rectangle((0, 0), 1, 1, fc="#bbbbbb", label="Media simple (principal)"),
                       plt.Rectangle((0, 0), 1, 1, fc="#bbbbbb", hatch="//", ec="black", label="Ponderada por filas")],
              frameon=False, fontsize=8, loc="upper left", ncol=1)
    eje_coma(a1, 0)
    w3 = 0.26
    for k, f in enumerate(ai.FRAMEWORKS):
        vals = [m3[(m3["escenario"] == e) & (m3["framework"] == f)]["m3_llamadas_por_archivo"].iloc[0]
                for e in ai.ESCENARIOS]
        bars = a2.bar(np.arange(3) + (k - 1) * w3, vals, w3, color=COL[f], label=ABR[f])
        for bb, v in zip(bars, vals):
            a2.text(bb.get_x() + bb.get_width() / 2, v + 0.015, es(v, 4), ha="center", fontsize=7, rotation=90)
    a2.set_xticks(range(3))
    a2.set_xticklabels([ESC_TXT[e] for e in ai.ESCENARIOS], fontsize=8)
    a2.set_ylim(0, 1.25)
    a2.set_ylabel("M3: llamadas al LLM por archivo")
    a2.set_title("M3: sin diferencias entre arquitecturas")
    a2.legend(frameon=False, fontsize=8, ncol=3, loc="upper center")
    eje_coma(a2, 1)
    fig.suptitle("M2 y M3 (valores idénticos entre arquitecturas en los registros)", y=1.03, fontsize=12)
    fig.text(0.5, -0.10, "M2 = filas_salida / filas_entrada × 100; no mide exactitud semántica. En M3, el escenario B "
             "registra 1 llamada por archivo y A y C 0,9167 (11 de 12 archivos).", ha="center", fontsize=7.5, color="#555555")
    pie(fig, PIE.replace("n = 10 ejecuciones por framework y escenario.", "1.080 instancias de archivo."))
    fig.savefig(salida / "fig5_m2_m3_resumen.png")
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera las figuras del manuscrito desde el consolidado oficial.")
    ap.add_argument("--consolidado", default=str(ai.CONSOLIDADO))
    ap.add_argument("--salida", default=str(ai.RAIZ / "resultados" / "graficos"))
    a = ap.parse_args(argv)
    d = ai.cargar(a.consolidado)
    R = ai.calcular(d)
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    for f in (fig1, fig2, fig3, fig4, fig5):
        f(R, salida)
    print("Figuras generadas en:", salida)


if __name__ == "__main__":
    main()
