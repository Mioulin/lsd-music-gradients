"""gradient_similarity.py

Compute similarity metrics (Pearson correlation and/or Euclidean distance)
between **subject‑level functional gradients** and a reference (or between
pairs of subject gradients).

The tool expects each subject's gradient as a standalone NumPy array (``.npy``)
of length **P** (number of parcels). A typical workflow might be:

1. Derive parcelwise gradients for each subject (e.g. via BrainSpace).
2. Save the principal gradient for every subject to ``gradients/<subject>.npy``.
3. Run ``gradient_similarity.py`` to quantify alignment with a normative
   gradient (e.g. HCP‑Young Adult) *or* across two experimental groups.

Examples
========

**Against a reference**
-----------------------
```
python gradient_similarity.py \
    --grad-dir gradients/lsd \
    --reference grad_reference.npy \
    --out correlations_lsd.tsv
```

**Group‑to‑group comparison** (e.g. LSD vs Placebo)
---------------------------------------------------
```
python gradient_similarity.py \
    --grad-dir gradients/lsd gradients/placebo \
    --metric both \
    --out group_similarity.tsv
```

CLI Arguments
-------------
```
--grad-dir   One or more directories containing <subject>.npy gradient files.
--reference  Optional reference gradient (.npy or text). If omitted and two
             grad‑dirs are supplied, the script computes pairwise metrics
             between *matched* subjects across the two directories.
--metric     Which metric(s) to compute: 'corr', 'euclid', or 'both'.
--out        Output TSV (default: gradient_similarity.tsv)
```

Output format
-------------
The result table contains one row per subject (or subject pair) with columns:
```
subject   group   corr   euclid
```
Columns for unused metrics are omitted.

Dependencies
------------
* numpy
* pandas
* scipy
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import zscore, pearsonr
from typing import Dict, List


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute similarity between subject gradients and a reference or between two groups.")
    p.add_argument(
        "--grad-dir",
        nargs='+',
        required=True,
        type=Path,
        help="One or more directories each containing <subject>.npy gradient files.",
    )
    p.add_argument(
        "--reference",
        type=Path,
        default=None,
        help="Optional reference gradient (.npy or text). If omitted and exactly two --grad-dir given, computes pairwise metrics between matched subjects.",
    )
    p.add_argument(
        "--metric",
        choices=["corr", "euclid", "both"],
        default="corr",
        help="Which metric(s) to compute (default: corr).",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("gradient_similarity.tsv"),
        help="Output TSV filename.",
    )
    return p.parse_args()


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def load_gradient(path: Path) -> np.ndarray:
    """Load 1‑D gradient from .npy, .txt, or .csv and z‑score it."""
    if path.suffix == ".npy":
        vec = np.load(str(path))
    else:
        vec = np.loadtxt(str(path))
    return zscore(vec)


def collect_subject_gradients(directory: Path) -> Dict[str, np.ndarray]:
    """Return mapping {*subject*: gradient ndarray}. Subject = filename stem."""
    grads = {}
    for f in sorted(directory.glob("*.npy")):
        grads[f.stem] = load_gradient(f)
    if not grads:
        raise FileNotFoundError(f"No .npy gradients found in {directory}")
    return grads


def similarity(a: np.ndarray, b: np.ndarray, metric: str) -> Dict[str, float]:
    """Compute requested similarity metric(s) between two vectors."""
    res = {}
    if metric in ("corr", "both"):
        res["corr"] = float(pearsonr(a, b)[0])
    if metric in ("euclid", "both"):
        res["euclid"] = float(np.linalg.norm(a - b))
    return res


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # Load gradients per directory
    group_gradients: List[Dict[str, np.ndarray]] = [collect_subject_gradients(d) for d in args.grad_dir]
    group_names = [d.name for d in args.grad_dir]

    if args.reference is not None:
        ref = load_gradient(args.reference)
        out_rows = []
        for gname, grads in zip(group_names, group_gradients):
            for subj, vec in grads.items():
                if vec.shape != ref.shape:
                    raise ValueError(f"Gradient length mismatch for {subj}: {vec.shape} vs {ref.shape}")
                metrics = similarity(vec, ref, args.metric)
                out_rows.append({"subject": subj, "group": gname, **metrics})

    else:
        # Reference not provided: expect exactly two groups and match subjects by stem
        if len(group_gradients) != 2:
            raise ValueError("Without --reference, exactly two --grad-dir must be supplied.")
        grads_a, grads_b = group_gradients
        name_a, name_b = group_names
        shared_subjects = set(grads_a.keys()) & set(grads_b.keys())
        if not shared_subjects:
            raise ValueError("No overlapping subject filenames between groups.")
        out_rows = []
        for subj in sorted(shared_subjects):
            vec_a = grads_a[subj]
            vec_b = grads_b[subj]
            if vec_a.shape != vec_b.shape:
                raise ValueError(f"Gradient length mismatch for {subj}: {vec_a.shape} vs {vec_b.shape}")
            metrics = similarity(vec_a, vec_b, args.metric)
            out_rows.append({"subject": subj, "groupA": name_a, "groupB": name_b, **metrics})

    # Save
    df = pd.DataFrame(out_rows)
    df.to_csv(args.out, sep="\t", index=False)
    print(f"Saved similarity metrics to {args.out.resolve()} (N={len(df)})")


if __name__ == "__main__":
    main()
