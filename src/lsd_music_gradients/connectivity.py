from __future__ import annotations
import json
import numpy as np
import networkx as nx
from typing import Dict

def load_fc(path: str) -> np.ndarray:
    if path.endswith('.npy'):
        return np.load(path)
    elif path.endswith('.csv'):
        return np.loadtxt(path, delimiter=',')
    else:
        raise ValueError("FC must be .npy or .csv")

def global_functional_connectivity(fc: np.ndarray) -> float:
    assert fc.shape[0] == fc.shape[1], "FC must be square"
    # fisher z of upper triangle (excluding diag)
    iu = np.triu_indices_from(fc, k=1)
    r = fc[iu]
    z = np.arctanh(np.clip(r, -0.999999, 0.999999))
    return float(np.nanmean(z))

def modularity_louvain(fc: np.ndarray) -> float:
    # build weighted graph; simple positive-edges only for demo
    W = np.clip(fc, 0, None)
    G = nx.from_numpy_array(W)
    try:
        import networkx.algorithms.community as nx_comm
        parts = nx_comm.louvain_communities(G, weight="weight", seed=42)
        # convert to dict for modularity
        communities = {i: set(c) for i, c in enumerate(parts)}
        return nx.algorithms.community.quality.modularity(G, communities.values(), weight="weight")
    except Exception:
        return float("nan")

def save_json(d: Dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)
