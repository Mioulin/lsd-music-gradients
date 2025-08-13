
from __future__ import annotations
import json
import numpy as np
from typing import Dict

def project_timecourses(roi_by_time: np.ndarray, gradients: np.ndarray) -> np.ndarray:
    """
    Project ROI x time signals (n_rois x T) into gradient space (n_rois x k).
    Returns array of shape (k, T) with projected components.
    """
    assert roi_by_time.shape[0] == gradients.shape[0], "ROI dimension mismatch"
    return gradients.T @ roi_by_time

def per_gradient_std(proj: np.ndarray) -> np.ndarray:
    """Standard deviation per gradient component (length-k vector)."""
    return proj.std(axis=1)

def mean_euclidean_step(proj: np.ndarray) -> float:
    """
    Mean Euclidean step between consecutive frames in gradient space.
    proj has shape (k, T).
    """
    steps = np.linalg.norm(np.diff(proj, axis=1), axis=0)
    return float(steps.mean())

def save_json(d: Dict, path: str) -> None:
    """Save a dictionary to JSON with pretty formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
