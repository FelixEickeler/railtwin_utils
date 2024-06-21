# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#
import json
from datetime import date

import laspy
import numpy as np

from src.model.header import Header, xyz, min_max


def test_header_from_laspy():
    header = laspy.LasHeader(point_format=3, version="1.3")
    header.add_extra_dim(laspy.ExtraBytesParams(name="random", type=np.int32))
    header.offsets = np.array([1, 2, 3])
    header.scales = np.array([0.1, 0.1, 0.1])

    header = Header.from_laspy_header(header)
    assert header.version == "1.3"
    assert all([a == b for a, b in zip(header.offset, [1, 2, 3])])
    assert all([a == b for a, b in zip(header.scale, [0.1, 0.1, 0.1])])
    assert all([b in header.dimensions for b in ["X", "Y", "Z", "random"]])


def test_to_json():
    header = Header(
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

    json_str = header.to_json()
    data = json.loads(json_str)

    assert data['offset'] == {'X': 1.0, 'Y': 2.0, 'Z': 3.0}
    assert data['scale'] == {'X': 0.1, 'Y': 0.1, 'Z': 0.1}
    assert data['x_range'] == {'mix': 0.0, 'max': 10.0}
    assert data['y_range'] == {'mix': 0.0, 'max': 10.0}
    assert data['z_range'] == {'mix': 0.0, 'max': 10.0}
    assert data['dimensions'] == ['X', 'Y', 'Z']
    assert data['record_length'] == 1000
    assert data['source'] == 'source_id'
    assert data['project'] == 'project_id'
    assert data['creation_date'] == '2023-01-01'
    assert data['version'] == '1.2'


def test_from_json():
    json_str = json.dumps({
        'offset': [1.0, 2.0, 3.0],
        'scale': [0.1, 0.1, 0.1],
        'x_range': [0.0, 10.0],
        'y_range': [0.0, 10.0],
        'z_range': [0.0, 10.0],
        'dimensions': ['X', 'Y', 'Z'],
        'record_length': 1000,
        'source': 'source_id',
        'project': 'project_id',
        'creation_date': '2023-01-01',
        'version': '1.2'
    })

    header = Header(
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

    loaded_header = header.from_json(json_str)

    assert loaded_header == header
