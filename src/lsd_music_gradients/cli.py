from __future__ import annotations
import json
import numpy as np
import typer
from .connectivity import load_fc, global_functional_connectivity, modularity_louvain, save_json
from .gradients import affinity_from_fc, gradient_embedding
from .dynamics import project_timecourses, per_gradient_std, mean_euclidean_step, save_json as save_json_dyn

app = typer.Typer()

@app.command()
def connectivity(fc: str = typer.Option(..., help="Path to FC matrix (.npy/.csv)"),
                 atlas: str = typer.Option("Schaefer100", help="Atlas name (metadata only)"),
                 out: str = typer.Option("outputs/connectivity.json", help="Output JSON path")):
    """Compute GFC and modularity from an FC matrix."""
    mat = load_fc(fc)
    gfc = global_functional_connectivity(mat)
    mod = modularity_louvain(mat)
    save_json({"atlas": atlas, "gfc": gfc, "modularity": mod}, out)
    typer.echo(f"Saved {out}")

@app.command()
def gradients(fc: str = typer.Option(..., help="Path to FC matrix (.npy/.csv)"),
              method: str = typer.Option("pca", help="Embedding method (stub: pca)"),
              out: str = typer.Option("outputs/gradients.npz", help="Output NPZ with 'G' array")):
    """Build a gradient embedding (top-3)."""
    if fc.endswith('.npy'):
        mat = np.load(fc)
    else:
        mat = np.loadtxt(fc, delimiter=',')
    aff = affinity_from_fc(mat)
    G = gradient_embedding(affinity=aff, n_components=3, method=method)
    np.savez(out, G=G)
    typer.echo(f"Saved {out}")

@app.command()
def dynamics(roi_ts: str = typer.Option(..., help="Path to ROI×time matrix (.npy)"),
             grad: str = typer.Option(..., help="NPZ from 'gradients' (contains array 'G' of shape [n_rois,3])"),
             out: str = typer.Option("outputs/dynamics.json", help="Output JSON path")):
    """Project ROI×time into gradient space and compute variability metrics."""
    X = np.load(roi_ts)  # shape (n_rois, T)
    G = np.load(grad)["G"]
    proj = project_timecourses(X, G)
    result = {"per_gradient_std": per_gradient_std(proj).tolist(),
              "mean_euclidean_step": mean_euclidean_step(proj)}
    save_json_dyn(result, out)
    typer.echo(f"Saved {out}")

def main():
    app()

if __name__ == "__main__":
    main()
