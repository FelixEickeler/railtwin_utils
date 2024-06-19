# 11/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#
import laspy
import numpy as np
from laspy.point.dims import PointFormatDict, _build_point_formats_dtypes, POINT_FORMAT_DIMENSIONS, DIMENSIONS_TO_TYPE
from src.io.reader.ascii import read_ascii

from test.test_files import tmc_traj_100

import pytest


# from src.io.reader.csv import create_csv_reader


def test_create_point_format():
    from laspy.point import dims
    import numpy as np
    dims.DIMENSIONS_TO_TYPE["roll"] = np.dtype("f8")
    dims.DIMENSIONS_TO_TYPE["pitch"] = np.dtype("f8")
    dims.DIMENSIONS_TO_TYPE["yaw"] = np.dtype("f8")

    POINT_FORMAT_TMC = (
        "gps_time",
        "roll",
        "pitch",
        "yaw",
        "X",
        "Y",
        "Z"
    )

    # Register Record Type and the corresponding composed fields. This is only FIELD_NAMES !
    dims.POINT_FORMAT_DIMENSIONS[324] = POINT_FORMAT_TMC
    dims.COMPOSED_FIELDS[324] = {}

    # version of las links to supported FMTs => custom version, for custom fmts
    dims.VERSION_TO_POINT_FMT["CUSTOM"]: ("TMC_TRAJ")

    # For each FMT, names and dtypes as np.dtype
    dims.POINT_FORMATS_DTYPE = PointFormatDict(
        _build_point_formats_dtypes(POINT_FORMAT_DIMENSIONS, DIMENSIONS_TO_TYPE)
    )
    # all FMTs which are supported, just names, same as POINT_FORMAT_DIMENSIONS ist a copy.
    dims.ALL_POINT_FORMATS_DIMENSIONS = PointFormatDict({**dims.POINT_FORMAT_DIMENSIONS})
    # and a copy of POINT_FORMATS_DTYPE, not sure WHY
    dims.ALL_POINT_FORMATS_DTYPE = PointFormatDict({**dims.POINT_FORMATS_DTYPE})
    import laspy
    pf = laspy.point.PointFormat(324)
    assert 324 in laspy.supported_point_formats()


def test_read_tmc_traj():
    POINT_FORMAT_TMC = {
        "gps_time": np.dtype("f8"),
        "roll": np.dtype("f8"),
        "pitch": np.dtype("f8"),
        "yaw": np.dtype("f8"),
        "X": np.dtype("f4"),
        "Y": np.dtype("f4"),
        "Z": np.dtype("f4")
    }

    from src.io.patches.monkey_patch_laspy import CustomPointFormat, patch_laspy_types

    patch_laspy_types({324: POINT_FORMAT_TMC})
    import laspy as claspy  # noqa: E402
    claspy.PointFormat = CustomPointFormat
    df = read_ascii(tmc_traj_100, row_skip=1, delimiter=r",", point_format=324, dimension_names=["gps_time", "roll", "pitch", "yaw", "X", "Y", "Z"])
    assert df.shape == (99, 7)
    assert df["gps_time"].iloc[0] == 551187.063988
    assert df["roll"].iloc[0] == -0.740754
    assert df["pitch"].iloc[0] == -0.501459
    assert df["yaw"].iloc[0] == 66.021689
    assert df["X"].iloc[0] == 4055672.4796 - df.attrs["metadata"]["offset"]["X"]
    assert df["Y"].iloc[0] == 615771.9272 - df.attrs["metadata"]["offset"]["Y"]
    assert df["Z"].iloc[0] == 4867783.8794 - df.attrs["metadata"]["offset"]["Z"]


# def test_laspy_we():
#     from laspy import PointFormat, PackedPointRecord
#     packed_point_record = PackedPointRecord.zeros(10, PointFormat(0))
#     ala = PackedPointRecord.from_point_record(packed_point_record, XYZIRGB)
#     print(ala)
