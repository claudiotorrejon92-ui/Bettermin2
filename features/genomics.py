"""
Metagenomic vectorisation utilities using hashing and dimensionality reduction.

The functions here turn DNA/RNA sequences into numeric feature vectors via
hashed k‑mer counts and reduce their dimensionality with PCA or UMAP.
"""

from typing import Iterable, List

import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_extraction import FeatureHasher

try:  # UMAP is optional at runtime but recommended
    import umap
except Exception:  # pragma: no cover - handled gracefully if missing
    umap = None


def _kmers(seq: str, k: int) -> List[str]:
    return [seq[i : i + k] for i in range(len(seq) - k + 1)]


def hash_sequences(seqs: Iterable[str], n_features: int = 1024, k: int = 6) -> np.ndarray:
    """Hash sequences into a sparse numeric matrix of k‑mers."""
    hasher = FeatureHasher(n_features=n_features, input_type="string")
    docs = [_kmers(s, k) for s in seqs]
    return hasher.transform(docs).toarray()


def reduce_dimensions(matrix: np.ndarray, method: str = "pca", n_components: int = 50, random_state: int = 42) -> np.ndarray:
    """Reduce dimensionality of hashed features using PCA or UMAP."""
    if method == "pca":
        model = PCA(n_components=n_components, random_state=random_state)
    elif method == "umap":
        if umap is None:
            raise ImportError("UMAP is not installed")
        model = umap.UMAP(n_components=n_components, random_state=random_state)
    else:
        raise ValueError("method must be 'pca' or 'umap'")
    return model.fit_transform(matrix)
