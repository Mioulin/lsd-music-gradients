from dataclasses import dataclass

@dataclass
class AtlasConfig:
    name: str = "Schaefer100"
    n_rois: int = 100
