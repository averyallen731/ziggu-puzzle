# Ziggu Mazes Simulator

An interactive simulator for the Ziggu maze puzzle family (Ziggurat, Zigguflat, Zigguhooked, …), based on §4 of Goertz & Williams, *The Quaternary Gray Code and Ziggu Puzzles* (FUN 2026).

Built with Streamlit.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (free)

1. Push this repo to GitHub.
2. Go to https://share.streamlit.io, sign in with GitHub, click **New app**, point it at this repo (`app.py`), deploy. You get a public URL you can share with your class.

## How the puzzle works

Each maze is an S-shape on a 4×4 grid with 13 valid cells. `m` mazes are connected via the rule **row of maze *i* = column of maze *i+1***, so moving one piece can cascade into the next. Only the rightmost maze has a free column. Start state is all `(0, 0)`; target is all `(3, 3)`.
