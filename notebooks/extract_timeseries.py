"""extract_timeseries.py

Utility script for extracting parcel‑wise fMRI time‑series from a collection of NIfTI
files using the Schaefer atlas (or any 3‑D/4‑D labelled parcellation).

Features
--------
* Supports any NIfTI volumetric atlas with integer labels.
* Handles an arbitrary list of input folders, grouping outputs by folder name.
* Saves output as a compressed pickle (`.pkl`) ready for further analysis.
* Fully configurable from the command line.

Example
-------
>>> python extract_timeseries.py \
        --atlas data/atlas/Schaefer2018_400.nii.gz \
        --labels data/atlas/Schaefer2018_400_labels.txt \
        --input-dirs data/lsd data/placebo \
        --output timeseries_music.pkl
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import pickle
from typing import Dict, List

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn.input_data import NiftiLabelsMasker
from nilearn import image


def parse_args() -> argparse.Namespace:
    """Command‑line interface."""
    parser = argparse.ArgumentParser(
        description="Extract ROI‑wise time‑series from fMRI NIfTI files."
    )
    parser.add_argument(
        "--atlas",
        required=True,
        type=Path,
        help="Path to a volumetric atlas NIfTI file (integer labels).")

    parser.add_argument(
        "--labels",
        type=Path,
        help="Optional text/tsv file with one label per line.")

    parser.add_argument(
        "--input-dirs",
        nargs='+',
        required=True,
        type=Path,
        help="One or more directories containing 4‑D fMRI NIfTI files.")

    parser.add_argument(
        "--output",
        default="timeseries.pkl",
        type=Path,
        help="Output pickle filename (default: timeseries.pkl).")

    parser.add_argument(
        "--pattern",
        default="*.nii*",  # matches .nii and .nii.gz
        help="Glob pattern for selecting fMRI files inside each input directory."
    )

    parser.add_argument(
        "--tr",
        type=float,
        default=None,
        help="Specify TR (repetition time) if the NIfTI header is missing it."
    )

    parser.add_argument(
        "--standardize",
        action="store_true",
        help="Z‑score each ROI time‑series (uses nilearn's standardize option)."
    )

    return parser.parse_args()


def load_labels(label_file: Path) -> List[str]:
    """Load ROI labels from a text/tsv file (one label per line)."""
    with open(label_file, "r", encoding="utf-8") as f:
        labels = [l.strip().split("\t")[-1] for l in f if l.strip()]
    return labels


def build_masker(
    atlas_img: nib.Nifti1Image,
    labels: List[str] | None = None,
    standardize: bool = False
) -> NiftiLabelsMasker:
    """Construct a nilearn NiftiLabelsMasker for the atlas."""
    masker = NiftiLabelsMasker(
        labels_img=atlas_img,
        labels=labels,
        standardize=standardize,
        memory="nilearn_cache",
        memory_level=2,
        verbose=1,
    )
    return masker


def extract_dir(
    directory: Path,
    masker: NiftiLabelsMasker,
    pattern: str
) -> Dict[str, np.ndarray]:
    """Extract time‑series for every NIfTI file in *directory* matching *pattern*.

    Returns
    -------
    dict
        Keys are file stems (filename without extension). Values are
        2‑D numpy arrays shaped (n_timepoints, n_parcels).
    """
    output: Dict[str, np.ndarray] = {}
    for fpath in sorted(directory.glob(pattern)):
        if not fpath.is_file():
            continue
        ts = masker.fit_transform(str(fpath))
        output[fpath.stem] = ts
    return output


def main() -> None:
    args = parse_args()

    # --- Load atlas & labels -------------------------------------------------
    atlas_img = nib.load(str(args.atlas))
    labels = load_labels(args.labels) if args.labels else None

    masker = build_masker(
        atlas_img=atlas_img,
        labels=labels,
        standardize=args.standardize,
    )

    # --- Extract -------------------------------------------------------------
    results: Dict[str, Dict[str, np.ndarray]] = {}

    for dir_path in args.input_dirs:
        if not dir_path.is_dir():
            raise FileNotFoundError(f"Input directory not found: {dir_path}")
        group_name = dir_path.name  # e.g. 'lsd', 'placebo'
        results[group_name] = extract_dir(
            directory=dir_path,
            masker=masker,
            pattern=args.pattern,
        )

    # --- Save ----------------------------------------------------------------
    with open(args.output, "wb") as fp:
        pickle.dump(results, fp)

    print(f"Saved time‑series dictionary to {args.output.absolute()}")


if __name__ == "__main__":
    main()
