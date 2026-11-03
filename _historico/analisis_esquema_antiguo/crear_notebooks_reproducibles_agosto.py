#!/usr/bin/env python3
"""
crear_notebooks_reproducibles.py
Genera, a partir de los notebooks originales de los experimentos, variantes *_reproducible.ipynb
que permiten ejecutarlos sin credenciales de Google Drive y con las versiones de LangChain,
LangGraph y LlamaIndex reportadas en el manuscrito. NO modifica los originales.

Cambios (y solo estos):
  1. Celda %pip: fija las versiones reportadas (pip freeze del experimento).
  2. Celda de configuracion: la inicializacion de Google Drive queda dentro de try/except
     (sin credenciales validas drive_service = None y el experimento sigue).
  3. Celdas que usan drive_service: se antepone un assert con un mensaje claro.
  4. Se agrega una celda markdown inicial que describe la variante.
Uso:  python crear_notebooks_reproducibles.py [raiz_del_repo]
"""
import copy, json, os, re, sys

RAIZ = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
PINS = {
    "AgenteCustom": [("langchain", "langchain==0.3.30 langchain-core==0.3.86")],
    "LangGraph":    [("langgraph", "langgraph==1.0.1"), ("langchain", "langchain==0.3.30 langchain-core==0.3.86")],
    "LlamaIndex":   [("llama-index llama-index-core", "llama-index==0.14.23 llama-index-workflows==2.22.2 llama-index-core")],
}
DRIVE_RE = re.compile(r"creds\s*=\s*service_account\.Credentials\.from_service_account_info\(\s*SERVICE_ACCOUNT_INFO,\s*scopes=\[[^\]]*\]\s*\)\s*drive_service\s*=\s*build\([^)]*\)")
DRIVE_NEW = '''try:
    creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive_service = build("drive", "v3", credentials=creds)
except Exception as _e:
    drive_service = None
    print("⚠️ Sin credenciales válidas de Google Drive: la exportación a Drive se omite (es opcional para reproducir las métricas).")'''
GUARD = 'assert drive_service is not None, "Esta celda exporta a Google Drive: configure SERVICE_ACCOUNT_INFO y FOLDER_OUTPUT_ID o no la ejecute (es opcional)."\n'
NOTA = ("# Variante reproducible\n\nMismo código que el notebook original, con cuatro cambios: (1) versiones fijadas de LangChain, "
        "LangGraph y LlamaIndex según el manuscrito; (2) la inicialización de Google Drive no detiene la ejecución si no hay "
        "credenciales; (3) las celdas que exportan a Drive lo avisan con un `assert`; (4) esta nota. "
        "Antes de ejecutar, defina `FAOSTAT_USERNAME`/`FAOSTAT_PASSWORD`, el catálogo/esquema y los volúmenes (ver REPRODUCIBILIDAD.md).")

def src(c): return "".join(c["source"])
def setsrc(c, text): c["source"] = text.splitlines(keepends=True)

def parchear(path):
    nb = json.load(open(path, encoding="utf-8")); arq = next(k for k in PINS if k.lower() in os.path.basename(path).lower().replace("agente", "agente") or k.lower() in path.lower())
    cambios = []
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code": continue
        s = src(c); n = s
        if "%pip install" in s and i < 8:
            for orig, nuevo in PINS[arq]:
                if orig in n: n = n.replace(orig, nuevo, 1); cambios.append((i, "pip fijado: " + nuevo))
            if "langchain-databricks" in n and "langchain-databricks==" not in n:
                n = n.replace("langchain-databricks", "langchain-databricks==0.1.2", 1); cambios.append((i, "pip fijado: langchain-databricks==0.1.2"))
        if DRIVE_RE.search(n):
            n = DRIVE_RE.sub(lambda m: DRIVE_NEW, n, 1); cambios.append((i, "Drive en try/except"))
        elif "drive_service" in n and "drive_service = None" not in n and "drive_service." in n:
            n = GUARD + n; cambios.append((i, "assert de Drive"))
        if n != s: setsrc(c, n)
    md = {"cell_type": "markdown", "metadata": {}, "source": NOTA.splitlines(keepends=True)}
    nb["cells"].insert(0, md)
    out = path.replace(".ipynb", "_reproducible.ipynb")
    json.dump(nb, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out, cambios

if __name__ == "__main__":
    base = os.path.join(RAIZ, "experimentos_comparacion")
    for d in sorted(os.listdir(base)):
        carpeta = os.path.join(base, d)
        if not os.path.isdir(carpeta): continue
        for f in os.listdir(carpeta):
            if f.endswith(".ipynb") and "_reproducible" not in f:
                out, cambios = parchear(os.path.join(carpeta, f)); print(os.path.basename(out)); [print("   celda", i, c) for i, c in cambios]
