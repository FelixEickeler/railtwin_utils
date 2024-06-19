# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import json
from dataclasses import dataclass, asdict
from collections import namedtuple
from typing import List
from datetime import date

min_max = namedtuple('expansion', 'mix max')
xyz = namedtuple('offset', 'X Y Z')


@dataclass
class Header:
    offset: xyz
    scale: xyz
    x_range: min_max
    y_range: min_max
    z_range: min_max
    dimensions: List[str]
    record_length: int
    source: str
    project: str
    creation_date: date
    version: str

    @classmethod
    def from_laspy_header(cls, header):
        offset = xyz(header.offset[0], header.offset[1], header.offset[2])
        scale = xyz(header.scale[0], header.scale[1], header.scale[2])
        x_range = min_max(header.x_min, header.x_max)
        y_range = min_max(header.y_min, header.y_max)
        z_range = min_max(header.z_min, header.z_max)
        dimensions = list(header.point_format.dimension_names)
        record_length = header.point_count
        source = header.file_source_id
        project = header.uuid
        creation_date = header.creation_date
        version = f"{header.major_version}.{header.minor_version}"
        return cls(offset, scale, x_range, y_range, z_range, dimensions, record_length, source, project, creation_date, version)

    def to_dict(self):
        return asdict(self)

    def from_json(self, json_str):
        data = json.loads(json_str)
        data['offset'] = xyz(*data['offset'])
        data['scale'] = xyz(*data['scale'])
        data['x_range'] = min_max(*data['x_range'])
        data['y_range'] = min_max(*data['y_range'])
        data['z_range'] = min_max(*data['z_range'])
        data['creation_date'] = date.fromisoformat(data['creation_date'])
        return self.__class__(**data)

    def to_json(self):
        data_dict = asdict(self)
        data_dict['offset'] = self.offset._asdict()
        data_dict['scale'] = self.scale._asdict()
        data_dict['x_range'] = self.x_range._asdict()
        data_dict['y_range'] = self.y_range._asdict()
        data_dict['z_range'] = self.z_range._asdict()
        data_dict['creation_date'] = self.creation_date.isoformat()
        return json.dumps(data_dict)