# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#
import laspy
import numpy as np
import pandas
import pandas as pd
import pytest
from datetime import date
import json
from src.io.formats.header import Header, xyz, min_max  # Adjust the import as necessary
from src.io.patches.patch_static_frame import custom_static_frame as csf


@pytest.fixture
def frame_las_pair():
    data = {
        'X': np.array([1.0, 4.0, 7.0]),
        'Y': np.array([2.0, 5.0, 8.0]),
        'Z': np.array([3.0, 6.0, 9.0])
    }

    frame = pd.DataFrame(data)
    frame.attrs["metadata"] = {
        "offset": xyz(1.0, 2.0, 3.0),
        "scale": xyz(0.1, 0.1, 0.1),
        "x_range": min_max(0.0, 10.0),
        "y_range": min_max(0.0, 10.0),
        "z_range": min_max(0.0, 10.0),
        "dimensions": ["X", "Y", "Z"],
        "record_length": 1000,
        "source": "source_id",
        "project": "project_id",
        "creation_date": date(2023, 1, 1),
        "version": "1.2"
    }

    las_header = laspy.LasHeader(point_format=3, version="1.2")
    las_header.offset = [1.0, 2.0, 3.0]
    las_header.scale = [0.1, 0.1, 0.1]
    las_header.x_min = 0.0
    las_header.y_min = 0.0
    las_header.z_min = 0.0
    las_header.x_max = 10.0
    las_header.y_max = 10.0
    las_header.z_max = 10.0

    las_header.point_count = 3
    las_header.file_source_id = 'source_id'
    las_header.uuid = 'project_id'
    las_header.creation_date = date(2023, 1, 1)

    las = laspy.LasData(las_header)
    las.X = data['X']
    las.Y = data['Y']
    las.Z = data['Z']

    return frame, las


def test_from_las_to_pandas(frame_las_pair):
    frame, las = frame_las_pair
    from src.io.patches.shared import _from_las_to_pandas
    frame = _from_las_to_pandas(las)

    assert isinstance(frame, pandas.DataFrame)
    assert frame.attrs["metadata"]['offset'] == xyz(1.0, 2.0, 3.0)
    assert frame.attrs["metadata"]['scale'] == xyz(0.1, 0.1, 0.1)
    assert frame.attrs["metadata"]['x_range'] == min_max(0.0, 10.0)
    assert frame.attrs["metadata"]['y_range'] == min_max(0.0, 10.0)
    assert frame.attrs["metadata"]['z_range'] == min_max(0.0, 10.0)
    assert all(i in frame.attrs["metadata"]['dimensions'] for i in ['X', 'Y', 'Z'])
    assert frame.attrs["metadata"]['record_length'] == 3
    assert frame.attrs["metadata"]['source'] == 'source_id'
    assert frame.attrs["metadata"]['project'] == 'project_id'
    assert frame.attrs["metadata"]['creation_date'] == date(2023, 1, 1)
    assert frame.attrs["metadata"]['version'] == '1.2'
    #
    # assert np.array_equal(csf_frame['X'].values, np.array([1.0, 4.0, 7.0]))
    # assert np.array_equal(csf_frame['Y'].values, np.array([2.0, 5.0, 8.0]))
    # assert np.array_equal(csf_frame['Z'].values, np.array([3.0, 6.0, 9.0]))


def test_from_pandas_to_las(frame_las_pair):
    frame, las = frame_las_pair
    from src.io.patches.shared import _from_pandas_to_las
    lasdata = _from_pandas_to_las(frame)

    header = lasdata.header

    assert header.offset[0] == 1.0
    assert header.offset[1] == 2.0
    assert header.offset[2] == 3.0
    assert header.scale[0] == 0.1
    assert header.scale[1] == 0.1
    assert header.scale[2] == 0.1
    assert header.x_min == 0.0
    assert header.y_min == 0.0
    assert header.z_min == 0.0
    assert header.x_max == 10.0
    assert header.y_max == 10.0
    assert header.z_max == 10.0
    assert header.point_count == 3
    assert header.file_source_id == 'source_id'
    assert header.uuid == 'project_id'
    assert header.creation_date == date(2023, 1, 1)

