#!/usr/bin/env python3
"""
generar_figuras.py
Regenera las figuras de resultados a partir de datos_individuales_corregidos.csv
(salida de analisis_ingenius.py). La unidad de analisis es la EJECUCION (n = 10 por
combinacion); el contador de reintentos se cuenta UNA VEZ POR FUENTE.

Uso: python generar_figuras.py --datos ../resultados/tablas/datos_individuales_corregidos.csv \
                                --salida ../resultados/graficos
"""
import argparse, itertools, os
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

CELDA = ["Arquitectura", "Escenario"]
COL = {"AgenteCustom": "#2b5c8f", "LangGraph": "#d95f02", "LlamaIndex": "#7570b3"}


def fuente(a):
    u = str(a).upper()
    if "FAOSTAT" in u: return "FAOSTAT"
    if "BANANOTAS" in u: return "AEBE"
    if "SIPA" in u and "ESPAC_TAB" not in u: return "SIPA"
    return "ESPAC"


def por_ejecucion(d):
    d = d.copy(); d["src"] = d.Archivo.map(fuente)
    t = d.groupby(CELDA + ["Corrida_ID"]).M1_Tiempo_s.sum().rename("t_total").reset_index()
    r = (d.groupby(CELDA + ["Corrida_ID", "src"]).Reintentos.max().reset_index()
         .groupby(CELDA + ["Corrida_ID"]).Reintentos.sum().rename("reintentos").reset_index())
    out = t.merge(r, on=CELDA + ["Corrida_ID"]); out["t_archivo"] = out.t_total / 12
    return out


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); aj = np.empty_like(p); prev = 0
    for k, i in enumerate(o):
        prev = max(prev, (len(p) - k) * p[i]); aj[i] = min(1, prev)
    return aj


def box(ax, datos, titulo, ylabel):
    arqs = list(COL)
    bp = ax.boxplot([datos[a] for a in arqs], patch_artist=True, widths=.5, showfliers=False)
    for patch, a in zip(bp["boxes"], arqs): patch.set_facecolor(COL[a]); patch.set_alpha(.7)
    for i, a in enumerate(arqs, 1):
        x = np.random.default_rng(1).normal(i, .05, len(datos[a])); ax.scatter(x, datos[a], c="k", s=14, alpha=.6, zorder=3)
    ax.set_xticks(range(1, 4)); ax.set_xticklabels(arqs); ax.set_title(titulo, fontweight="bold"); ax.set_ylabel(ylabel)
    ax.grid(axis="y", ls="--", alpha=.4)


def fuente_verdad(a):
    f = fuente(a)
    return {"ESPAC": "INEC_ESPAC", "SIPA": "SIPA_MAG", "FAOSTAT": "FAOSTAT", "AEBE": "AEBE_BANANOTAS"}[f]


def fig_resumen(d, r, salida):
    """Fig 1: resumen de metricas (M1, M3, M4 a nivel de archivo, M5)."""
    fig, axs = plt.subplots(1, 4, figsize=(17, 4.5))
    w = .26; x = np.arange(3)
    for i, k in enumerate(COL):
        m = [r[(r.Arquitectura == k) & (r.Escenario == e)].t_archivo for e in "ABC"]
        axs[0].bar(x + (i - 1) * w, [v.mean() for v in m], w, yerr=[v.std(ddof=1) for v in m], color=COL[k], capsize=3, label=k)
        axs[1].bar(x + (i - 1) * w, [d[(d.Arquitectura == k) & (d.Escenario == e)].M3_LLM_Calls.mean() for e in "ABC"], w, color=COL[k])
        axs[2].bar(x + (i - 1) * w, [(d[(d.Arquitectura == k) & (d.Escenario == e)].pipe(lambda t: (t.Fuente == t.Archivo.map(fuente_verdad)).mean() * 100)) for e in "ABC"], w, color=COL[k])
    c = r[r.Escenario == "C"]
    axs[3].bar(list(COL), [c[c.Arquitectura == k].reintentos.mean() for k in COL], .5, yerr=[c[c.Arquitectura == k].reintentos.std(ddof=1) for k in COL], color=list(COL.values()), capsize=3)
    for ax, t, yl in zip(axs, ["M1: s por archivo (media ± DE entre ejecuciones)", "M3: llamadas al LLM por archivo", "Archivos con la fuente correcta (%)", "M5: reintentos por corrida (Esc. C)"], ["s", "llamadas", "%", "reintentos"]):
        ax.set_title(t, fontsize=10, fontweight="bold"); ax.set_ylabel(yl); ax.grid(axis="y", ls="--", alpha=.4)
    for ax in axs[:3]: ax.set_xticks(x); ax.set_xticklabels(["A", "B", "C"]); ax.set_xlabel("Escenario")
    axs[2].set_ylim(0, 110); axs[3].tick_params(axis="x", labelsize=8); axs[0].legend(fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(salida, "fig1_resumen_metricas.png"), dpi=300); plt.close(fig)


def fig_fuente(d, salida):
    """Fig 3: identificacion de la fuente a nivel de archivo (los dos archivos SIPA pertenecen a SIPA-MAG)."""
    fig, ax = plt.subplots(figsize=(8, 4.8)); w = .26; x = np.arange(3)
    for i, k in enumerate(COL):
        v = [(lambda t: (t.Fuente == t.Archivo.map(fuente_verdad)).mean() * 100)(d[(d.Arquitectura == k) & (d.Escenario == e)]) for e in "ABC"]
        b = ax.bar(x + (i - 1) * w, v, w, color=COL[k], label=k)
        for rect, val in zip(b, v): ax.text(rect.get_x() + rect.get_width() / 2, val + 1, f"{val:.1f}", ha="center", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(["A", "B", "C"]); ax.set_xlabel("Escenario"); ax.set_ylabel("Archivos con la fuente correcta (%)"); ax.set_ylim(0, 112)
    ax.set_title("Identificación de la fuente por archivo (12 archivos por ejecución)", fontweight="bold"); ax.legend(loc="lower left", fontsize=8); ax.grid(axis="y", ls="--", alpha=.4)
    fig.tight_layout(); fig.savefig(os.path.join(salida, "fig3_identificacion_fuente.png"), dpi=300); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--datos", required=True); ap.add_argument("--salida", required=True)
    a = ap.parse_args(); os.makedirs(a.salida, exist_ok=True)
    d = pd.read_csv(a.datos); r = por_ejecucion(d)
    fig_resumen(d, r, a.salida); fig_fuente(d, a.salida)
    # Fig 2: M1 por ejecucion
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.5), sharey=True)
    for ax, e in zip(axs, "ABC"):
        box(ax, {k: r[(r.Escenario == e) & (r.Arquitectura == k)].t_archivo.values for k in COL}, f"Escenario {e}", "M1: s por archivo (media de cada ejecución)")
    fig.suptitle("M1 por ejecución (n = 10 por combinación)", fontweight="bold"); fig.tight_layout()
    fig.savefig(os.path.join(a.salida, "fig2_m1_por_ejecucion.png"), dpi=300); plt.close(fig)
    # Fig 4: M5 corregido
    c = r[r.Escenario == "C"]; fig, ax = plt.subplots(figsize=(8, 5))
    box(ax, {k: c[c.Arquitectura == k].reintentos.values for k in COL}, "M5: reintentos por corrida en el Escenario C (una vez por fuente)", "Reintentos por corrida (4 fuentes)")
    ax.axhline(6, c="r", ls="--", lw=1); ax.text(3.45, 6.15, "6 esperados por diseño", color="r", ha="right", fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(a.salida, "fig4_m5_reintentos_por_fuente.png"), dpi=300); plt.close(fig)
    # Fig 5: pruebas exploratorias a nivel de ejecucion
    kw, pares = [], []
    for e in "ABC":
        g = {k: r[(r.Escenario == e) & (r.Arquitectura == k)].t_total.values for k in COL}
        kw.append((f"M1 Esc. {e}", stats.kruskal(*g.values()).pvalue))
        for x, y in itertools.combinations(COL, 2):
            pares.append((f"M1 {e}: {x} vs {y}", stats.mannwhitneyu(g[x], g[y]).pvalue))
    g = {k: c[c.Arquitectura == k].reintentos.values for k in COL}
    kw.append(("M5 Esc. C", stats.kruskal(*g.values()).pvalue))
    pm = []
    for x, y in itertools.combinations(COL, 2): pm.append((f"M5 C: {x} vs {y}", stats.mannwhitneyu(g[x], g[y]).pvalue))
    adj1 = holm([p for _, p in pares]); adj2 = holm([p for _, p in pm])
    pares = [(n, p) for (n, _), p in zip(pares, adj1)] + [(n, p) for (n, _), p in zip(pm, adj2)]
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    axs[0].bar([n for n, _ in kw], [p for _, p in kw], color=["#2b5c8f" if p > .05 else "#d95f02" for _, p in kw])
    axs[0].axhline(.05, c="r", ls="--"); axs[0].set_ylabel("p (Kruskal-Wallis)"); axs[0].set_title("Kruskal-Wallis por ejecución", fontweight="bold")
    for i, (_, p) in enumerate(kw): axs[0].text(i, p, f"{p:.3f}", ha="center", va="bottom", fontsize=8)
    axs[1].barh([n for n, _ in pares], [max(p, 1e-4) for _, p in pares], color=["#2b5c8f" if p > .05 else "#d95f02" for _, p in pares])
    axs[1].axvline(.05, c="r", ls="--"); axs[1].set_xscale("log"); axs[1].set_xlabel("p ajustado (Holm)"); axs[1].set_title("Mann-Whitney por pares (exploratorio)", fontweight="bold")
    fig.tight_layout(); fig.savefig(os.path.join(a.salida, "fig5_comparaciones_exploratorias.png"), dpi=300); plt.close(fig)
    print("Figuras en", a.salida)

if __name__ == "__main__":
    main()
