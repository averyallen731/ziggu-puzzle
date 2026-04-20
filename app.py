"""Streamlit UI for the Ziggu maze puzzle simulator."""
import streamlit as st
from ziggu import ZigguPuzzle, S_PATH, VALID_CELLS

st.set_page_config(page_title="Ziggu Mazes", layout="wide")

MAZE_COLORS = [
    "#1f4fb8",  # blue   - Maze m (leftmost)
    "#2e8b3d",  # green
    "#e08a1a",  # orange
    "#b22222",  # red    - Maze 1 (rightmost)
    "#6a1b9a",  # purple
    "#00838f",  # teal
    "#c62828",  # crimson
    "#4e342e",  # brown
]


def color_for(slide_label: int) -> str:
    # slide_label: 1..m; color cycle matches slide 33 (blue, green, orange, red)
    return MAZE_COLORS[(slide_label - 1) % len(MAZE_COLORS)]


def render_maze_svg(pos, color, size=180):
    cell = size / 4
    r, c = pos
    # column label 0 is rightmost per paper; x increases right, so x = (3 - c) * cell
    def xy(row, col):
        return (3 - col) * cell + cell / 2, row * cell + cell / 2

    svg = [f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">']
    svg.append(f'<rect x="0" y="0" width="{size}" height="{size}" fill="white" stroke="#ddd"/>')

    # draw S path
    pts = [xy(rr, cc) for (rr, cc) in S_PATH]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    svg.append(f'<path d="{d}" stroke="{color}" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.35"/>')

    # draw valid cell dots
    for (rr, cc) in VALID_CELLS:
        x, y = xy(rr, cc)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}" opacity="0.5"/>')

    # current position
    x, y = xy(r, c)
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{color}" stroke="white" stroke-width="2"/>')

    # row labels on right side
    for row in range(4):
        svg.append(f'<text x="{size - 10}" y="{row * cell + cell / 2 + 4}" font-size="11" fill="{color}" text-anchor="end">{row}</text>')
    # column labels on bottom
    for col in range(4):
        x = (3 - col) * cell + cell / 2
        svg.append(f'<text x="{x:.1f}" y="{size - 4}" font-size="11" fill="{color}" text-anchor="middle">{col}</text>')

    svg.append("</svg>")
    return "".join(svg)


def main():
    st.title("Ziggu Mazes")
    st.caption("Based on Goertz & Williams, 'The Quaternary Gray Code and Ziggu Puzzles' (FUN 2026), §4.")

    with st.sidebar:
        m = st.slider("Number of mazes (m)", 1, 8, 4)
        if st.button("Reset"):
            st.session_state.pop("puzzle", None)

    if "puzzle" not in st.session_state or st.session_state.puzzle.m != m:
        st.session_state.puzzle = ZigguPuzzle(m=m)

    puzzle: ZigguPuzzle = st.session_state.puzzle

    # Layout: leftmost in UI is Maze m; rightmost is Maze 1 (matches slide 33).
    cols = st.columns(m)
    for ui_idx, col in enumerate(cols):
        internal_idx = ui_idx  # left-to-right matches our internal list
        slide_label = m - ui_idx  # leftmost is Maze m
        color = color_for(slide_label)
        pos = puzzle.positions[internal_idx]
        with col:
            st.markdown(
                f"<div style='text-align:center;font-weight:600;color:{color}'>Maze {slide_label}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='display:flex;justify-content:center'>{render_maze_svg(pos, color)}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='text-align:center;font-family:monospace'>({pos[0]}, {pos[1]})</div>",
                unsafe_allow_html=True,
            )
            b1, b2 = st.columns(2)
            with b1:
                if st.button("− back", key=f"back_{internal_idx}", disabled=not puzzle.can_move(internal_idx, -1), use_container_width=True):
                    puzzle.move(internal_idx, -1)
                    st.rerun()
            with b2:
                if st.button("+ fwd", key=f"fwd_{internal_idx}", disabled=not puzzle.can_move(internal_idx, +1), use_container_width=True):
                    puzzle.move(internal_idx, +1)
                    st.rerun()

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Moves", puzzle.moves)
    c2.metric("State string", puzzle.state_string())
    c3.metric("Solved?", "YES" if puzzle.is_solved() else "no")

    with st.expander("How it works"):
        st.markdown(
            """
- Each maze is an S-shaped path on a 4×4 grid with 13 valid cells
  (position `(3, y)` is only valid when `y = 3`).
- The current position of maze *i* is coupled to its right neighbor:
  `row(i) == col(i+1)`. Only the rightmost maze has a free column.
- **+ fwd** / **− back** moves that maze one step along its S-path, and
  the coupling with neighbors is automatically enforced.
  Moves that would violate the coupling are disabled.
- **State string**: `c₁ r₁ r₂ … rₘ` as defined in the paper (base-4, length `m+1`).
  Start state is `00…0`; target is `33…3`.
            """
        )


if __name__ == "__main__":
    main()
