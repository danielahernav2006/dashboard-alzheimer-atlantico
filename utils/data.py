"""Carga en caché de los archivos ligeros de `data/` (generados por prepare_dashboard_data.py)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def _check(path: Path) -> Path:
    if not path.exists():
        st.error(
            f"No se encontró `{path.name}` en `data/`. Ejecuta primero "
            "`python prepare_dashboard_data.py --project-root <raíz del proyecto>`."
        )
        st.stop()
    return path


@st.cache_data(show_spinner=False)
def _csv_cached(name, stamp, size, **kw):
    return pd.read_csv(_check(DATA / name), **kw)

def csv(name: str, **kw):
    p = _check(DATA / name)
    return _csv_cached(name, p.stat().st_mtime_ns, p.stat().st_size, **kw)

@st.cache_data(show_spinner=False)
def _json_cached(name, stamp):
    return json.loads(_check(DATA / name).read_text(encoding="utf8"))

def jsonf(name: str):
    p = _check(DATA / name)
    return _json_cached(name, p.stat().st_mtime_ns)

def kpis():
    return jsonf("kpis.json")

def gwas() -> pd.DataFrame:
    df = csv("gwas_resultados.csv.gz", dtype={"rsid_documentado": str})
    df["crom"] = df["crom"].astype(int)
    df["logp"] = -np.log10(df["p"].clip(lower=np.finfo(float).tiny))
    df["rsid_documentado"] = df["rsid_documentado"].fillna("")
    return df


def manhattan_coords() -> tuple[pd.DataFrame, list, list]:
    d = gwas().sort_values(["crom", "pos"]).copy()
    lim = d.groupby("crom")["pos"].agg(["min", "max"])
    offset, offs, ticks = 0, {}, []
    gap = 8_000_000
    for c, r in lim.iterrows():
        offs[c] = offset - r["min"]
        ticks.append(offset + (r["max"] - r["min"]) / 2)
        offset += (r["max"] - r["min"]) + gap
    d["x"] = d["pos"] + d["crom"].map(offs)
    return d, ticks, list(lim.index)


def variables_meta() -> pd.DataFrame:
    return pd.DataFrame(jsonf("variables_meta.json"))


def eda() -> pd.DataFrame:
    df = pd.read_csv(_check(DATA / "eda_bivariado.csv"))
    for c in ["n_EDA", "Estadístico", "efecto_EDA", "IC 95% inf.", "IC 95% sup.", "p_EDA", "FDR_EDA", "missing_pct"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def literatura() -> list[dict]:
    return jsonf("literatura.json")


def fmt_int(x) -> str:
    return f"{int(x):,}".replace(",", ".")


def fmt_p(p: float) -> str:
    if p is None or pd.isna(p):
        return "—"
    if p < 1e-3:
        m, e = f"{p:.2e}".split("e")
        return f"{m}×10<sup>{int(e)}</sup>"
    return f"{p:.4f}"


def fmt_p_plain(p: float) -> str:
    if p is None or pd.isna(p):
        return "—"
    return f"{p:.2e}" if p < 1e-3 else f"{p:.4f}"


def fmt_dec(x, d=2) -> str:
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
