# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np
import pytest

from src.io.reader.ascii import read_ascii
from src.model.spline_xd import SplineXD
from test_files import tmc_traj_100


@pytest.fixture
def trajectory():
    df = read_ascii(tmc_traj_100, row_skip=1, delimiter=r",", point_format=324,
                    dimension_names=["gps_time", "roll", "pitch", "yaw", "X", "Y", "Z"])
    return df


def test_spline3D(trajectory):
    spline3d = SplineXD.build(x=trajectory["gps_time"], y=trajectory[["X", "Y", "Z"]], mse_threshold=0.001, error_threshold=0.0001)

    for i, s in trajectory[["gps_time", "X", "Y", "Z"]].iterrows():
        res = spline3d.evaluate(s["gps_time"])
        # print(np.linalg.norm(np.ravel(res) - s[["X", "Y", "Z"]]))
        assert np.allclose(res, s[["X", "Y", "Z"]], atol=0.001)


def test_trajectory_serialization(trajectory, tmp_path):
    from src.model.trajectory import Trajectory
    trajectory = Trajectory(trajectory)
    trajectory.write_to_disk(tmp_path)

@pytest.mark.skip(reason="not implemented")
def test_trajectory_roundtrip(trajectory, tmp_path):
    from src.model.trajectory import Trajectory
    trajectory = Trajectory(trajectory)
    trajectory.write_to_disk(tmp_path)
    trajectory = Trajectory.read_from_disk(tmp_path)
    assert trajectory is not None
    assert len(trajectory) > 0
    assert "gps_time" in trajectory.columns
    assert "X" in trajectory.columns
    assert "Y" in trajectory.columns
    assert "Z" in trajectory.columns
    assert "roll" in trajectory.columns
    assert "pitch" in trajectory.columns
    assert "yaw" in trajectory.columns
    assert "L" in trajectory.columns
    assert "L3D" in trajectory.columns
    assert "time_xyz" in trajectory.splines
    assert "time_L" in trajectory.splines
    assert "time_L3D" in trajectory.splines
    assert "L_time" in trajectory.splines
    assert "L3D_time" in trajectory.splines
    assert "metadata" in trajectory
    assert "gps_time" in trajectory.metadata
    assert "X" in trajectory.metadata
    assert "Y" in trajectory.metadata
    assert "Z" in trajectory.metadata
    assert "roll" in trajectory.metadata
    assert "pitch" in trajectory.metadata
    assert "yaw" in trajectory.metadata
    assert "L" in trajectory.metadata
    assert "L3D" in trajectory.metadata
    assert "time_xyz" in trajectory.metadata
    assert "time_L" in trajectory.metadata
    assert "time_L3D" in trajectory.metadata
    assert "L_time" in trajectory.metadata
    assert "L3D_time" in trajectory.metadata
    assert "metadata.json" in trajectory.files
    assert "time_xyz.json" in trajectory.files
    assert "time_L.json" in trajectory.files
    assert "time_L3D.json" in trajectory.files
    assert "L_time.json" in trajectory.files
    assert "L3D_time.json" in trajectory.files
    assert "gps_time" in trajectory.splines["time_xyz"]
    assert "X" in trajectory.splines["time_xyz"]
    assert "Y" in trajectory.splines["time_xyz"]
    assert "Z" in trajectory.splines["time_xyz"]
    assert "gps_time" in trajectory.splines["time_L"]
