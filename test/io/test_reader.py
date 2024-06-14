# 11/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import laspy
from laspy.point.dims import PointFormatDict, _build_point_formats_dtypes, POINT_FORMAT_DIMENSIONS, DIMENSIONS_TO_TYPE

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

    print(laspy.point.format.supported_point_formats())
    pass


def test_read_tmc_traj():
    tmc_format = TmcTrajectory()
    csv_reader = create_csv_reader(tmc_format, row_skip=1, delimiter=r",")
    result = csv_reader(tmc_traj_100)


def test_laspy_we():
    from laspy import PointFormat, PackedPointRecord
    packed_point_record = PackedPointRecord.zeros(10, PointFormat(0))
    ala = PackedPointRecord.from_point_record(packed_point_record, XYZIRGB)
    print(ala)
