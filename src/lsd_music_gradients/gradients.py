from __future__ import annotations
import numpy as np
from sklearn.decomposition import PCA

def affinity_from_fc(fc: np.ndarray, metric: str = "normalized_angle") -> np.ndarray:
    # Simple cosine-like similarity for demo purposes
    # Normalize rows
    X = fc - fc.mean(axis=1, keepdims=True)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X @ X.T

def gradient_embedding(affinity: np.ndarray, n_components: int = 3, method: str = "pca") -> np.ndarray:
    if method != "pca":
        # placeholder: pca only in stub
        method = "pca"
    pca = PCA(n_components=n_components, random_state=0)
    return pca.fit_transform(affinity)
