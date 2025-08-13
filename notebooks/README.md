# Neuro‑Music Toolkit

*A modular, command‑line pipeline for parcel‑wise fMRI time‑series, connectivity, and gradient analysis*

---

## 1. Overview

This repository bundles **four interoperable Python scripts** that convert raw 4‑D fMRI runs into high‑level metrics used in music‑psychedelic neuroimaging studies.  Each script is self‑contained, atlas‑agnostic, and documented via a CLI help page (`-h`).  They can be chained or used à la carte:

```
NIfTI → (1) time‑series → (2) connectivity metrics ↘
                                   ↘             ↘
                                     gradients   ↘
                                   (3) corr vs ref
                                   (4) subject similarities
```

| Level  | Script                       | Purpose                                                                                          | Typical Output                                             |
| ------ | ---------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| **1**  | `extract_timeseries.py`      | Extract ROI × time matrices from NIfTI files with any volumetric atlas                           | `timeseries.pkl` (nested dict)                             |
| **2**  | `functional_connectivity.py` | Compute Global Functional Connectivity (GFC) & simplified modularity                             | `metrics/global_fc.tsv`, `metrics/modularity.tsv`          |
| **3a** | `gradient_analysis.py`       | Correlate each TR with a reference gradient, summarise Fisher‑z                                  | `gradient_correlations.tsv` + optional `corr_series/*.npy` |
| **3b** | `gradient_similarity.py`     | Pearson / Euclidean similarity between subject gradients & a reference **or** between two groups | `gradient_similarity.tsv`                                  |

---

## 2. Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install nilearn nibabel numpy pandas scipy tqdm brainspace
```

Each script lists its minimal deps in the header; `requirements.txt` can be generated later via `pip freeze > requirements.txt`.

---

## 3. Folder conventions

```
.
├── data/
│   ├── atlas/
│   │   ├── Schaefer2018_400.nii.gz
│   │   └── Schaefer2018_400_labels.txt  # optional
│   ├── lsd/        # 4‑D runs (*.nii*)
│   └── placebo/
├── gradients/      # subject gradient .npy (optional)
├── metrics/        # generated tables
├── extract_timeseries.py
├── functional_connectivity.py
├── gradient_analysis.py
├── gradient_similarity.py
└── README.md
```

*Feel free to rename/relocate; all paths are explicit CLI args.*

---

## 4. Quick‑start pipeline 🏃‍♂️

### 4.1 Time‑series extraction

```bash
python extract_timeseries.py \
  --atlas data/atlas/Schaefer2018_400.nii.gz \
  --labels data/atlas/Schaefer2018_400_labels.txt \
  --input-dirs data/lsd data/placebo \
  --output timeseries_music.pkl \
  --standardize            # optional z‑score per ROI
```

### 4.2 Connectivity metrics

```bash
python functional_connectivity.py \
  --timeseries timeseries_music.pkl \
  --network-map schaefer100_yeo7.tsv \
  --out-dir metrics/
```

### 4.3 Gradient analyses

#### (a) Correlation vs reference over time

```bash
python gradient_analysis.py \
  --timeseries timeseries_music.pkl \
  --gradient grad_hcp.npy \
  --output correlations.tsv \
  --save-series            # per‑TR .npy
```

#### (b) Subject‑level gradient similarity

```bash
# Against reference
python gradient_similarity.py \
  --grad-dir gradients/lsd \
  --reference grad_hcp.npy \
  --metric both \
  --out similarity_lsd.tsv

# Pairwise LSD vs Placebo (no reference needed)
python gradient_similarity.py \
  --grad-dir gradients/lsd gradients/placebo \
  --metric corr \
  --out lsd_vs_placebo_corr.tsv
```

---

## 5. Script cheat‑sheet

<details>
<summary><code>extract_timeseries.py</code></summary>

```
--atlas        <NIfTI>    # integer‑labelled parcellation
--labels       <txt/tsv>  # optional ROI names
--input-dirs   dir1 dir2  # each 4‑D run folder
--pattern      *.nii*     # glob (default)
--standardize             # z‑score time‑series
--output       timeseries.pkl
```

</details>

<details>
<summary><code>functional_connectivity.py</code></summary>

```
--timeseries   timeseries.pkl
--network-map  <csv/tsv>  # parcel→network (optional)
--out-dir      metrics/
```

</details>

<details>
<summary><code>gradient_analysis.py</code></summary>

```
--timeseries   timeseries.pkl
--gradient     grad_ref.npy  # 1‑D (parcels)
--output       gradient_correlations.tsv
--save-series  (flag)
```

</details>

<details>
<summary><code>gradient_similarity.py</code></summary>

```
--grad-dir   grp1/ [grp2/]   # ≥1 dirs with <subject>.npy
--reference  grad_ref.npy    # optional
--metric     corr|euclid|both (default corr)
--out        gradient_similarity.tsv
```

</details>

---

## 6. Tips & Notes

* **Atlas‑agnostic:** all scripts assume the same parcel ordering across data, labels, network maps, and gradients.
* **Memory:** `extract_timeseries.py` streams runs via *nilearn*; whole‑brain correlation matrices for high‑parcel atlases may consume RAM—consider subsampling or chunking.
* **Modularity metric:** implemented as mean within‑network FC minus mean between‑network FC; swap in a graph‑theoretic modularity if needed.

---

## 7. License

MIT — do whatever you want; credit appreciated.

---

### Citation

If you use this toolkit, please cite the underlying atlases (e.g., Schaefer 2018), *nilearn*, *BrainSpace*, and any reference gradients employed.
