"""
Formation de Cellules Industrielles & Optimiseur de Disposition
===============================================================
Étape 0 – Saisir les données de gamme : importer un fichier Excel ou les saisir manuellement.
Étape 1 – Appliquer la méthode de King pour réordonner la matrice d'incidence et détecter les îlots.
Étape 2 – Sélectionner un îlot et visualiser la disposition en nid d'abeille (méthode Chaînon).
"""

from __future__ import annotations

import math
import random
import re
from collections import defaultdict
from io import BytesIO

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Formation de Cellules Industrielles",
    layout="wide",
    page_icon="🏭",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — Design industriel épuré, palette bleu acier / orange
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Source+Sans+3:wght@300;400;600&display=swap');

:root {
    --primary: #1a3a5c;
    --accent: #e8721a;
    --accent2: #2e86ab;
    --light-bg: #f4f7fb;
    --card-bg: #ffffff;
    --border: #dce4ef;
    --text-main: #1a2b3c;
    --text-muted: #5a7184;
    --success: #2d9e6b;
    --warning: #d97706;
    --danger: #c0392b;
    --step1-color: #1a3a5c;
    --step2-color: #e8721a;
    --step3-color: #2d9e6b;
}

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    color: var(--text-main);
}

/* Header principal */
.app-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #2e5f8a 50%, #1a3a5c 100%);
    padding: 2rem 2.5rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    border-bottom: 4px solid var(--accent);
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(232,114,26,0.08);
    border-radius: 50%;
}
.app-header-icon {
    font-size: 3rem;
    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3));
}
.app-header-text h1 {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 2rem;
    color: #ffffff;
    margin: 0;
    letter-spacing: 0.5px;
}
.app-header-text p {
    color: rgba(255,255,255,0.75);
    margin: 0.25rem 0 0;
    font-size: 0.95rem;
}

/* Étapes */
.step-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.5rem;
    border-radius: 10px;
    margin: 1.5rem 0 1rem;
}
.step-badge {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    color: white;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    white-space: nowrap;
}
.step-title {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 1.4rem;
    margin: 0;
}

/* Cards */
.info-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* KPI boxes */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 0.8rem;
    margin: 1rem 0;
}
.kpi-box {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.kpi-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--primary);
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 0.2rem;
}

/* Îlot cards */
.ilot-card {
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 5px solid;
    background: #f9fbff;
}
.ilot-card h4 {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    margin: 0 0 0.4rem;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3a5c 0%, #12293f 100%);
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.9) !important;
}
section[data-testid="stSidebar"] .stMarkdown p {
    color: rgba(255,255,255,0.75) !important;
}

/* Progress steps in sidebar */
.sidebar-step {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    transition: background 0.2s;
}
.sidebar-step.done {
    background: rgba(45,158,107,0.2);
    border: 1px solid rgba(45,158,107,0.4);
}
.sidebar-step.current {
    background: rgba(232,114,26,0.2);
    border: 1px solid rgba(232,114,26,0.4);
}
.sidebar-step.pending {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
}

/* Table styling */
.dataframe {
    border-radius: 8px;
    overflow: hidden;
}

/* Button overrides */
.stButton > button {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 0.3px;
    border-radius: 8px;
    transition: all 0.2s;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #e8721a, #d4601a);
    border: none;
    color: white;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(232,114,26,0.35);
}

/* Alert boxes */
.stAlert {
    border-radius: 8px;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* Tooltip / caption */
.stCaption {
    color: var(--text-muted) !important;
}

/* Spinner text */
.stSpinner > div {
    font-family: 'Rajdhani', sans-serif;
}

/* File uploader */
.stFileUploader {
    border-radius: 10px;
    overflow: hidden;
}

/* Expander */
.streamlit-expanderHeader {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
}

/* Data editor */
.stDataEditor {
    border-radius: 8px;
    overflow: hidden;
}

/* Footer */
.footer {
    text-align: center;
    padding: 1.5rem;
    color: var(--text-muted);
    font-size: 0.85rem;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# ── KING'S METHOD ──────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

def _king_sort_once(df: pd.DataFrame) -> pd.DataFrame:
    e = df.copy()
    L, C = e.shape

    ed_c = [
        sum(e.iloc[i, j] * (2 ** (C - j - 1)) for j in range(C))
        for i in range(L)
    ]
    e["EDc"] = ed_c
    e.sort_values("EDc", ascending=False, inplace=True)

    ed_i = [
        sum(e.iloc[i, j] * (2 ** (L - i - 1)) for i in range(L))
        for j in range(C)
    ]
    ed_i.append(0)
    e.loc["EDi"] = ed_i

    numeric_row = e.loc["EDi"].apply(pd.to_numeric, errors="coerce")
    sorted_cols = numeric_row.sort_values(ascending=False).index
    e = e[sorted_cols]
    return e


def apply_king_method(matrix_df: pd.DataFrame) -> pd.DataFrame:
    e = matrix_df.fillna(0).astype(float)
    L, C = e.shape

    e = _king_sort_once(e)

    while True:
        prev_edi = e.iloc[L].tolist()
        prev_edc = e["EDc"].tolist()

        e.drop("EDc", axis=1, inplace=True)
        e.drop(e.index[-1], axis=0, inplace=True)

        e = _king_sort_once(e)

        curr_edi = e.iloc[L].tolist()
        curr_edc = e["EDc"].tolist()

        if curr_edi == prev_edi and curr_edc == prev_edc:
            break

    final = e.copy()
    if "EDc" in final.columns:
        final.drop(columns=["EDc"], inplace=True)
    if "EDi" in final.index:
        final.drop(index="EDi", inplace=True)

    return final.astype(float)


def detect_cellules(df_final: pd.DataFrame) -> list[list]:
    products = list(df_final.index)
    machines = list(df_final.columns)
    m_idx = {m: i for i, m in enumerate(machines)}

    parent = list(range(len(machines)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x: int, y: int) -> None:
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for p in products:
        used = [m for m in machines if df_final.loc[p, m] == 1]
        for k in range(len(used) - 1):
            union(m_idx[used[k]], m_idx[used[k + 1]])

    groups: dict[int, list] = defaultdict(list)
    for m in machines:
        groups[find(m_idx[m])].append(m)

    col_order = {m: i for i, m in enumerate(machines)}
    cellules = [sorted(g, key=lambda m: col_order[m]) for g in groups.values()]
    cellules.sort(key=lambda c: col_order[c[0]])
    return cellules


def build_incidence_matrix(gamme_df: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    all_machines: set = set()

    for _, row in gamme_df.iterrows():
        product = str(row.iloc[0]).strip()
        raw_seq = str(row.iloc[1]).strip()
        tokens = re.split(r"[;\-,\s]+", raw_seq)
        machines = []
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            if t.upper().startswith("M"):
                t = t[1:]
            try:
                machines.append(int(t))
            except ValueError:
                pass
        all_machines.update(machines)
        rows[product] = machines

    all_machines_sorted = sorted(all_machines)
    matrix: dict[str, dict[int, int]] = {}
    for product, machines in rows.items():
        matrix[product] = {m: (1 if m in machines else 0) for m in all_machines_sorted}

    df = pd.DataFrame(matrix).T
    df.columns = [f"M{m}" for m in all_machines_sorted]
    return df.fillna(0).astype(float)


# ---------------------------------------------------------------------------
# ── CHAINON METHOD ──────────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

def traffic_from_sequences(gamme_df: pd.DataFrame, machines: list[str]) -> np.ndarray:
    m_labels = machines
    m_count = len(m_labels)
    label_to_idx = {lbl: i for i, lbl in enumerate(m_labels)}

    traffic = np.zeros((m_count, m_count), dtype=int)

    for _, row in gamme_df.iterrows():
        raw_seq = str(row.iloc[1]).strip()
        try:
            w = int(row.iloc[2])
        except (ValueError, TypeError):
            w = 1

        tokens = re.split(r"[;\-,\s]+", raw_seq)
        seq_labels = []
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            if not t.upper().startswith("M"):
                t = f"M{t}"
            if t in label_to_idx:
                seq_labels.append(t)

        for k in range(len(seq_labels) - 1):
            a = label_to_idx[seq_labels[k]]
            b = label_to_idx[seq_labels[k + 1]]
            traffic[a, b] += w

    return traffic


def directed_edges_from_traffic(
    traffic: np.ndarray, machines: list[str], threshold: int = 1
) -> tuple[list, dict]:
    m = traffic.shape[0]
    edges = []
    weights: dict = {}
    for a in range(m):
        for b in range(m):
            w = int(traffic[a, b])
            if w >= threshold:
                edges.append((machines[a], machines[b]))
                weights[(machines[a], machines[b])] = w
    return edges, weights


# Honeycomb geometry -----------------------------------------------------------

def honeycomb_points(rows: int, cols: int, dx: float = 1.0) -> dict:
    dy = math.sqrt(3) / 2 * dx
    pts = {}
    for r in range(rows):
        for c in range(cols):
            x = c * dx + (0.5 * dx if (r % 2) else 0.0)
            y = -r * dy
            pts[(r, c)] = (x, y)
    return pts


def honeycomb_edges(rows: int, cols: int) -> list:
    E = set()
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                E.add(((r, c), (r, c + 1)))
            if r + 1 < rows:
                if r % 2 == 0:
                    E.add(((r, c), (r + 1, c)))
                    if c - 1 >= 0:
                        E.add(((r, c), (r + 1, c - 1)))
                else:
                    E.add(((r, c), (r + 1, c)))
                    if c + 1 < cols:
                        E.add(((r, c), (r + 1, c + 1)))
    return list(E)


def lattice_neighbors(cell: tuple, rows: int, cols: int) -> list:
    r, c = cell
    nbrs = []
    if c - 1 >= 0:
        nbrs.append((r, c - 1))
    if c + 1 < cols:
        nbrs.append((r, c + 1))
    for dr in [-1, 1]:
        nr = r + dr
        if 0 <= nr < rows:
            nbrs.append((nr, c))
            if r % 2 == 0 and c - 1 >= 0:
                nbrs.append((nr, c - 1))
            elif r % 2 != 0 and c + 1 < cols:
                nbrs.append((nr, c + 1))
    return list(dict.fromkeys(nbrs))


def bfs_cells(center: tuple, rows: int, cols: int, k: int) -> list:
    q = [center]
    seen = {center}
    out = []
    while q and len(out) < k:
        cur = q.pop(0)
        out.append(cur)
        for nb in lattice_neighbors(cur, rows, cols):
            if nb not in seen:
                seen.add(nb)
                q.append(nb)
    return out


# Layout scoring ---------------------------------------------------------------

def _orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_seg(a, b, c):
    return (
        min(a[0], b[0]) <= c[0] <= max(a[0], b[0])
        and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])
    )


def segments_intersect(p1, p2, q1, q2) -> bool:
    o1, o2 = _orient(p1, p2, q1), _orient(p1, p2, q2)
    o3, o4 = _orient(q1, q2, p1), _orient(q1, q2, p2)
    if (o1 > 0 > o2 or o1 < 0 < o2) and (o3 > 0 > o4 or o3 < 0 < o4):
        return True
    if o1 == 0 and _on_seg(p1, p2, q1):
        return True
    if o2 == 0 and _on_seg(p1, p2, q2):
        return True
    if o3 == 0 and _on_seg(q1, q2, p1):
        return True
    if o4 == 0 and _on_seg(q1, q2, p2):
        return True
    return False


def layout_score(machine_to_cell, pts, edges, weights):
    pos = {m: pts[cell] for m, cell in machine_to_cell.items()}
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    dists = [math.hypot(x - cx, y - cy) for x, y in pos.values()]
    compact = sum(dists)
    radius = max(dists) if dists else 0.0

    pair = sum(
        math.hypot(
            pos[list(pos.keys())[i]][0] - pos[list(pos.keys())[j]][0],
            pos[list(pos.keys())[i]][1] - pos[list(pos.keys())[j]][1],
        )
        for i in range(len(pos))
        for j in range(i + 1, len(pos))
    )

    length = sum(
        weights[(u, v)]
        * math.hypot(pos[u][0] - pos[v][0], pos[u][1] - pos[v][1])
        for (u, v) in edges
    )

    segs = [(u, v, pos[u], pos[v]) for u, v in edges]
    crossings = 0.0
    for i in range(len(segs)):
        u1, v1, a1, a2 = segs[i]
        for j in range(i + 1, len(segs)):
            u2, v2, b1, b2 = segs[j]
            if len({u1, v1, u2, v2}) < 4:
                continue
            if segments_intersect(a1, a2, b1, b2):
                crossings += weights[(u1, v1)] + weights[(u2, v2)]

    score = (
        140.0 * crossings
        + 0.6 * length
        + 20.0 * compact
        + 200.0 * (radius**2)
        + 4.0 * pair
    )
    return score, crossings, length, compact, radius


def optimize_layout(machines, candidate_cells, pts, edges, weights, steps=80000, restarts=8, seed=0):
    rng = random.Random(seed)
    best_global = None
    best_global_score = float("inf")
    best_global_stats = None

    T0, T_end = 2.0, 0.01

    for _ in range(restarts):
        cells = candidate_cells[:]
        rng.shuffle(cells)
        cur = {machines[i]: cells[i] for i in range(len(machines))}
        cur_score, *cur_stats = layout_score(cur, pts, edges, weights)
        best_local = cur.copy()
        best_local_score = cur_score
        best_local_stats = cur_stats

        for s in range(steps):
            t = T0 * ((T_end / T0) ** (s / max(1, steps - 1)))
            a, b = rng.sample(machines, 2)
            cur[a], cur[b] = cur[b], cur[a]
            new_score, *new_stats = layout_score(cur, pts, edges, weights)
            delta = new_score - cur_score
            accept = (delta <= 0) or (rng.random() < math.exp(-delta / max(t, 1e-9)))
            if accept:
                cur_score = new_score
                if new_score < best_local_score:
                    best_local_score = new_score
                    best_local = cur.copy()
                    best_local_stats = new_stats
            else:
                cur[a], cur[b] = cur[b], cur[a]

        if best_local_score < best_global_score:
            best_global_score = best_local_score
            best_global = best_local
            best_global_stats = best_local_stats

    return best_global, best_global_score, best_global_stats


# Drawing ----------------------------------------------------------------------

def _unit_perp(dx, dy):
    n = math.hypot(dx, dy)
    return (0.0, 0.0) if n == 0 else (-dy / n, dx / n)


def draw_chainon(machine_to_cell, pts, base_edges, edges, weights, title="", palette_idx=0):
    fig, ax = plt.subplots(figsize=(13, 7), facecolor="#f4f7fb")
    ax.set_facecolor("#f4f7fb")

    # Draw honeycomb grid lightly
    for a, b in base_edges:
        x1, y1 = pts[a]
        x2, y2 = pts[b]
        ax.plot([x1, x2], [y1, y2], color="#c8d8e8", lw=0.8, zorder=1)

    # Empty nodes (small)
    for (r, c), (x, y) in pts.items():
        if (r, c) not in machine_to_cell.values():
            ax.add_patch(plt.Circle((x, y), 0.14, fc="#e8eef5", ec="#c0cfe0", lw=0.6, zorder=2))

    maxw = max(weights.values()) if weights else 1
    edge_set = set(edges)

    # Draw edges (arrows)
    node_colors = ["#1a3a5c", "#e8721a", "#2d9e6b", "#9b59b6", "#c0392b", "#16a085", "#d97706", "#2980b9"]
    machine_colors = {}
    for i, m in enumerate(machine_to_cell.keys()):
        machine_colors[m] = node_colors[i % len(node_colors)]

    for u, v in edges:
        x1, y1 = pts[machine_to_cell[u]]
        x2, y2 = pts[machine_to_cell[v]]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            continue
        ux, uy = dx / dist, dy / dist
        node_r = 0.28
        start = (x1 + ux * node_r, y1 + uy * node_r)
        end = (x2 - ux * node_r, y2 - uy * node_r)

        offx, offy = 0.0, 0.0
        if (v, u) in edge_set:
            px, py = _unit_perp(dx, dy)
            sgn = 1.0 if (str(u) < str(v)) else -1.0
            offx, offy = px * 0.1 * sgn, py * 0.1 * sgn

        w = weights[(u, v)]
        lw = 2.0 + 4.5 * (w / maxw)

        # Arrow color gradient by weight
        alpha = 0.5 + 0.5 * (w / maxw)
        ax.annotate(
            "",
            xy=(end[0] + offx, end[1] + offy),
            xytext=(start[0] + offx, start[1] + offy),
            arrowprops=dict(
                arrowstyle="-|>",
                color="#e8721a",
                lw=lw,
                shrinkA=0,
                shrinkB=0,
                alpha=alpha,
            ),
            zorder=4,
        )
        mx = (start[0] + end[0]) / 2 + offx
        my = (start[1] + end[1]) / 2 + offy
        ax.text(
            mx, my, str(w),
            fontsize=8.5, ha="center", va="center", fontweight="bold",
            color="#1a3a5c",
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="#dce4ef", lw=0.8),
            zorder=6,
        )

    # Draw machine nodes
    for i, (mid, cell) in enumerate(machine_to_cell.items()):
        x, y = pts[cell]
        color = node_colors[i % len(node_colors)]
        # Outer glow ring
        ax.add_patch(plt.Circle((x, y), 0.36, fc=color, ec="white", lw=2.5, zorder=6, alpha=0.15))
        # Main circle
        ax.add_patch(plt.Circle((x, y), 0.28, fc=color, ec="white", lw=2.5, zorder=7))
        ax.text(x, y, str(mid), ha="center", va="center",
                fontsize=10, fontweight="bold", color="white", zorder=8)

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", color="#1a3a5c", pad=12)
    plt.tight_layout(pad=1.5)
    return fig


# ===========================================================================
# ── STREAMLIT UI ────────────────────────────────────────────────────────────
# ===========================================================================

PALETTE = [
    "#1a3a5c", "#e8721a", "#2d9e6b", "#9b59b6",
    "#c0392b", "#16a085", "#d97706", "#2980b9",
]

PALETTE_LIGHT = [
    "#e8eef5", "#fef0e6", "#e8f7f2", "#f5eef8",
    "#fdecea", "#e8f6f3", "#fef9e7", "#eaf4fb",
]


def _init_state():
    for key, default in [
        ("gamme_df", None),
        ("incidence_df", None),
        ("king_df", None),
        ("cellules", None),
        ("selected_cellule_idx", 0),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


_init_state()

# ── En-tête principal ─────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div class="app-header-icon">🏭</div>
    <div class="app-header-text">
        <h1>Formation de Cellules Industrielles</h1>
        <p>Optimisation de la disposition des ateliers · Méthode de King &amp; Méthode Chaînon</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏭 Navigation")
    st.markdown("---")

    step_done = 0
    if st.session_state.gamme_df is not None:
        step_done = 1
    if st.session_state.king_df is not None:
        step_done = 2
    if st.session_state.cellules is not None:
        step_done = 3

    steps_info = [
        ("Données de gamme", "Importer ou saisir les gammes opératoires"),
        ("Méthode de King", "Réordonner la matrice — détecter les îlots"),
        ("Méthode Chaînon", "Optimiser la disposition des flux"),
    ]

    for i, (step_name, step_desc) in enumerate(steps_info):
        if step_done > i:
            css_class = "done"
            icon = "✅"
        elif i == step_done:
            css_class = "current"
            icon = "▶️"
        else:
            css_class = "pending"
            icon = "⏳"

        st.markdown(
            f'<div class="sidebar-step {css_class}">'
            f'<span style="font-size:1.1rem">{icon}</span>'
            f'<div>'
            f'<div style="font-weight:600;font-size:0.9rem">Étape {i + 1} — {step_name}</div>'
            f'<div style="font-size:0.75rem;opacity:0.75">{step_desc}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("**À propos**")
    st.caption(
        "Outil d'optimisation de la production industrielle basé sur "
        "la méthode de King (formation d'îlots) et la méthode Chaînon "
        "(disposition des flux par recuit simulé)."
    )

    if st.session_state.gamme_df is not None:
        st.markdown("---")
        if st.button("🔁 Réinitialiser tout", use_container_width=True):
            for k in ["gamme_df", "incidence_df", "king_df", "cellules"]:
                st.session_state[k] = None
            st.rerun()

# ===========================================================================
# ÉTAPE 0 – SAISIE DES DONNÉES
# ===========================================================================
st.markdown("""
<div class="step-header" style="background:#eef3fb">
  <span class="step-badge" style="background:#1a3a5c">Étape 0</span>
  <span class="step-title" style="color:#1a3a5c">Saisie des Données de Gamme</span>
</div>
""", unsafe_allow_html=True)

if st.session_state.gamme_df is None:
    st.markdown("""
    <div class="info-card">
    Fournissez le tableau de <strong>gamme opératoire</strong> (routage).
    Chaque ligne représente un produit avec sa séquence de machines et le nombre de manutentions.
    </div>
    """, unsafe_allow_html=True)

    col_ex, col_fmt = st.columns([2, 1])
    with col_ex:
        st.markdown("**Format attendu :**")
        example_df = pd.DataFrame({
            "Produit": ["P1", "P2", "P3"],
            "Gamme": ["M1-M2-M3", "M2-M4-M5", "M1-M3-M5"],
            "Nombre de manutentions": [5, 3, 4],
        })
        st.dataframe(example_df, use_container_width=True, hide_index=True)
    with col_fmt:
        st.markdown("**Séparateurs acceptés :**")
        st.markdown("- Tiret : `M1-M2-M3`")
        st.markdown("- Point-virgule : `M1;M2;M3`")
        st.markdown("- Virgule : `M1,M2,M3`")
        st.markdown("- Espace : `M1 M2 M3`")

    st.markdown("---")
    input_mode = st.radio(
        "Mode de saisie :",
        ["📁 Importer un fichier Excel", "✏️ Saisie manuelle"],
        horizontal=True,
    )

    if input_mode == "📁 Importer un fichier Excel":
        uploaded = st.file_uploader(
            "Glissez-déposez votre fichier ou cliquez pour parcourir",
            type=["xlsx", "xls"],
            help="Colonnes attendues : Produit | Gamme | Nombre de manutentions"
        )
        if uploaded:
            try:
                raw = pd.read_excel(uploaded, header=0)
                raw = raw.iloc[:, :3]
                raw.columns = ["Product", "Gamme", "Nombre de manutention"]
                raw.dropna(subset=["Product", "Gamme"], inplace=True)
                raw["Nombre de manutention"] = pd.to_numeric(
                    raw["Nombre de manutention"], errors="coerce"
                ).fillna(1).astype(int)
                st.session_state.gamme_df = raw
                st.success(f"✅ {len(raw)} produits chargés depuis le fichier.")
                st.rerun()
            except Exception as exc:
                st.error(f"Impossible de lire le fichier : {exc}")

    else:
        st.markdown("Saisissez vos données ci-dessous (ajoutez des lignes avec le bouton **+**) :")

        default_data = pd.DataFrame({
            "Product": ["P1", "P2", "P3", "P4"],
            "Gamme": ["M1-M2-M3", "M2-M4-M5", "M1-M3-M5", "M3-M4"],
            "Nombre de manutention": [5, 3, 4, 2],
        })

        edited = st.data_editor(
            default_data,
            num_rows="dynamic",
            use_container_width=True,
            key="manual_gamme",
            column_config={
                "Product": st.column_config.TextColumn("Produit", help="Code produit (ex: P1)"),
                "Gamme": st.column_config.TextColumn("Gamme", help="Séquence de machines (ex: M1-M2-M3)"),
                "Nombre de manutention": st.column_config.NumberColumn("Nb. manutentions", min_value=1, step=1),
            }
        )
        if st.button("✅ Confirmer la saisie", type="primary"):
            edited = edited.dropna(subset=["Product", "Gamme"])
            edited["Nombre de manutention"] = pd.to_numeric(
                edited["Nombre de manutention"], errors="coerce"
            ).fillna(1).astype(int)
            st.session_state.gamme_df = edited.reset_index(drop=True)
            st.success(f"✅ {len(edited)} produits enregistrés.")
            st.rerun()

else:
    gdf = st.session_state.gamme_df
    n_products = len(gdf)
    n_machines_raw = set()
    for _, row in gdf.iterrows():
        for t in re.split(r"[;\-,\s]+", str(row.iloc[1])):
            t = t.strip()
            if t:
                n_machines_raw.add(t)

    # KPI summary
    st.markdown(
        f'<div class="kpi-grid">'
        f'<div class="kpi-box"><div class="kpi-value">{n_products}</div><div class="kpi-label">Produits</div></div>'
        f'<div class="kpi-box"><div class="kpi-value">{len(n_machines_raw)}</div><div class="kpi-label">Machines</div></div>'
        f'<div class="kpi-box"><div class="kpi-value">{gdf.iloc[:, 2].sum()}</div><div class="kpi-label">Manut. totales</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.success("✅ Données de gamme chargées avec succès.")
    with st.expander("📋 Aperçu du tableau de gamme", expanded=False):
        st.dataframe(
            gdf.rename(columns={"Product": "Produit", "Nombre de manutention": "Nb. manutentions"}),
            use_container_width=True,
            hide_index=True
        )

# ===========================================================================
# ÉTAPE 1 – MÉTHODE DE KING
# ===========================================================================
if st.session_state.gamme_df is not None:
    st.markdown("""
    <div class="step-header" style="background:#fef3ea">
      <span class="step-badge" style="background:#e8721a">Étape 1</span>
      <span class="step-title" style="color:#e8721a">Méthode de King — Formation des Îlots</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.king_df is None:
        st.markdown("""
        <div class="info-card">
        La <strong>méthode de King</strong> réordonne la matrice d'incidence produit × machine 
        par calcul itératif des scores EDc (lignes) et EDi (colonnes) jusqu'à stabilisation, 
        puis détecte les <strong>îlots de fabrication</strong> par analyse de composantes connexes.
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Appliquer la méthode de King", type="primary"):
            with st.spinner("Application de la méthode de King en cours …"):
                try:
                    inc = build_incidence_matrix(st.session_state.gamme_df)
                    king = apply_king_method(inc)
                    cellules = detect_cellules(king)
                    st.session_state.incidence_df = inc
                    st.session_state.king_df = king
                    st.session_state.cellules = cellules
                    st.rerun()
                except Exception as exc:
                    st.error(f"La méthode de King a échoué : {exc}")
    else:
        king = st.session_state.king_df
        cellules = st.session_state.cellules

        # KPI
        n_ilots = len(cellules)
        avg_m = sum(len(c) for c in cellules) / max(n_ilots, 1)
        st.markdown(
            f'<div class="kpi-grid">'
            f'<div class="kpi-box"><div class="kpi-value">{n_ilots}</div><div class="kpi-label">Îlots détectés</div></div>'
            f'<div class="kpi-box"><div class="kpi-value">{len(king.columns)}</div><div class="kpi-label">Machines</div></div>'
            f'<div class="kpi-box"><div class="kpi-value">{len(king.index)}</div><div class="kpi-label">Produits</div></div>'
            f'<div class="kpi-box"><div class="kpi-value">{avg_m:.1f}</div><div class="kpi-label">Machines/îlot</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("**📊 Matrice d'incidence réordonnée (Méthode de King)**")

            n_cells = len(cellules)
            fig_hm, ax_hm = plt.subplots(
                figsize=(max(6, len(king.columns) * 0.7), max(4, len(king.index) * 0.6)),
                facecolor="#f4f7fb"
            )
            ax_hm.set_facecolor("#f4f7fb")

            colour_mat = np.zeros_like(king.values, dtype=float)
            for ci, cell_machines in enumerate(cellules):
                for j, col in enumerate(king.columns):
                    if col in cell_machines:
                        colour_mat[:, j] = ci + 1

            # Custom color palette
            cmap_colors = ["#eef3fb"] + [PALETTE_LIGHT[i] for i in range(n_cells)]
            from matplotlib.colors import LinearSegmentedColormap

            sns.heatmap(
                colour_mat,
                ax=ax_hm,
                cmap=sns.color_palette([PALETTE_LIGHT[i % len(PALETTE_LIGHT)] for i in range(n_cells + 1)]),
                linewidths=0.8,
                linecolor="white",
                cbar=False,
                xticklabels=king.columns,
                yticklabels=king.index,
                annot=king.astype(int),
                fmt="d",
                annot_kws={"size": 9, "color": "#1a3a5c", "fontweight": "bold"},
                vmin=0,
                vmax=n_cells,
            )

            # Add cellule labels on top
            for ci, cell_machines in enumerate(cellules):
                col_indices = [list(king.columns).index(m) for m in cell_machines if m in king.columns]
                if col_indices:
                    mid = (min(col_indices) + max(col_indices)) / 2
                    ax_hm.text(
                        mid + 0.5, -0.6, f"Îlot {ci+1}",
                        ha="center", va="bottom", fontsize=8,
                        color=PALETTE[ci % len(PALETTE)], fontweight="bold"
                    )

            ax_hm.set_title("Matrice réordonnée — Îlots colorés", fontsize=11, fontweight="bold", color="#1a3a5c", pad=15)
            ax_hm.set_xlabel("Machines", fontsize=9, color="#5a7184")
            ax_hm.set_ylabel("Produits", fontsize=9, color="#5a7184")
            ax_hm.tick_params(colors="#1a3a5c", labelsize=8)
            plt.tight_layout(pad=1.2)
            st.pyplot(fig_hm)
            plt.close(fig_hm)

        with col_right:
            st.markdown("**🔵 Îlots de machines détectés**")

            if not cellules:
                st.warning("Aucun îlot détecté.")
            else:
                for idx, cell_machines in enumerate(cellules):
                    col_hex = PALETTE[idx % len(PALETTE)]
                    col_light = PALETTE_LIGHT[idx % len(PALETTE_LIGHT)]
                    machines_str = " · ".join(str(m) for m in cell_machines)

                    cell_products = [
                        str(p)
                        for p in king.index
                        if any(king.loc[p, m] == 1 for m in cell_machines if m in king.columns)
                    ]
                    prod_count = len(cell_products)

                    st.markdown(
                        f'<div class="ilot-card" style="border-left-color:{col_hex};background:{col_light}">'
                        f'<h4 style="color:{col_hex}">🏭 Îlot {idx + 1}</h4>'
                        f'<div style="display:flex;gap:1rem;margin-bottom:0.4rem">'
                        f'<span style="font-size:0.8rem;background:{col_hex};color:white;'
                        f'padding:2px 8px;border-radius:12px">{len(cell_machines)} machines</span>'
                        f'<span style="font-size:0.8rem;background:#1a3a5c;color:white;'
                        f'padding:2px 8px;border-radius:12px">{prod_count} produits</span>'
                        f'</div>'
                        f'<div style="font-size:0.85rem;color:#1a3a5c"><b>Machines :</b> {machines_str}</div>'
                        f'<div style="font-size:0.82rem;color:#5a7184;margin-top:0.3rem">'
                        f'<b>Produits :</b> {", ".join(cell_products)}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

# ===========================================================================
# ÉTAPE 2 – MÉTHODE CHAÎNON
# ===========================================================================
if st.session_state.cellules is not None:
    st.markdown("""
    <div class="step-header" style="background:#eaf7f2">
      <span class="step-badge" style="background:#2d9e6b">Étape 2</span>
      <span class="step-title" style="color:#2d9e6b">Méthode Chaînon — Optimisation des Flux</span>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.cellules:
        st.warning("Aucun îlot détecté — impossible d'appliquer la méthode Chaînon.")
    else:
        cellules = st.session_state.cellules
        gamme_df = st.session_state.gamme_df

        st.markdown("""
        <div class="info-card">
        La <strong>méthode Chaînon</strong> détermine la disposition optimale des machines 
        dans un îlot sur une grille en nid d'abeille, en minimisant les croisements de flux 
        et la distance totale pondérée via un algorithme de <strong>recuit simulé</strong>.
        </div>
        """, unsafe_allow_html=True)

        cell_labels = [
            f"Îlot {i + 1} — {', '.join(str(m) for m in c)} ({len(c)} machines)"
            for i, c in enumerate(cellules)
        ]

        selected_label = st.selectbox(
            "🔍 Sélectionner un îlot à analyser :",
            cell_labels,
            help="Choisissez l'îlot pour lequel optimiser la disposition des machines"
        )
        selected_idx = cell_labels.index(selected_label)
        cell_machines = cellules[selected_idx]

        col_hex = PALETTE[selected_idx % len(PALETTE)]
        machines_display = " → ".join(str(m) for m in cell_machines)
        st.markdown(
            f'<div style="background:{PALETTE_LIGHT[selected_idx % len(PALETTE_LIGHT)]};'
            f'border:1px solid {col_hex};border-radius:8px;padding:0.7rem 1rem;margin:0.5rem 0">'
            f'<span style="color:{col_hex};font-weight:600">Îlot {selected_idx+1} :</span> '
            f'<span style="color:#1a3a5c">{machines_display}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            n_steps = st.slider(
                "Nombre de pas d'optimisation :",
                min_value=20000, max_value=150000, value=80000, step=10000,
                help="Plus le nombre est élevé, meilleure est la solution (mais plus long)"
            )
        with col_opt2:
            n_restarts = st.slider(
                "Nombre de redémarrages :",
                min_value=3, max_value=15, value=8,
                help="Plusieurs redémarrages évitent les optima locaux"
            )

        if st.button("🚀 Calculer la disposition Chaînon", type="primary"):
            with st.spinner(f"Optimisation par recuit simulé en cours ({n_steps:,} pas × {n_restarts} redémarrages) …"):
                try:
                    machine_set = {
                        m if str(m).upper().startswith("M") else f"M{m}"
                        for m in cell_machines
                    }

                    def _relevant_machines(raw_seq):
                        tokens = re.split(r"[;\-,\s]+", str(raw_seq))
                        result = []
                        for t in tokens:
                            t = t.strip()
                            if not t:
                                continue
                            label = t if t.upper().startswith("M") else f"M{t}"
                            if label in machine_set:
                                result.append(label)
                        return result

                    filtered_rows = []
                    for _, row in gamme_df.iterrows():
                        rel = _relevant_machines(row.iloc[1])
                        if len(rel) >= 2:
                            new_seq = "-".join(rel)
                            try:
                                qty = int(row.iloc[2])
                            except (ValueError, TypeError):
                                qty = 1
                            filtered_rows.append([str(row.iloc[0]), new_seq, qty])

                    if not filtered_rows:
                        st.warning(
                            "Aucun itinéraire produit ne passe par au moins 2 machines de cet îlot. "
                            "Vérifiez vos données de gamme."
                        )
                    else:
                        filtered_df = pd.DataFrame(
                            filtered_rows,
                            columns=["Product", "Gamme", "Nombre de manutention"]
                        )

                        machines_list = list(cell_machines)
                        m_count = len(machines_list)

                        traffic = traffic_from_sequences(filtered_df, machines_list)
                        edges, weights = directed_edges_from_traffic(traffic, machines_list)

                        if not edges:
                            st.warning(
                                "Aucun flux de trafic détecté entre les machines de cet îlot. "
                                "Ajustez vos données de gamme ou le seuil."
                            )
                        else:
                            rows_hc = max(5, m_count + 2)
                            cols_hc = max(6, m_count + 3)
                            pts = honeycomb_points(rows_hc, cols_hc, dx=1.2)
                            base_edges_hc = honeycomb_edges(rows_hc, cols_hc)
                            center = (rows_hc // 2, cols_hc // 2)
                            candidate_cells = bfs_cells(center, rows_hc, cols_hc, k=m_count)

                            best_layout, best_score, stats = optimize_layout(
                                machines_list,
                                candidate_cells,
                                pts,
                                edges,
                                weights,
                                steps=n_steps,
                                restarts=n_restarts,
                                seed=42,
                            )

                            crossings, length, compact, radius = stats
                            title = (
                                f"Îlot {selected_idx + 1} — Disposition optimisée  "
                                f"(croisements : {crossings:.0f}  |  rayon : {radius:.2f})"
                            )

                            # KPI résultats
                            st.markdown(
                                f'<div class="kpi-grid">'
                                f'<div class="kpi-box"><div class="kpi-value" style="color:#2d9e6b">{best_score:.0f}</div><div class="kpi-label">Score optimal</div></div>'
                                f'<div class="kpi-box"><div class="kpi-value" style="color:{"#c0392b" if crossings>0 else "#2d9e6b"}">{crossings:.0f}</div><div class="kpi-label">Croisements</div></div>'
                                f'<div class="kpi-box"><div class="kpi-value">{length:.1f}</div><div class="kpi-label">Long. pondérée</div></div>'
                                f'<div class="kpi-box"><div class="kpi-value">{radius:.2f}</div><div class="kpi-label">Rayon max</div></div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                            fig = draw_chainon(
                                best_layout, pts, base_edges_hc, edges, weights,
                                title=title, palette_idx=selected_idx
                            )
                            st.pyplot(fig)
                            plt.close(fig)

                            col_t, col_f = st.columns(2)
                            with col_t:
                                st.markdown("**📋 Matrice de trafic dirigé**")
                                traffic_df = pd.DataFrame(
                                    traffic,
                                    index=machines_list,
                                    columns=machines_list,
                                )
                                st.dataframe(
                                    traffic_df.style.background_gradient(cmap="Blues", axis=None),
                                    use_container_width=True
                                )

                            with col_f:
                                st.markdown("**🔗 Détail des flux**")
                                flows = [
                                    {"De": u, "Vers": v, "Flux": weights[(u, v)]}
                                    for u, v in sorted(edges, key=lambda e: -weights[e])
                                ]
                                flows_df = pd.DataFrame(flows)
                                st.dataframe(flows_df, use_container_width=True, hide_index=True)

                except Exception as exc:
                    st.error(f"La méthode Chaînon a échoué : {exc}")

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    🏭 Formation de Cellules Industrielles &nbsp;·&nbsp; Méthode de King + Méthode Chaînon
    <br><span style="font-size:0.8rem">Optimisation par recuit simulé · Grille en nid d'abeille</span>
</div>
""", unsafe_allow_html=True)
