# Methods Summary

- **Functional connectivity:** Pearson correlation of Schaefer-100 parcels; GFC = mean Fisher-z across pairs.
- **Modularity:** Louvain modularity on thresholded/weighted networks (NetworkX placeholder implementation).
- **Gradients:** PCA/diffusion embedding on affinity from FC (via BrainSpace); first 3 components.
- **Alignment:** Optional Procrustes to normative space.
- **Dynamics:** Project ROI×time to gradient components; per-gradient std; mean frame-to-frame Euclidean distance.

> This repo ships *interfaces* and example calls. Replace data paths with your own study data.
