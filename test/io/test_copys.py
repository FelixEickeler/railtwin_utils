# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import laspy
import numpy as np
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

    csf_header = Header(
        offset=xyz(1.0, 2.0, 3.0),
        scale=xyz(0.1, 0.1, 0.1),
        x_range=min_max(0.0, 10.0),
        y_range=min_max(0.0, 10.0),
        z_range=min_max(0.0, 10.0),
        dimensions=['X', 'Y', 'Z'],
        record_length=1000,
        source='source_id',
        project='project_id',
        creation_date=date(2023, 1, 1),
        version='1.2'
    )
    frame = csf.Frame.from_dict(data)
    frame.metadata.update(csf_header.to_dict())

    las_header = laspy.LasHeader(point_format=3, version="1.2")
    las_header.offset = [1.0, 2.0, 3.0]
    las_header.scale = [0.1, 0.1, 0.1]
    las_header.x_range = [0.0, 10.0]
    las_header.y_range = [0.0, 10.0]
    las_header.z_range = [0.0, 10.0]
    las_header.point_count = 3
    las_header.file_source_id = 'source_id'
    las_header.uuid = 'project_id'
    las_header.creation_date = date(2023, 1, 1)

    las = laspy.LasData(las_header)
    las.X = data['X']
    las.Y = data['Y']
    las.Z = data['Z']

    return frame, las


def test_from_las_to_csf(frame_las_pair):
    frame, las = frame_las_pair
    from src.io.patches.shared import _from_las_to_csf
    csf_frame = _from_las_to_csf(las)

    assert isinstance(csf_frame, csf.Frame)
    assert csf_frame.metadata['offset'] == {'X': 1.0, 'Y': 2.0, 'Z': 3.0}
    assert csf_frame.metadata['scale'] == {'X': 0.1, 'Y': 0.1, 'Z': 0.1}
    assert csf_frame.metadata['x_range'] == {'mix': 0.0, 'max': 10.0}
    assert csf_frame.metadata['y_range'] == {'mix': 0.0, 'max': 10.0}
    assert csf_frame.metadata['z_range'] == {'mix': 0.0, 'max': 10.0}
    assert csf_frame.metadata['dimensions'] == ['X', 'Y', 'Z']
    assert csf_frame.metadata['record_length'] == 1000
    assert csf_frame.metadata['source'] == 'source_id'
    assert csf_frame.metadata['project'] == 'project_id'
    assert csf_frame.metadata['creation_date'] == '2023-01-01'
    assert csf_frame.metadata['version'] == '1.2'

    assert np.array_equal(csf_frame['X'].values, np.array([1.0, 4.0, 7.0]))
    assert np.array_equal(csf_frame['Y'].values, np.array([2.0, 5.0, 8.0]))
    assert np.array_equal(csf_frame['Z'].values, np.array([3.0, 6.0, 9.0]))


def test_from_csf_to_las(mock_custom_frame):
    from src.io.patches.shared import _from_csf_to_las
    las_record = _from_csf_to_las(mock_custom_frame)

    assert las_record['X'] == mock_custom_frame['X']
    assert las_record['Y'] == mock_custom_frame['Y']
    assert las_record['Z'] == mock_custom_frame['Z']
    assert len(las_record['X']) == 3