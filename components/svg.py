"""Ilustraciones SVG lineales (baja opacidad) e iconos para la interfaz."""
import math
import random

from utils.theme import BURGUNDY, GOLD, PETROL, ROSE


def dna_helix(width=520, height=150, turns=3.2, color=ROSE, color2=GOLD, opacity=0.55, rungs=34) -> str:
    """Doble hélice horizontal con peldaños (pares de bases)."""
    pts1, pts2, lines = [], [], []
    amp, mid = height * 0.36, height / 2
    n = 220
    for i in range(n + 1):
        x = width * i / n
        t = 2 * math.pi * turns * i / n
        pts1.append(f"{x:.1f},{mid + amp * math.sin(t):.1f}")
        pts2.append(f"{x:.1f},{mid + amp * math.sin(t + math.pi):.1f}")
    for k in range(rungs):
        x = width * (k + 0.5) / rungs
        t = 2 * math.pi * turns * (k + 0.5) / rungs
        y1, y2 = mid + amp * math.sin(t), mid + amp * math.sin(t + math.pi)
        c = color2 if k % 4 == 0 else color
        lines.append(f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{c}" '
                     f'stroke-width="1.6" stroke-linecap="round" opacity="0.8"/>')
    return (f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
            f'preserveAspectRatio="xMidYMid meet" style="width:100%;height:auto;opacity:{opacity}">'
            + "".join(lines)
            + f'<polyline points="{" ".join(pts1)}" fill="none" stroke="{color}" stroke-width="2.4"/>'
            + f'<polyline points="{" ".join(pts2)}" fill="none" stroke="{color}" stroke-width="2.4" opacity="0.75"/>'
            + "</svg>")


def network(width=420, height=260, n=26, seed=7, color=ROSE, accent=GOLD, opacity=0.5) -> str:
    """Red de nodos y conexiones (redes genéticas / neuronales)."""
    rnd = random.Random(seed)
    nodes = [(rnd.uniform(15, width - 15), rnd.uniform(15, height - 15)) for _ in range(n)]
    edges = []
    for i, (x, y) in enumerate(nodes):
        d = sorted(((math.hypot(x - a, y - b), j) for j, (a, b) in enumerate(nodes) if j != i))[:2]
        for _, j in d:
            if i < j:
                a, b = nodes[j]
                edges.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{a:.1f}" y2="{b:.1f}" stroke="{color}" stroke-width="1"/>')
    circles = []
    for k, (x, y) in enumerate(nodes):
        r = 3 + (k % 3)
        c = accent if k % 7 == 0 else color
        circles.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}"/>')
    return (f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
            f'style="width:100%;height:auto;opacity:{opacity}">' + "".join(edges + circles) + "</svg>")


def brain(size=220, color=ROSE, accent=GOLD, opacity=0.55) -> str:
    """Silueta cerebral lineal con circunvoluciones estilizadas y nodos."""
    return f'''<svg viewBox="0 0 220 180" width="{size}" xmlns="http://www.w3.org/2000/svg" style="opacity:{opacity}">
<g fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
<path d="M108 22c-14-12-40-10-50 6-18-2-32 12-30 30-14 8-18 28-8 42-6 16 4 34 22 36 6 14 24 20 38 12 10 8 22 8 28 0z"/>
<path d="M112 22c14-12 40-10 50 6 18-2 32 12 30 30 14 8 18 28 8 42 6 16-4 34-22 36-6 14-24 20-38 12-10 8-22 8-28 0z"/>
<path d="M110 24v124"/>
<path d="M60 44c10 4 14 14 10 24M40 74c12-2 22 6 24 16M48 110c10-8 24-6 30 4M86 60c-8 8-6 20 4 26M84 120c4-10 14-14 22-10"/>
<path d="M160 44c-10 4-14 14-10 24M180 74c-12-2-22 6-24 16M172 110c-10-8-24-6-30 4M134 60c8 8 6 20-4 26M136 120c-4-10-14-14-22-10"/>
<path d="M104 148c0 10 6 18 6 24M116 148c0 10-6 18-6 24"/>
</g>
<g fill="{accent}"><circle cx="70" cy="68" r="3.4"/><circle cx="150" cy="92" r="3.4"/><circle cx="92" cy="112" r="3"/><circle cx="136" cy="56" r="3"/></g>
</svg>'''


def chromosome(height=120, color=PETROL, band=ROSE, opacity=0.7) -> str:
    """Par de cromátidas con centrómero y bandas."""
    return f'''<svg viewBox="0 0 60 160" height="{height}" xmlns="http://www.w3.org/2000/svg" style="opacity:{opacity}">
<g fill="none" stroke="{color}" stroke-width="2.4">
<path d="M8 14q0-10 10-10t10 10v50q0 8-6 12q6 4 6 12v58q0 10-10 10t-10-10v-58q0-8 6-12q-6-4-6-12z"/>
<path d="M32 14q0-10 10-10t10 10v50q0 8-6 12q6 4 6 12v58q0 10-10 10t-10-10v-58q0-8 6-12q-6-4-6-12z"/>
</g>
<g fill="{band}"><rect x="10" y="24" width="16" height="6" rx="2"/><rect x="34" y="24" width="16" height="6" rx="2"/>
<rect x="10" y="46" width="16" height="4" rx="2"/><rect x="34" y="46" width="16" height="4" rx="2"/>
<rect x="10" y="100" width="16" height="8" rx="2"/><rect x="34" y="100" width="16" height="8" rx="2"/>
<rect x="10" y="126" width="16" height="4" rx="2"/><rect x="34" y="126" width="16" height="4" rx="2"/></g>
</svg>'''


def acgt_strip(n=64, seed=3) -> str:
    rnd = random.Random(seed)
    s = "".join(rnd.choice("ACGT") for _ in range(n))
    return f'<div class="acgt">{s}</div>'


_ICONS = {
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "dna": '<path d="M7 3c0 6 10 6 10 12s-10 6-10 6"/><path d="M17 3c0 6-10 6-10 12"/><path d="M8 7h8M8 17h8M10 12h4"/>',
    "chromosome": '<path d="M8 3c0 4 3 6 3 9s-3 5-3 9"/><path d="M16 3c0 4-3 6-3 9s3 5 3 9"/><path d="M9.5 12h5"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>',
    "filter": '<path d="M3 5h18l-7 8v6l-4 2v-8z"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    "grid": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>',
    "scale": '<path d="M12 3v18M5 7h14M5 7l-3 7h6zM19 7l-3 7h6z"/>',
    "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    "brain": '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 3 3h3V4z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-3 3h-3V4z"/>',
    "book": '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/>',
    "network": '<circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><circle cx="12" cy="10" r="2"/><path d="M7 6.8l3.3 2.4M17 6.8l-3.3 2.4M12 12v4"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-5-5"/>',
    "sigma": '<path d="M18 4H6l6 8-6 8h12"/>',
}


def icon(name: str, size=22, color=BURGUNDY, stroke=1.8) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'xmlns="http://www.w3.org/2000/svg">{_ICONS.get(name, _ICONS["dna"])}</svg>')
