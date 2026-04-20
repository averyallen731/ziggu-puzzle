"""Streamlit UI for the Ziggu maze puzzle simulator."""
import streamlit as st
import streamlit.components.v1 as components
from ziggu import ZigguPuzzle

st.set_page_config(page_title="Ziggu Mazes", layout="wide")

MAZE_COLORS = ["#1a56db", "#2e8b3d", "#e08a1a", "#b22222",
               "#6a1b9a", "#00838f", "#c62828", "#4e342e"]
CELL_SIZE = 180


def color_for(slide_label, m):
    return MAZE_COLORS[(m - slide_label) % len(MAZE_COLORS)]


def is_adjacent(a, b):
    return (abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 and
            (a[0] == b[0] or a[1] == b[1]))


def render_maze_svg(pos, color, path, size=CELL_SIZE):
    cell = size / 4

    def xy(row, col):
        return (3 - col) * cell + cell / 2, row * cell + cell / 2

    s = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<rect x="2" y="2" width="{size-4}" height="{size-4}" rx="6" fill="white" stroke="{color}" stroke-width="2" opacity="0.15"/>')
    pts = [xy(r, c) for r, c in path]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    s.append(f'<path d="{d}" stroke="{color}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.3"/>')
    for r, c in path:
        x, y = xy(r, c)
        if (r, c) == path[0]:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="none" stroke="{color}" stroke-width="2" opacity="0.8"/>')
        elif (r, c) == path[-1]:
            s.append(f'<rect x="{x-5:.1f}" y="{y-5:.1f}" width="10" height="10" fill="{color}" opacity="0.8"/>')
        else:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}" opacity="0.4"/>')
    x, y = xy(*pos)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{color}" stroke="white" stroke-width="2.5"/>')
    for row in range(4):
        s.append(f'<text x="{size-10}" y="{row*cell+cell/2+4}" font-size="11" fill="{color}" text-anchor="end" opacity="0.7">{row}</text>')
    for col in range(4):
        x, _ = xy(3.75, col)
        s.append(f'<text x="{x:.1f}" y="{size-4}" font-size="11" fill="{color}" text-anchor="middle" opacity="0.7">{col}</text>')
    s.append("</svg>")
    return "".join(s)


def render_editor_html(draw_path, size=300):
    cell = size / 4
    path_set = set(draw_path)
    last = draw_path[-1] if draw_path else None

    def xy(row, col):
        return (3 - col) * cell + cell / 2, row * cell + cell / 2

    s = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">']
    s.append(f'<rect width="{size}" height="{size}" fill="#1e1e2e" rx="8"/>')
    for i in range(5):
        v = i * cell
        s.append(f'<line x1="{v:.1f}" y1="0" x2="{v:.1f}" y2="{size}" stroke="#333" stroke-width="1"/>')
        s.append(f'<line x1="0" y1="{v:.1f}" x2="{size}" y2="{v:.1f}" stroke="#333" stroke-width="1"/>')
    if len(draw_path) > 1:
        pts = [xy(r, c) for r, c in draw_path]
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        s.append(f'<path d="{d}" stroke="#60a5fa" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    for row in range(4):
        for col in range(4):
            x, y = xy(row, col)
            cp = (row, col)
            in_path = cp in path_set
            is_last = cp == last
            is_first = bool(draw_path) and cp == draw_path[0]
            can_add = not in_path and (not draw_path or is_adjacent(last, cp))
            can_click = can_add or (is_last and len(draw_path) > 1)
            if is_first:
                fill, rsz = "#22c55e", 16
            elif is_last and len(draw_path) > 1:
                fill, rsz = "#f97316", 16
            elif in_path:
                fill, rsz = "#60a5fa", 14
            elif can_add:
                fill, rsz = "#4b5563", 13
            else:
                fill, rsz = "#1f2937", 9
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rsz}" fill="{fill}"/>')
            if in_path:
                idx = draw_path.index(cp)
                lbl = "S" if idx == 0 else ("E" if idx == len(draw_path)-1 else str(idx))
                s.append(f'<text x="{x:.1f}" y="{y+4:.1f}" font-size="12" fill="white" text-anchor="middle" font-weight="bold">{lbl}</text>')
            elif can_add:
                s.append(f'<text x="{x:.1f}" y="{y+4:.1f}" font-size="9" fill="#9ca3af" text-anchor="middle">{row},{col}</text>')
            cur = "pointer" if can_click else "default"
            cb = f"go({row},{col})" if can_click else ""
            s.append(f'<rect x="{x-cell/2:.1f}" y="{y-cell/2:.1f}" width="{cell:.1f}" height="{cell:.1f}" fill="transparent" cursor="{cur}" onclick="{cb}"/>')
    for col in range(4):
        x, _ = xy(3.88, col)
        s.append(f'<text x="{x:.1f}" y="{size-2}" font-size="9" fill="#6b7280" text-anchor="middle">{col}</text>')
    for row in range(4):
        _, y = xy(row, -0.35)
        s.append(f'<text x="{size-4}" y="{y+3:.1f}" font-size="9" fill="#6b7280" text-anchor="end">{row}</text>')
    s.append("</svg>")
    svg = "".join(s)
    return f"""<!DOCTYPE html><html><head><style>body{{margin:0;background:transparent;}}</style></head>
<body>{svg}
<script>
function go(r,c){{
  var u=new URL(window.parent.location.href);
  u.searchParams.set('cell_click',r+','+c);
  window.parent.location.href=u.toString();
}}
</script></body></html>"""


# ── session state ──────────────────────────────────────────────────────────────
STATE_VERSION = 4
if st.session_state.get("_v") != STATE_VERSION:
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.session_state._v = STATE_VERSION
    st.session_state.puzzle = None
    st.session_state.active_path = None
    st.session_state.draw_path = []

for key, default in [("puzzle", None), ("active_path", None), ("draw_path", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── handle cell click ──────────────────────────────────────────────────────────
cc = st.query_params.get("cell_click", "")
if cc:
    row, col = map(int, cc.split(","))
    cp = (row, col)
    dp = st.session_state.draw_path
    last = dp[-1] if dp else None
    if cp not in dp and (not dp or is_adjacent(last, cp)):
        st.session_state.draw_path.append(cp)
    elif dp and cp == dp[-1] and len(dp) > 1:
        st.session_state.draw_path.pop()
    del st.query_params["cell_click"]
    st.rerun()

puzzle = st.session_state.puzzle
active_path = st.session_state.active_path

# ── top bar ────────────────────────────────────────────────────────────────────
st.title("Ziggu Mazes")
top = st.columns([3, 1])
with top[0]:
    m = st.slider("Mazes (m)", 1, 8, puzzle.m if puzzle else 4)
with top[1]:
    st.write("")
    if puzzle and st.button("Reset", use_container_width=True):
        st.session_state.puzzle = ZigguPuzzle(m=m, path=active_path)
        st.rerun()

if puzzle and puzzle.m != m:
    st.session_state.puzzle = ZigguPuzzle(m=m, path=active_path)
    puzzle = st.session_state.puzzle

# ── editor ─────────────────────────────────────────────────────────────────────
st.divider()
st.subheader("Maze Shape Editor")
st.caption("Click cells to draw path. **S** = start · **E** = exit · click E to undo.")

draw_path = st.session_state.draw_path
ed_col, ctrl_col = st.columns([1, 1])

with ed_col:
    components.html(render_editor_html(draw_path), height=320)

with ctrl_col:
    st.markdown(f"**{len(draw_path)} cells**" + (f"  `{'→'.join(str(p) for p in draw_path)}`" if draw_path else ""))
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("Undo", use_container_width=True, disabled=not draw_path):
            st.session_state.draw_path.pop()
            st.rerun()
    with a2:
        if st.button("Clear", use_container_width=True, disabled=not draw_path):
            st.session_state.draw_path = []
            st.rerun()
    with a3:
        if st.button("Apply", use_container_width=True, disabled=len(draw_path) < 2, type="primary"):
            st.session_state.active_path = list(draw_path)
            st.session_state.puzzle = ZigguPuzzle(m=m, path=draw_path)
            active_path = list(draw_path)
            puzzle = st.session_state.puzzle
            st.rerun()

# ── maze display ───────────────────────────────────────────────────────────────
st.divider()
if not puzzle or not active_path:
    st.info("Draw a maze shape above and click **Apply** to start.")
else:
    cols = st.columns(m)
    for ui_idx, col in enumerate(cols):
        slide_label = m - ui_idx
        color = color_for(slide_label, m)
        pos = puzzle.positions[ui_idx]
        with col:
            st.markdown(f"<div style='text-align:center;font-weight:600;color:{color};margin-bottom:4px'>Maze {slide_label}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='display:flex;justify-content:center'>{render_maze_svg(pos, color, active_path)}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-family:monospace;font-size:13px;margin-top:4px'>({pos[0]}, {pos[1]})</div>", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                if st.button("− back", key=f"back_{ui_idx}", disabled=not puzzle.can_move(ui_idx, -1), use_container_width=True):
                    puzzle.move(ui_idx, -1)
                    st.rerun()
            with b2:
                if st.button("+ fwd", key=f"fwd_{ui_idx}", disabled=not puzzle.can_move(ui_idx, +1), use_container_width=True):
                    puzzle.move(ui_idx, +1)
                    st.rerun()
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Moves", puzzle.moves)
    c2.metric("State string", puzzle.state_string())
    c3.metric("Solved?", "YES 🎉" if puzzle.is_solved() else "no")
