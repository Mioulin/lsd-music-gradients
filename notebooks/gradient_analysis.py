"""gradient_analysis.py

Compute subject‑level alignment between parcel‑wise fMRI time‑series and a reference
connectivity gradient (e.g., the principal gradient from HCP 7T data).

Inputs
------
* timeseries.pkl : Pickle created by *extract_timeseries.py*:
    {
        "group1": { "sub-01": array(T×P), ... },
        "group2": ...
    }
  where P is number of parcels, T timepoints.
* gradient.npy / .txt : 1‑D array of length P with gradient values.

Outputs
-------
* CSV/TSV table summarising, for each group and subject, the average Fisher‑z
  correlation between the gradient vector and parcel signals across time‑points.
* Optionally, per‑TR correlation series saved as .npy for each subject.

Example
-------
python gradient_analysis.py \
    --timeseries timeseries_music.pkl \
    --gradient grad_hcp.npy \
    --output correlations.tsv

The script is atlas‑agnostic: the time‑series and gradient vector must share the
same parcellation and ordering.
"""

from __future__ import annotations
import argparse
from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from scipy.stats import zscore, pearsonr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compute subject‑level correlations between fMRI parcel signals and "
            "a reference gradient."
        )
    )
    parser.add_argument(
        "--timeseries",
        required=True,
        type=Path,
        help="Pickle file produced by extract_timeseries.py",
    )
    parser.add_argument(
        "--gradient",
        required=True,
        type=Path,
        help="1‑D numpy .npy or text file with gradient values (length = parcels)",
    )
    parser.add_argument(
        "--output",
        default="gradient_correlations.tsv",
        type=Path,
        help="Output TSV summarising mean Fisher‑z correlations.",
    )
    parser.add_argument(
        "--save-series",
        action="store_true",
        help="Save per‑timepoint correlation series as .npy for each subject.",
    )
    return parser.parse_args()


def load_gradient(path: Path) -> np.ndarray:
    """Load gradient vector from .npy, .txt, or .csv."""
    if path.suffix == ".npy":
        grad = np.load(str(path))
    else:
        grad = np.loadtxt(str(path))
    return zscore(grad)


def vector_correlate(ts: np.ndarray, gradient: np.ndarray) -> np.ndarray:
    """Correlate each time‑point (row) with the gradient vector.

    Parameters
    ----------
    ts : ndarray, shape (T, P)
        ROI signals.
    gradient : ndarray, shape (P,)
        Reference gradient values.

    Returns
    -------
    ndarray, shape (T,)
        Pearson r for each TR.
    """
    ts_z = zscore(ts, axis=1)
    grad_z = zscore(gradient)
    return np.array([pearsonr(row, grad_z)[0] for row in ts_z])


def main() -> None:
    args = parse_args()
    grad = load_gradient(args.gradient)

    with open(args.timeseries, "rb") as fp:
        ts_dict: dict[str, dict[str, np.ndarray]] = pickle.load(fp)

    results = []
    for group, subjects in ts_dict.items():
        for subj, ts in subjects.items():
            if ts.shape[1] != grad.shape[0]:
                raise ValueError(
                    f"Gradient length {grad.shape[0]} ≠ parcels in {subj} ({ts.shape[1]})"
                )
            corr_series = vector_correlate(ts, grad)
            mean_r = float(np.mean(corr_series))
            mean_z = float(np.arctanh(mean_r))
            results.append(
                {
                    "group": group,
                    "subject": subj,
                    "n_timepoints": int(ts.shape[0]),
                    "mean_r": mean_r,
                    "mean_z": mean_z,
                }
            )

            if args.save_series:
                out_dir = args.output.with_suffix("").parent / "corr_series"
                out_dir.mkdir(parents=True, exist_ok=True)
                np.save(out_dir / f"{group}_{subj}_corr.npy", corr_series)

    df = pd.DataFrame(results)
    df.to_csv(args.output, sep="\t", index=False)
    print(f"Saved summary to {args.output.absolute()} (N = {len(df)} subjects)")


if __name__ == "__main__":
    main()
