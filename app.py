"""Streamlit UI for the Ziggu maze puzzle simulator."""
import streamlit as st
from ziggu import ZigguPuzzle, DEFAULT_PATH

st.set_page_config(page_title="Ziggu Mazes", layout="wide")

MAZE_COLORS = ["#1a56db", "#2e8b3d", "#e08a1a", "#b22222",
               "#6a1b9a", "#00838f", "#c62828", "#4e342e"]

CELL_SIZE = 180


def color_for(slide_label: int, m: int) -> str:
    return MAZE_COLORS[(m - slide_label) % len(MAZE_COLORS)]


def render_maze_svg(pos, color, path, reflected=False, size=CELL_SIZE):
    cell = size / 4
    valid_cells = set(path)
    pos_index = {p: i for i, p in enumerate(path)}

    def xy(row, col):
        x = (col * cell + cell / 2) if reflected else ((3 - col) * cell + cell / 2)
        return x, row * cell + cell / 2

    svg = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    svg.append(f'<rect x="2" y="2" width="{size-4}" height="{size-4}" rx="6" '
               f'fill="white" stroke="{color}" stroke-width="2" opacity="0.15"/>')

    # path track
    pts = [xy(r, c) for (r, c) in path]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    svg.append(f'<path d="{d}" stroke="{color}" stroke-width="7" fill="none" '
               f'stroke-linecap="round" stroke-linejoin="round" opacity="0.3"/>')

    # cell dots
    for (r, c) in valid_cells:
        x, y = xy(r, c)
        # mark start/exit
        if (r, c) == path[0]:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="none" '
                       f'stroke="{color}" stroke-width="2" opacity="0.7"/>')
        elif (r, c) == path[-1]:
            svg.append(f'<rect x="{x-5:.1f}" y="{y-5:.1f}" width="10" height="10" '
                       f'fill="{color}" opacity="0.7"/>')
        else:
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}" opacity="0.4"/>')

    # current position
    x, y = xy(*pos)
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{color}" '
               f'stroke="white" stroke-width="2.5"/>')

    # row labels
    for row in range(4):
        lx = 10 if reflected else size - 10
        anchor = "start" if reflected else "end"
        svg.append(f'<text x="{lx}" y="{row * cell + cell / 2 + 4}" font-size="11" '
                   f'fill="{color}" text-anchor="{anchor}" opacity="0.7">{row}</text>')
    # col labels
    for col in range(4):
        x, _ = xy(3.75, col)
        svg.append(f'<text x="{x:.1f}" y="{size - 4}" font-size="11" '
                   f'fill="{color}" text-anchor="middle" opacity="0.7">{col}</text>')

    svg.append("</svg>")
    return "".join(svg)


def render_editor_svg(drawn_path, hover_cell=None, size=280):
    """4x4 grid SVG for the path editor (col 0 = right)."""
    cell = size / 4

    def xy(row, col):
        return (3 - col) * cell + cell / 2, row * cell + cell / 2

    svg = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
           f'xmlns="http://www.w3.org/2000/svg">']
    svg.append(f'<rect x="0" y="0" width="{size}" height="{size}" fill="#1e1e2e" rx="8"/>')

    # grid lines
    for i in range(5):
        coord = i * cell
        svg.append(f'<line x1="{coord}" y1="0" x2="{coord}" y2="{size}" '
                   f'stroke="#444" stroke-width="1"/>')
        svg.append(f'<line x1="0" y1="{coord}" x2="{size}" y2="{coord}" '
                   f'stroke="#444" stroke-width="1"/>')

    # drawn path
    if len(drawn_path) > 1:
        pts = [xy(r, c) for (r, c) in drawn_path]
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        svg.append(f'<path d="{d}" stroke="#60a5fa" stroke-width="5" fill="none" '
                   f'stroke-linecap="round" stroke-linejoin="round"/>')

    # cells
    for r in range(4):
        for c in range(4):
            x, y = xy(r, c)
            if (r, c) in drawn_path:
                idx = drawn_path.index((r, c))
                color = "#22c55e" if idx == 0 else ("#f97316" if idx == len(drawn_path) - 1 else "#60a5fa")
                svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="14" fill="{color}"/>')
                svg.append(f'<text x="{x:.1f}" y="{y + 4:.1f}" font-size="11" '
                           f'fill="white" text-anchor="middle" font-weight="bold">{idx}</text>')
            else:
                svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#374151"/>')

    # labels
    for col in range(4):
        x, _ = xy(3.85, col)
        svg.append(f'<text x="{x:.1f}" y="{size - 3}" font-size="10" '
                   f'fill="#9ca3af" text-anchor="middle">{col}</text>')
    for row in range(4):
        _, y = xy(row, -0.4)
        svg.append(f'<text x="{size - 6}" y="{y + 4}" font-size="10" '
                   f'fill="#9ca3af" text-anchor="end">{row}</text>')

    svg.append("</svg>")
    return "".join(svg)


def is_adjacent(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 and \
           (a[0] == b[0] or a[1] == b[1])  # row OR col changes (not diagonal)


def init_state(m=4, path=None):
    p = path or DEFAULT_PATH
    return ZigguPuzzle(m=m, path=p if path else None)


# ── session state ──────────────────────────────────────────────────────────────
STATE_VERSION = 2
if st.session_state.get("_v") != STATE_VERSION:
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state._v = STATE_VERSION
    st.session_state.puzzle = None
    st.session_state.active_path = None
    st.session_state.draw_path = []

if "puzzle" not in st.session_state:
    st.session_state.puzzle = None
if "active_path" not in st.session_state:
    st.session_state.active_path = None
if "draw_path" not in st.session_state:
    st.session_state.draw_path = []

puzzle = st.session_state.puzzle
active_path = st.session_state.active_path

# ── top bar ────────────────────────────────────────────────────────────────────
st.title("Ziggu Mazes")
top = st.columns([2, 2, 1, 1])
with top[0]:
    m = st.slider("Mazes (m)", 1, 8, puzzle.m if puzzle else 4)
with top[2]:
    st.write("")
    if puzzle and st.button("Reset", use_container_width=True):
        st.session_state.puzzle = ZigguPuzzle(m=m, path=active_path)
        st.rerun()

# rebuild puzzle if m changed
if puzzle and puzzle.m != m:
    st.session_state.puzzle = ZigguPuzzle(m=m, path=active_path)
    puzzle = st.session_state.puzzle
    puzzle = st.session_state.puzzle

# ── maze shape editor ──────────────────────────────────────────────────────────
if True:
    st.divider()
    st.subheader("Maze Shape Editor")
    st.caption("Click cells in order to draw your path. **Green = start**, **orange = exit**. Each cell must be adjacent (no diagonals).")

    draw_path: list = st.session_state.draw_path  # empty by default

    ed_col, ctrl_col = st.columns([2, 3])

    with ed_col:
        st.markdown(
            f"<div style='display:flex;justify-content:center'>{render_editor_svg(draw_path)}</div>",
            unsafe_allow_html=True,
        )

    with ctrl_col:
        st.caption(f"Path: {len(draw_path)} cells")

        # 4x4 button grid (col 3 leftmost, col 0 rightmost)
        for row in range(4):
            btn_cols = st.columns(4)
            for ci, col in enumerate(range(3, -1, -1)):
                cell = (row, col)
                in_path = cell in draw_path
                last = draw_path[-1] if draw_path else None
                can_add = not in_path and (not draw_path or is_adjacent(last, cell))
                is_last_cell = bool(draw_path) and cell == draw_path[-1]

                if in_path:
                    idx = draw_path.index(cell)
                    label = "S" if idx == 0 else ("E" if idx == len(draw_path) - 1 else str(idx))
                elif can_add:
                    label = f"{row},{col}"
                else:
                    label = "·"

                disabled = not (can_add or is_last_cell)
                if btn_cols[ci].button(label, key=f"ed_{row}_{col}", disabled=disabled,
                                       use_container_width=True):
                    if can_add:
                        st.session_state.draw_path.append(cell)
                    elif is_last_cell and len(draw_path) > 1:
                        st.session_state.draw_path.pop()
                    st.rerun()

        action_cols = st.columns(3)
        with action_cols[0]:
            if st.button("↩ Undo", use_container_width=True, disabled=len(draw_path) == 0):
                st.session_state.draw_path.pop()
                st.rerun()
        with action_cols[1]:
            if st.button("Clear", use_container_width=True):
                st.session_state.draw_path = []
                st.rerun()
        with action_cols[2]:
            can_apply = len(draw_path) >= 2
            if st.button("Apply", use_container_width=True, disabled=not can_apply, type="primary"):
                final_path = list(draw_path)  # first = start, last = exit
                st.session_state.active_path = final_path
                active_path = final_path
                st.session_state.puzzle = ZigguPuzzle(m=m, path=final_path)
                puzzle = st.session_state.puzzle
                st.rerun()

# ── maze display ───────────────────────────────────────────────────────────────
st.divider()
if not puzzle or not active_path:
    st.info("Draw a maze shape above and click **Apply** to start.")
else:
    cols = st.columns(m)
    for ui_idx, col in enumerate(cols):
        internal_idx = ui_idx
        slide_label = m - ui_idx
        color = color_for(slide_label, m)
        pos = puzzle.positions[internal_idx]

        with col:
            st.markdown(
                f"<div style='text-align:center;font-weight:600;color:{color};margin-bottom:4px'>"
                f"Maze {slide_label}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='display:flex;justify-content:center'>"
                f"{render_maze_svg(pos, color, active_path)}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align:center;font-family:monospace;font-size:13px;"
                f"margin-top:4px'>({pos[0]}, {pos[1]})</div>",
                unsafe_allow_html=True,
            )
            b1, b2 = st.columns(2)
            with b1:
                if st.button("− back", key=f"back_{internal_idx}",
                             disabled=not puzzle.can_move(internal_idx, -1),
                             use_container_width=True):
                    puzzle.move(internal_idx, -1)
                    st.rerun()
            with b2:
                if st.button("+ fwd", key=f"fwd_{internal_idx}",
                             disabled=not puzzle.can_move(internal_idx, +1),
                             use_container_width=True):
                    puzzle.move(internal_idx, +1)
                    st.rerun()

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Moves", puzzle.moves)
    c2.metric("State string", puzzle.state_string())
    c3.metric("Solved?", "YES 🎉" if puzzle.is_solved() else "no")

with st.expander("How it works"):
    st.markdown("""
- Each maze is a path on a 4×4 grid. The **green circle** marks the start; the **orange square** marks the exit.
- Mazes are coupled: **column of maze *i* = row of maze *i+1***. Moving one piece can cascade into the neighbor.
- **+ fwd / − back** steps a piece one position along the path. Illegal moves are disabled.
- Use **Edit maze shape** to draw a custom path (click cells in sequence — must be grid-adjacent, no diagonals).
    """)
