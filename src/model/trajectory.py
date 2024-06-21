# 20/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
from pathlib import Path

import numpy as np
import pandas as pd

from src.model.spline_2d import Spline2D
from src.io.patches.strict_pos import ensure_strict_pos
from src.model.spline_xd import SplineXD


# noinspection PyPep8Naming
# as L it is the common way of notation
class Trajectory:

    def __init__(self, points: pd.DataFrame, metadata: dict = None):
        assert all([key in points.columns for key in ["gps_time", "X", "Y", "Z"]])
        self.metadata = points.attrs.get("metadata", {})
        self.metadata.update(metadata or {})
        gps_time = ensure_strict_pos(points["gps_time"].to_numpy())
        self.time_xyz = SplineXD.build(points["gps_time"], points[["X", "Y", "Z"]], mse_threshold=0.001, error_threshold=0.001)

        L = np.zeros(len(points))
        if "L" not in points.columns:
            L[1:] = np.cumsum(np.sqrt(np.sum(np.diff(points[['X', 'Y']], axis=0) ** 2, axis=1)))
        else:
            L = points['L'].to_numpy()

        L = ensure_strict_pos(L)
        self.time_L = Spline2D.build(x=gps_time, y=L, mse_threshold=0.001, error_threshold=0.0001)
        self.time_L = Spline2D.build(x=L, y=gps_time, mse_threshold=0.001, error_threshold=0.0001)

        L3D = np.zeros(len(points))
        if "L3D" not in points.columns:
            L3D[1:] = np.cumsum(np.sqrt(np.sum(np.diff(points[['X', 'Y', 'Z']], axis=0) ** 2, axis=1)))
        else:
            L3D = points['L3D'].to_numpy()
        L3D = ensure_strict_pos(L3D)

        self.time_L3D = Spline2D.build(gps_time, L3D, mse_threshold=0.001, error_threshold=0.0001)
        self.L3D_time = Spline2D.build(L3D, gps_time, mse_threshold=0.001, error_threshold=0.0001)

    def write_to_disk(self, path: Path):
        from src.io.writer.npz import write_to_folder
        # noinspection PyTypeChecker
        write_to_folder(path, (
            ("/metadata.json", dict, self.metadata),
            ("/time_xyz.json", SplineXD, self.time_xyz),
            ("/time_L.json", Spline2D, self.time_L),
            ("/L_time.json", Spline2D, self.time_L),
            ("/time_L3D.json", Spline2D, self.time_L3D),
            ("/L3D_time.json", Spline2D, self.L3D_time)
        ))

    @classmethod
    def read_from_disk(cls, tmp_path):
        raise NotImplementedError
