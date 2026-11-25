"""Componentes de interfaz reutilizables (HTML/CSS sobre Streamlit)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from components import svg
from utils.theme import PLOT_CONFIG

try:
    _V = tuple(int(x) for x in st.__version__.split(".")[:2])
except Exception:  # pragma: no cover
    _V = (1, 50)
# `use_container_width` está deprecado desde Streamlit 1.49 (reemplazado por width="stretch").
STRETCH = {"width": "stretch"} if _V >= (1, 49) else {"use_container_width": True}

CSS = Path(__file__).resolve().parent.parent / "assets" / "css" / "style.css"


def _compact(s: str) -> str:
    # Evita que Markdown interprete la indentación como bloque de código.
    return " ".join(line.strip() for line in s.splitlines() if line.strip())


def html(s: str) -> None:
    st.markdown(_compact(s), unsafe_allow_html=True)


def inject_css() -> None:
    st.markdown(f"<style>{CSS.read_text(encoding='utf8')}</style>", unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str = "", icon: str = "dna", deco: str = "dna") -> None:
    art = {
        "dna": svg.dna_helix(width=420, height=120, opacity=0.5),
        "network": svg.network(width=360, height=150, opacity=0.55),
        "brain": f'<div style="text-align:right;padding-right:40px">{svg.brain(150, opacity=0.5)}</div>',
        "chromosome": f'<div style="text-align:right;padding-right:50px">{svg.chromosome(110, opacity=0.5)}{svg.chromosome(80, opacity=0.35)}</div>',
        "none": "",
    }[deco]
    html(f"""
    <div class="ph"><div class="bar"></div>
      <div class="deco">{art}</div>
      <div class="eyebrow">{svg.icon(icon, 16, "#3E6870")} {eyebrow}</div>
      <h1>{title}</h1>
      <div class="sub">{subtitle}</div>
    </div>""")


def kpis(items: list[dict]) -> None:
    cards = []
    for it in items:
        kind = it.get("kind", "clinic")
        tip = f' title="{it["tip"]}"' if it.get("tip") else ""
        color = {"clinic": "#721C3B", "genetic": "#3E6870", "accent": "#8F6A38"}.get(kind, "#721C3B")
        cards.append(f"""
        <div class="kpi {kind}"{tip}>
          <div class="top"><div class="lbl">{it['label']}</div>{svg.icon(it.get('icon', 'chart'), 20, color)}</div>
          <div class="val">{it['value']}</div>
          <div class="sub">{it.get('sub', '')}</div>
        </div>""")
    html(f'<div class="kpis">{"".join(cards)}</div>')


def callout(text: str, kind: str = "info", icon: str | None = None) -> None:
    ic = icon or {"info": "check", "key": "target", "warn": "alert", "neutral": "book"}[kind]
    col = {"info": "#3E6870", "key": "#8F6A38", "warn": "#721C3B", "neutral": "#52697A"}[kind]
    html(f'<div class="callout {kind}"><div class="ic">{svg.icon(ic, 20, col)}</div><div>{text}</div></div>')


def badge(text: str, kind: str = "burg") -> str:
    return f'<span class="badge {kind}">{text}</span>'


def section(title: str, kicker: str = "") -> None:
    html(f'<div class="section"><div><div class="k">{kicker}</div><div class="t">{title}</div></div><div class="ln"></div></div>')


def details(md: str, title: str = "Detalles metodológicos") -> None:
    with st.expander(f"🔬 {title}", expanded=False):
        st.markdown(md)


def pipeline(steps: list[str], genetic_from: int = 2, final: int | None = None) -> None:
    parts = []
    for i, s in enumerate(steps):
        cls = "st"
        if i >= genetic_from:
            cls += " g"
        if final is not None and i == final:
            cls = "st f"
        parts.append(f'<div class="{cls}">{s}</div>')
        if i < len(steps) - 1:
            parts.append('<div class="ar">→</div>')
    html(f'<div class="pipe">{"".join(parts)}</div>')


def plot(fig, key: str | None = None, height: int | None = None) -> None:
    if height:
        fig.update_layout(height=height)
    st.plotly_chart(fig, config=PLOT_CONFIG, key=key, use_container_width=True)


def sources(*files: str) -> None:
    items = " · ".join(f"<code>{f}</code>" for f in files)
    html(f'<div class="foot"><b>Fuente de datos de esta página:</b> {items}</div>')


def download(df: pd.DataFrame, name: str, label: str = "Descargar CSV", key: str | None = None) -> None:
    st.download_button(label, df.to_csv(index=False).encode("utf-8-sig"), file_name=name,
                       mime="text/csv", key=key or f"dl_{name}", icon=":material/download:")


def summary(text: str) -> None:
    """Bloque de 'Resumen' en lenguaje sencillo."""
    html(f'<div class="card"><div class="badge petrol">RESUMEN</div><div style="margin-top:8px">{text}</div></div>')
