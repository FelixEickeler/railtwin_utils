# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np

from src.io.reader.ascii import read_ascii
from src.io.model.spline_3d import Spline3D
from test_files import tmc_traj_100


def test_spline3D():
    df = read_ascii(tmc_traj_100, row_skip=1, delimiter=r",", point_format=324,
                    dimension_names=["gps_time", "roll", "pitch", "yaw", "X", "Y", "Z"])

    spline3d = Spline3D(t=df["gps_time"], points=df[["X", "Y", "Z"]], estimated_mse=0.001, error_threshold=0.0001)

    for i, s in df[["gps_time", "X", "Y", "Z"]].iterrows():
        res = spline3d.evaluate(s["gps_time"])
        print(np.linalg.norm(np.ravel(res) - s[["X", "Y", "Z"]]))
        assert np.allclose(res, s[["X", "Y", "Z"]], atol=0.001)
