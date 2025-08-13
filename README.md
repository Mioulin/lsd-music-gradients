# LSD + Music: Gradient-Based fMRI Analysis

Reproducible scaffold for the analysis described in **Chapter 2** of my PhD: validation and application of gradient-based analysis for assessing LSD‑induced changes in brain connectivity during music listening. The repository is designed as a **portfolio-quality** public project: clean structure, CI, tests, docs, and a novice-friendly quickstart.

> Code is MIT-licensed. Text in `/paper` is CC BY 4.0.

## Highlights

- 📦 Python package (`src/lsd_music_gradients`) with CLI via `typer`
- 🧪 Tests (`pytest`), linting (`ruff`), formatting (`black`), pre-commit hooks
- ⚙️ Pip or Conda setup; GitHub Actions CI out of the box
- 📚 Docs with MkDocs + Material theme
- 🧠 Methods implemented as modular utilities:
  - Global Functional Connectivity (GFC) & Modularity
  - Gradient embeddings (BrainSpace) & alignment
  - Gradient-projected time courses & Euclidean dynamics

## Quickstart

```bash
# clone your fork
git clone https://github.com/<your-username>/lsd-music-gradients.git
cd lsd-music-gradients

# create environment (pip)
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# (optional) install pre-commit
pre-commit install

# editable install
pip install -e .

# smoke test
lsdgradients --help
pytest -q
```

## Minimal usage example

```bash
# 1) Compute GFC & modularity from a 100x100 FC matrix (CSV/NPY)
lsdgradients connectivity --fc path/to/fc.npy --atlas Schaefer100 --out outputs/connectivity.json

# 2) Build gradient space from FC and export top-3 gradients
lsdgradients gradients --fc path/to/fc.npy --method pca --out outputs/gradients.npz

# 3) Project ROI×time data into gradient space and compute dynamics
lsdgradients dynamics --roi-ts path/to/roi_by_time.npy --grad outputs/gradients.npz --out outputs/dynamics.json
```

> Data are **not** shipped. See `data/README.md` for pointers to public datasets and expected formats.

## Project map

```
lsd-music-gradients/
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── CITATION.cff
├── LICENSE
├── LICENSE-DOCS
├── README.md
├── requirements.txt
├── mkdocs.yml
├── docs/
│   ├── index.md
│   └── methods.md
├── src/lsd_music_gradients/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── connectivity.py
│   ├── gradients.py
│   └── dynamics.py
├── tests/
│   ├── test_imports.py
│   └── test_cli.py
├── notebooks/
│   └── README.md
├── data/
│   └── README.md
├── outputs/
│   └── .gitkeep
└── paper/
    └── chapter-2/
        ├── README.md
        └── figures/
```

## Citation

If you use this repository, please cite the thesis chapter (details TBD in `CITATION.cff`).
